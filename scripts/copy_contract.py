"""Source-copy extraction and coverage checks; creative suitability is reviewed by the agent."""
import argparse,hashlib,json,re,unicodedata
from pathlib import Path
from openpyxl.utils.cell import coordinate_from_string,column_index_from_string,get_column_letter

KINDS={
 'headline':'headline','title':'headline','heading':'headline','主标题':'headline','标题':'headline',
 'subheadline':'subheadline','subtitle':'subheadline','副标题':'subheadline','小标题':'subheadline',
 'copy':'copy','body':'copy','bodycopy':'copy','description':'copy','正文':'copy','文案':'copy','描述':'copy',
 'tagline':'tagline','slogan':'tagline','口号':'tagline',
 'bullet':'bullet','bullets':'bullet','sellingpoints':'bullet','卖点':'bullet'}
def value(cell):
 v=cell.get('value')
 if isinstance(v,str) and v.startswith('='):v=cell.get('cached_value')
 return str(v).strip() if v is not None else ''
def section(text):
 m=re.match(r'^\s*(?:section|模块)\s*([0-9]+)\b',str(text),re.I)
 # Section1Headline also occurs as a compact field key.
 if not m:m=re.match(r'^\s*(?:section|模块)\s*([0-9]+)',str(text),re.I)
 return m.group(1) if m else None
def kind(text):
 s=re.sub(r'^\s*(?:section|模块)\s*[0-9]+\s*','',str(text),flags=re.I)
 return KINDS.get(re.sub(r'[\s_:/：-]+','',s).casefold())
def extract_candidates(attributes):
 result=[];seen=set()
 for sheet,table in attributes.items():
  rows={}
  for c in table['cells']:
   col,row=coordinate_from_string(c['cell']);rows.setdefault(row,{})[column_index_from_string(col)]=c
  current=None;header={};table_active=False
  def add(c,typ,label):
   txt=value(c)
   if not txt:return
   sid=sheet+'!'+c['cell']
   if sid in seen:return
   seen.add(sid);result.append(dict(id=sid,sheet=sheet,cell=c['cell'],section=current,kind=typ,label=label,text=txt))
  for row,cells in sorted(rows.items()):
   texts={col:value(c) for col,c in cells.items()}
   sec=next((section(t) for t in texts.values() if section(t)),None)
   if sec is not None:current=sec;table_active=True
   labels={col:kind(t) for col,t in texts.items() if kind(t)}
   # Horizontal column headings, not copy values.
   if len(labels)>1 and all(t.strip().casefold() in KINDS for col,t in texts.items() if col in labels):
    header=labels;table_active=False;continue
   explicit=False
   for col,typ in labels.items():
    label=texts[col];next_col=col+1
    candidate=cells.get(next_col,dict(cell=get_column_letter(next_col)+str(row),value=None))
    if kind(value(candidate)):continue
    add(candidate,typ,label);explicit=True
   if not explicit and header and table_active:
    # Non-section row labels (e.g. 尺码表) begin another table, not continuation copy.
    if sec is None and texts.get(1):table_active=False;continue
    for col,typ in header.items():
     if col in cells:add(cells[col],typ,texts.get(1) or 'section '+str(current))
 return result
def normal(text):
 # Preserve words/punctuation; typography may change case or wrap at arbitrary boundaries.
 return re.sub(r'\s+','',unicodedata.normalize('NFKC',str(text))).casefold()
def text_index(layout):
 found={}
 def walk(nodes,module,visible=True):
  for node in nodes:
   show=visible and node.get('opacity',100)>0
   if node['type']=='group':walk(node['layers'],module,show)
   elif node['type']=='text':
    name=node['name'];qualified=name if name.startswith(module+' / ') else module+' / '+name
    found[qualified]=dict(text=node['text'],visible=show,module=module)
 for mod in layout['modules']:walk(mod['layers'],mod['name'])
 return found
def validate_copy(ws,layout,native_texts=None,require_psd=False):
 ws=Path(ws);issues=[];counts=dict(adopt=0,adapt=0,exclude=0)
 def fail(msg):issues.append('Copy: '+msg)
 if (ws/'manifest.json').is_file():
  manifest=json.loads((ws/'manifest.json').read_text(encoding='utf-8-sig'));expected=manifest.get('attribute_workbook_sha256')
  if expected:
   original=Path(manifest['attribute_workbook'])
   if not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest()!=expected:
    fail('attribute workbook changed/unavailable since intake; reread and review the source copy')
 if not (ws/'attributes.json').is_file():return ['Copy: attribute intake missing'],counts
 attrs=json.loads((ws/'attributes.json').read_text(encoding='utf-8-sig'))
 if any(t.get('reader')!='read_only_full_xml_cells' for t in attrs.values()):
  fail('refresh legacy attribute intake using workspace.attributes; merged XML cells were not preserved')
 required={c['id']:c for c in extract_candidates(attrs)}
 p=ws/'copy_plan.json'
 if not p.is_file():return issues+['Copy: copy_plan.json missing; source copy must be reviewed before layout'],counts
 plan=json.loads(p.read_text(encoding='utf-8-sig'))
 if plan.get('reviewed') is not True:fail('source-copy suitability and module mapping not reviewed')
 entries=plan.get('entries',[]);mapped={}
 grid={sheet+'!'+c['cell']:value(c) for sheet,t in attrs.items() for c in t['cells']}
 for entry in entries:
  sid=entry.get('id')
  if not sid or sid in mapped:fail('missing/duplicate source ID '+str(sid));continue
  mapped[sid]=entry
  if sid not in grid or not grid[sid]:fail('source cell missing/blank '+sid)
 # Additional semantically selected copy cells are allowed; every detected field still needs a decision.
 for sid in required:
  if sid not in mapped:fail('unaccounted source field '+sid)
 layers=text_index(layout);actual={t['name']:t for t in (native_texts or [])}
 if require_psd and not native_texts and layers:fail('saved PSD actual text snapshot missing')
 for sid,entry in mapped.items():
  decision=entry.get('decision');reason=entry.get('reason','').strip();code=entry.get('reason_code')
  if decision=='exclude':
   counts['exclude']+=1
   if code not in {'product_mismatch','not_product_supported','out_of_scope','user_override'} or not reason:
    fail('exclusion needs a specific suitability/scope reason '+sid)
   if not entry.get('evidence'):fail('exclusion evidence/user instruction missing '+sid)
   continue
  if decision not in {'adopt','adapt'}:fail('unresolved source field '+sid);continue
  counts[decision]+=1
  if decision=='adapt':
   if code not in {'typo','shorten','translate','product_correction','user_override'} or not reason:
    fail('revision reason missing '+sid)
   if not entry.get('evidence'):fail('revision evidence/mapping explanation missing '+sid)
  placements=entry.get('placements',[])
  if not placements:fail('no target text layer '+sid);continue
  chunks=[]
  for placement in placements:
   mod=placement.get('module','');name=placement.get('layer','')
   qualified=name if name.startswith(mod+' / ') else mod+' / '+name
   expected=placement.get('text')
   layer=layers.get(qualified)
   if not layer or layer['module']!=mod:fail('wrong/missing module-layer target '+sid+' -> '+qualified);continue
   if not layer['visible']:fail('source text hidden in layout '+qualified)
   if not isinstance(expected,str) or not expected.strip():fail('placement text not specified '+sid);continue
   if normal(layer['text'])!=normal(expected):fail('layout text differs from mapped copy '+qualified)
   chunks.append(expected)
   if require_psd:
    saved=actual.get(qualified)
    if not saved or normal(saved.get('text',''))!=normal(expected):fail('saved PSD text differs/missing '+qualified)
    elif not saved.get('visible') or saved.get('opacity',0)<=0:fail('saved PSD text hidden '+qualified)
  if decision=='adopt' and normal(''.join(chunks))!=normal(grid.get(sid,'')):
   fail('adopted copy was omitted/replaced/reordered '+sid+'; preserve it or document a necessary revision')
 return issues,counts
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--attributes',required=True);p.add_argument('--output');a=p.parse_args()
 data=extract_candidates(json.loads(Path(a.attributes).read_text(encoding='utf-8-sig')))
 if a.output:Path(a.output).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 else:print(json.dumps(data,ensure_ascii=False,indent=2))


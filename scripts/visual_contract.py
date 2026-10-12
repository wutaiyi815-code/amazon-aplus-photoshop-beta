"""Deterministic background constraints; visual proportions still require human review."""
from pathlib import Path
import hashlib,json
BACKGROUND={'background_texture','background_campaign'}
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def visible_nodes(nodes,opacity=100):
 out=[]
 for n in nodes:
  op=opacity*n.get('opacity',100)/100
  if op<=0:continue
  if n['type']=='group':out.extend(visible_nodes(n['layers'],op))
  else:out.append(n)
 return out
def validate_visual(ws,layout,require_review=False):
 ws=Path(ws);issues=[];evidence={};groups=[];qualified=0;width=layout.get('width',1464)
 def fail(msg):issues.append('Visual: '+msg)
 for mod in layout['modules']:
  nodes=visible_nodes(mod['layers']);backgrounds=[]
  for n in nodes:
   role=n.get('design_role')
   if n['type']=='image':
    box=n.get('box',[])
    if len(box)==4 and box[2]==width and box[3]==mod['height'] and role not in BACKGROUND:
     fail(mod['name']+': classify full-module image background using design_role')
   if role not in BACKGROUND:continue
   if n['type']!='image':fail(mod['name']+': background texture/campaign must be an image');continue
   source=n.get('background_source_id','')
   if not isinstance(source,str) or not source.strip():fail(mod['name']+': stable background_source_id missing')
   p=(ws/n['file']).resolve()
   if not p.is_file():fail(mod['name']+': selected background file missing');continue
   sha=digest(p);evidence[str(p)]=sha;backgrounds.append((source,sha))
   if role=='background_texture':qualified+=1
   elif any(other is not n and other['type']=='image' and other.get('design_role') not in BACKGROUND and other.get('role') in {'photo','product','detail'} for other in nodes):
    qualified+=1
  if backgrounds and any(n.get('design_role')=='decorative_large_pale_type' for n in nodes):
   fail(mod['name']+': texture/campaign background conflicts with oversized decorative background type')
  groups.append(backgrounds)
 for index in range(1,len(groups)):
  if any((a[0] and a[0]==b[0]) or a[1]==b[1] for a in groups[index-1] for b in groups[index]):
   fail(layout['modules'][index]['name']+': adjacent modules reuse the same background source or file content')
 if len(layout['modules'])>3 and not qualified:
  fail('more than three modules require a visible texture or campaign background with other photo/product overlays')
 if require_review:
  p=ws/'checks/visual_balance.json'
  if not p.is_file():fail('visual_balance.json inspection missing')
  else:
   review=json.loads(p.read_text(encoding='utf-8-sig'));evidence[str(p)]=digest(p)
   if review.get('status')!='passed' or not review.get('notes'):fail('visual balance inspection not completed')
   for key in ['subject_scale','rule1_visible','decoration_restraint','adjacent_backgrounds']:
    if review.get('checks',{}).get(key) is not True:fail('actual export inspection missing: '+key)
   refs=review.get('reference_files',[])
   if not refs:fail('selected scale/design reference files missing')
   for raw in refs:
    ref=Path(raw)
    if not ref.is_absolute():ref=ws/ref
    if not ref.is_file():fail('visual reference file unavailable: '+str(ref))
    else:evidence[str(ref.resolve())]=digest(ref)
 return issues,evidence


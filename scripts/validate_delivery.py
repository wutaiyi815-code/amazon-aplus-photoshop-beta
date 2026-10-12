"""Evidence gate for PSD A+, with user-resolved cast and module counts."""
from pathlib import Path
import argparse,json,struct
from PIL import Image
from workspace import read,write,sha
from copy_contract import validate_copy
from visual_contract import validate_visual
CHECKS=('product_fidelity','scene_logic','visual_variety','typography_readability','layer_editability')
CREATOR={'creator','occasion','creator_occasion'}
def validate(ws):
 ws=Path(ws).resolve();m=read(ws/'manifest.json');problems=[];outputs=m.get('outputs',{});dims=m['canvas'];policy=m['model_policy']
 def fail(msg):problems.append(msg)
 def local(raw):return (ws/raw).resolve() if raw else None
 if not m.get('criteria_read'):fail('Current reference document/cases have not been marked as read')
 if not m.get('product_lock'):fail('Missing product lock')
 models=m.get('model_identities',[]);groups={g:[x for x in models if x.get('group')==g] for g in ['A','B']}
 key=lambda x:x.get('identity_id') or x.get('identity_name') or x.get('id')
 for g in ['A','B']:
  keys=[key(x) for x in groups[g]]
  if len(keys)!=policy[g+'_count'] or len(set(keys))!=len(keys) or any(not x for x in keys):fail('Cast count/unique identity mismatch in group '+g)
  if any(not x.get('eagle_id') and not x.get('user_specified') for x in groups[g]):fail('Unverified Eagle/user identity in group '+g)
 if policy.get('disjoint',True) and ({key(x) for x in groups['A']} & {key(x) for x in groups['B']}):fail('A/B model identities overlap')
 for name,job in m.get('jobs',{}).items():
  if job.get('required',True):
   if job.get('status')!='completed':fail('Required generation job is not completed: '+name)
   elif not local(job.get('result')) or not local(job['result']).is_file():fail('Completed generation result is missing: '+name)
 all_ids={x.get('id') for x in models}
 refs=[r for j in m.get('jobs',{}).values() for r in j.get('references',[])]
 scenes={s['id']:s for s in m.get('scene_research',[]) if s.get('selected')}
 main_scene_ids={sid for mod in m['modules'] if mod.get('kind') not in CREATOR for sid in mod.get('scene_ids',[])}
 main_settings={scenes[sid].get('setting_id',sid) for sid in main_scene_ids if sid in scenes}
 main_files={sha(local(scenes[sid]['file'])) for sid in main_scene_ids if sid in scenes and local(scenes[sid].get('file')) and local(scenes[sid]['file']).is_file()}
 for mod in m['modules']:
  n=mod['name'];q=mod.get('qc',{})
  for check in CHECKS:
   if q.get(check) is not True:fail(n+': '+check+' not passed by inspection')
  if not mod.get('source_ids'):fail(n+': source IDs missing')
  people=mod.get('people',0);assets=mod.get('people_assets',[])
  used={i for a in assets for i in a.get('person_ids',[])}
  group='B' if mod.get('kind') in CREATOR else 'A';allowed={x.get('id') for x in groups[group]}
  if people and (not used or not used.issubset(allowed) or any(not local(a.get('file')) or not local(a['file']).is_file() for a in assets)):fail(n+': model/photo ownership missing or wrong')
  if mod.get('kind')=='campaign':
   if not any(len(a.get('person_ids',[]))==people for a in assets) or q.get('interaction') is not True:fail(n+': campaign people/interaction evidence failed')
  if mod.get('kind') in CREATOR and policy.get('creator_solo_each',True):
   solo=[a for a in assets if len(a.get('person_ids',[]))==1]
   if len(solo)!=people or len(used)!=people or len({a.get('file') for a in solo})!=people:fail(n+': expected distinct single-person assets')
  if mod.get('kind') in {'campaign',*CREATOR} or mod.get('needs_scene'):
   if not mod.get('scene_ids'):fail(n+': selected scene missing')
   for sid in mod.get('scene_ids',[]):
    s=scenes.get(sid);p=local(s.get('file')) if s else None
    if not s or not p or not p.is_file() or not (s.get('source_url') or s.get('eagle_id') or s.get('user_supplied')):fail(n+': actual scene source missing '+sid);continue
    if mod.get('kind') in CREATOR and (s.get('setting_id',sid) in main_settings or sha(p) in main_files):fail(n+': creator scene repeats a main-module setting/source')
    if n not in s.get('used_in',[]):fail(n+': scene not assigned to module '+sid)
    if not any(sid in r.get('source_ids',[]) or (r.get('file') and local(r['file'])==p and 'scene' in r.get('role','')) for r in refs):fail(n+': scene not actually recorded as generation input '+sid)
  if mod.get('kind')=='styling':
   products=m.get('pairing_products',[])
   methods={'official_flatlay','official_stilllife','source_flatlay','generated_independent_flatlay'}
   if not products or any(x.get('method') not in methods or not (x.get('source_url') or x.get('source_path')) or not local(x.get('file')) or not local(x['file']).is_file() for x in products):fail(n+': independent real-product flatlay evidence missing')
 edits=read(ws/'checks/editability.json') if (ws/'checks/editability.json').exists() else {}
 structure=read(ws/'checks/structure.json') if (ws/'checks/structure.json').exists() else {}
 resolved=ws/'checks/resolved_layout.json'
 if not resolved.is_file():copy_issues,copy_counts=['Copy: resolved layout missing'],{}
 else:copy_issues,copy_counts=validate_copy(ws,read(resolved),edits.get('native_texts'),require_psd=True)
 problems.extend(copy_issues)
 if resolved.is_file():visual_issues,visual_hashes=validate_visual(ws,read(resolved),require_review=True)
 else:visual_issues,visual_hashes=['Visual: resolved layout missing'],{}
 problems.extend(visual_issues)
 if edits.get('status')!='verified' or edits.get('final_unchanged') is not True:fail('PSD reopen/edit test not verified')
 if len(edits.get('text_edits',[]))!=structure.get('counts',{}).get('text'):fail('Native text edit coverage mismatch')
 if not edits.get('photo_replace') and structure.get('roles',{}).get('photos'):fail('Photo replacement test missing')
 if any(x.get('kind') in {'fit_detail','detail'} for x in m['modules']) and not structure.get('roles',{}).get('icons'):fail('Informational icons missing')
 if structure.get('roles',{}).get('icons') and not (edits.get('icon_recolor') and edits.get('icon_replace')):fail('Icon edit test missing')
 if structure.get('width')!=dims['width'] or structure.get('height')!=dims['height'] or structure.get('module_groups')!=len(m['modules']):fail('PSD structure dimensions/module mismatch')
 psd=local(outputs.get('psd'))
 if not psd or not psd.is_file():fail('PSD missing')
 else:
  with psd.open('rb') as f:head=f.read(26)
  if head[:4]!=b'8BPS' or len(head)<26 or struct.unpack('>II',head[14:22])!=(dims['height'],dims['width']):fail('Actual PSD header dimensions invalid')
 for i,mod in enumerate(m['modules'],1):
  p=local(outputs.get('module_'+str(i)))
  if not p or not p.is_file():fail('Module PNG missing '+mod['name']);continue
  with Image.open(p) as im:
   if im.size!=(dims['width'],mod['height']):fail('Actual PNG dimensions invalid '+mod['name'])
 p=local(outputs.get('long_png'))
 if not p or not p.is_file():fail('Long PNG missing')
 else:
  with Image.open(p) as im:
   if im.size!=(dims['width'],dims['height']):fail('Long PNG dimensions invalid')
 if not local(outputs.get('preview')) or not local(outputs['preview']).is_file():fail('Preview missing')
 hashes={str(p):sha(p) for p in [local(v) for v in outputs.values()] if p and p.is_file()}
 copy_hashes={str(ws/f):sha(ws/f) for f in ['attributes.json','copy_plan.json','checks/resolved_layout.json','checks/editability.json'] if (ws/f).is_file()}
 copy_hashes.update(visual_hashes)
 report={'status':'failed' if problems else 'passed','problems':problems,'artifact_sha256':hashes,'copy_evidence_sha256':copy_hashes,'copy_counts':copy_counts,'module_count':len(m['modules']),'model_count':len(models)}
 write(ws/'checks/validation.json',report);return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);a=p.parse_args();r=validate(a.workspace);print(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(0 if r['status']=='passed' else 1)

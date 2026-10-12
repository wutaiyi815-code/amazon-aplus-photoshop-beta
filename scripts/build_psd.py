"""Compile an agent-authored layout into guarded Photoshop Beta JSX; no fixed design."""
from pathlib import Path
import argparse,json,re
from workspace import read,write,load_workspace
from copy_contract import validate_copy
from visual_contract import validate_visual

SKILL=Path(__file__).resolve().parents[1]
def normalize(nodes,ws,prefix,roles,seen,planned):
 for n in nodes:
  n['name']=prefix+' / '+n['name']
  if n['name'] in seen:raise ValueError('Duplicate layer name '+n['name'])
  seen.add(n['name']);kind=n['type']
  if kind=='group':normalize(n['layers'],ws,prefix,roles,seen,planned)
  elif kind=='image':
   f=(ws/n['file']).resolve()
   if not f.is_file() and f not in planned:raise ValueError('Missing asset '+str(f))
   if not f.is_relative_to(ws):raise ValueError('Copy selected sources into this SKU workspace before layout: '+str(f))
   n['file']=str(f).replace('\\','/')
   if n.get('fit','cover') not in {'cover','contain','stretch'}:raise ValueError('Unknown image fit')
   if n.get('role')=='icon':roles['icons'].append(n['name'])
   if n.get('role') in {'photo','product','detail'}:roles['photos'].append(n['name'])
  elif kind=='text':
   if not n.get('text'):raise ValueError('Empty text layer')
   roles['texts'].append(n['name']);roles['fonts'].add(n.get('font','Arial-BoldMT' if n.get('bold') else 'ArialMT'))
  elif kind=='shape':
   if n.get('purpose') not in {'background','rule'}:raise ValueError('Native shapes are for backgrounds/rules; use real material assets for decorative icons/frames')
  else:raise ValueError('Unknown layer type '+kind)
  if kind in {'shape','image'} and (len(n['box'])!=4 or n['box'][2]<=0 or n['box'][3]<=0):raise ValueError('Invalid layer box')
  if n.get('blend') not in {None,'NORMAL','MULTIPLY','SCREEN','OVERLAY','SOFTLIGHT','COLOR','LUMINOSITY'}:raise ValueError('Unsupported blend')

def compile_layout(ws,layout_path,probe_path=None):
 ws=Path(ws).resolve();_,manifest=load_workspace(ws);cfg=read(layout_path);probe=read(probe_path or ws/'checks/beta_probe.json')
 if probe.get('status')!='verified' or not re.fullmatch(r'photoshop-[\w.-]+',probe.get('specifier','')):raise ValueError('A verified Beta probe is required')
 modules=cfg['modules'];width=cfg.get('width',manifest['canvas']['width']);height=sum(m['height'] for m in modules)
 if not isinstance(width,int) or width<=0 or width>30000 or not isinstance(height,int) or height<=0 or height>30000:raise ValueError('Canvas exceeds standard PSD dimensions or is invalid')
 if cfg.get('kind','aplus')=='aplus':
  if width!=manifest['canvas']['width']:raise ValueError('Layout width does not match the user-resolved contract')
  if [(x['name'],x['height']) for x in modules]!=[(x['name'],x['height']) for x in manifest['modules']]:raise ValueError('Layout does not match the user-resolved module contract')
  copy_issues,copy_counts=validate_copy(ws,cfg)
  write(ws/'checks/copy_layout_validation.json',{'status':'failed' if copy_issues else 'passed','problems':copy_issues,'counts':copy_counts})
  if copy_issues:raise ValueError('\n'.join(copy_issues))
  visual_issues,_=validate_visual(ws,cfg)
  write(ws/'checks/visual_layout_validation.json',{'status':'failed' if visual_issues else 'passed','problems':visual_issues})
  if visual_issues:raise ValueError('\n'.join(visual_issues))
 stem=cfg.get('output_stem','Aplus_Editable')
 if not re.fullmatch(r'[\w.-]+',stem):raise ValueError('Unsafe output stem')
 roles={'texts':[],'photos':[],'icons':[],'fonts':set()};seen=set()
 planned={(ws/j['output']).resolve() for j in cfg.get('crop_assets',[])}
 for mod in modules:normalize(mod['layers'],ws,mod['name'],roles,seen,planned)
 for job in cfg.get('crop_assets',[]):
  src=(ws/job['source']).resolve();dst=(ws/job['output']).resolve()
  if not src.is_file() or not src.is_relative_to(ws) or not dst.is_relative_to(ws):raise ValueError('Crop sources/outputs must be in this SKU workspace')
  dst.parent.mkdir(parents=True,exist_ok=True);job.update(source=str(src).replace('\\','/'),output=str(dst).replace('\\','/'))
 outputs={'psd':stem+'.psd','long_png':stem+'_Long.png','preview':stem+'_Preview.png'}
 for i,mod in enumerate(modules,1):outputs['module_'+str(i)]=f'Module_{i}_{width}x{mod["height"]}.png'
 cfg.update(workspace=str(ws).replace('\\','/'),height=height,width=width,outputs=outputs,fonts=sorted(roles.pop('fonts')),roles=roles)
 write(ws/'checks/resolved_layout.json',cfg)
 assets='\n'.join((SKILL/'assets'/f).read_text(encoding='utf-8') for f in ['json_writer.jsx','photoshop_helpers.jsx','render_layout.jsx'])
 header='#target '+probe['specifier']+'\nvar CFG='+json.dumps(cfg,ensure_ascii=False)+';\nvar W=CFG.workspace,A=W+"/assets/",EXPECTED_BETA_ROOT='+json.dumps(probe['app_path'].replace('\\','/'))+';\n'
 body=r'''
var status={status:'running',outputs:CFG.outputs};
try{
 if(new Folder(app.path).fsName.toLowerCase()!==new Folder(EXPECTED_BETA_ROOT).fsName.toLowerCase())throw Error('Wrong Photoshop installation; no documents changed');
 writeJSON(W+'/checks/build_status.json',status);
 for(var k=0;k<CFG.fonts.length;k++){var present=false;for(var j=0;j<app.fonts.length;j++)if(app.fonts[j].postScriptName===CFG.fonts[k])present=true;if(!present)throw Error('Font missing: '+CFG.fonts[k]);}
 for(var k=0;k<(CFG.crop_assets||[]).length;k++){var c=CFG.crop_assets[k],already=false;for(var u=0;u<app.documents.length;u++){try{if(app.documents[u].fullName.fsName===new File(c.source).fsName)already=true;}catch(ignore){}}var original=app.open(new File(c.source)),s=original.duplicate('Source crop — owned copy',false);s.crop(c.bounds);s.saveAs(new File(c.output),new PNGSaveOptions(),true,Extension.LOWERCASE);s.close(SaveOptions.DONOTSAVECHANGES);if(!already)original.close(SaveOptions.DONOTSAVECHANGES);}
 D=app.documents.add(CFG.width,CFG.height,72,CFG.output_stem||'Editable Aplus',NewDocumentMode.RGB,DocumentFill.WHITE);
 D.convertProfile('sRGB IEC61966-2.1',Intent.RELATIVECOLORIMETRIC,true,true);
 var y=0;
 for(var k=0;k<CFG.modules.length;k++){var mod=CFG.modules[k];group((k+1)+' / '+mod.name+' | '+CFG.width+' x '+mod.height);nodes(mod.layers,0,y);y+=mod.height;if(k<CFG.modules.length-1)D.guides.add(Direction.HORIZONTAL,UnitValue(y,'px'));status.last_module=mod.name;writeJSON(W+'/checks/build_status.json',status);}
 var o=new PhotoshopSaveOptions();o.layers=true;o.embedColorProfile=true;D.saveAs(new File(W+'/'+CFG.outputs.psd),o,true,Extension.LOWERCASE);
 var e=D.duplicate('PNG export',true);png(e,W+'/'+CFG.outputs.long_png);e.resizeImage(UnitValue(Math.min(732,CFG.width),'px'),null,null,ResampleMethod.BICUBICSHARPER);png(e,W+'/'+CFG.outputs.preview);e.close(SaveOptions.DONOTSAVECHANGES);
 y=0;for(var k=0;k<CFG.modules.length;k++){e=D.duplicate('Module export',true);e.crop([0,y,CFG.width,y+CFG.modules[k].height]);png(e,W+'/'+CFG.outputs['module_'+(k+1)]);e.close(SaveOptions.DONOTSAVECHANGES);y+=CFG.modules[k].height;}
 var counts={text:0,smartobjects:0};countLayers(D,counts);writeJSON(W+'/checks/structure.json',{version:app.version,app_path:app.path.fsName,width:CFG.width,height:CFG.height,module_groups:CFG.modules.length,counts:counts,roles:CFG.roles,outputs:CFG.outputs});
 status.status='completed';writeJSON(W+'/checks/build_status.json',status);
}catch(err){status.status='error';status.error=err.message;status.line=err.line;writeJSON(W+'/checks/build_status.json',status);}
'''
 out=ws/'scripts/build.jsx';out.write_text(header+assets+body,encoding='utf-8')
 verification=r'''
var report={status:'error',text_edits:[],native_texts:[],photo_replace:false,icon_recolor:false,icon_replace:false};
try{
 if(new Folder(app.path).fsName.toLowerCase()!==new Folder(EXPECTED_BETA_ROOT).fsName.toLowerCase())throw Error('Wrong Photoshop installation');
 var temporary=new File(W+'/checks/_verify_'+(new Date()).getTime()+'.psd');if(!new File(W+'/'+CFG.outputs.psd).copy(temporary))throw Error('Unable to copy saved PSD for reopen verification');var saved=app.open(temporary);D=saved.duplicate('Editable verification — DISCARD',false);app.activeDocument=D;
 for(var k=0;k<CFG.roles.texts.length;k++){var l=findLayer(D,CFG.roles.texts[k]);if(!l||l.kind!==LayerKind.TEXT)throw Error('Missing native text '+CFG.roles.texts[k]);var t=l.textItem.contents,visible=l.visible,parent=l.parent;while(parent&&parent.typename==='LayerSet'){visible=visible&&parent.visible&&parent.opacity>0;parent=parent.parent;}report.native_texts.push({name:l.name,text:t,visible:visible,opacity:l.opacity});l.textItem.contents=t+' EDIT';report.text_edits.push(CFG.roles.texts[k]);}
 if(CFG.roles.photos.length){D.activeLayer=findLayer(D,CFG.roles.photos[0]);if(D.activeLayer.kind!==LayerKind.SMARTOBJECT)throw Error('Photo not independent SO');var p=new ActionDescriptor();p.putPath(charIDToTypeID('null'),new File(CFG.verification_asset));executeAction(stringIDToTypeID('placedLayerReplaceContents'),p,DialogModes.NO);report.photo_replace=true;}
 if(CFG.roles.icons.length){var l=findLayer(D,CFG.roles.icons[0]);if(l.kind!==LayerKind.SMARTOBJECT)throw Error('Icon not independent SO');recolor(l,'9F3344');report.icon_recolor=true;D.activeLayer=l;var p=new ActionDescriptor();p.putPath(charIDToTypeID('null'),new File(CFG.verification_asset));executeAction(stringIDToTypeID('placedLayerReplaceContents'),p,DialogModes.NO);report.icon_replace=true;}
 D.close(SaveOptions.DONOTSAVECHANGES);saved.close(SaveOptions.DONOTSAVECHANGES);temporary.remove();report.status='verified';report.final_unchanged=true;writeJSON(W+'/checks/editability.json',report);
}catch(err){report.error=err.message;report.line=err.line;if(D&&D.name==='Editable verification — DISCARD')D.close(SaveOptions.DONOTSAVECHANGES);writeJSON(W+'/checks/editability.json',report);}
'''
 images=[]
 def collect(nodes):
  for n in nodes:
   if n['type']=='image':images.append(n['file'])
   if n['type']=='group':collect(n['layers'])
 for mod in modules:collect(mod['layers'])
 cfg['verification_asset']=images[-1] if images else ''
 (ws/'scripts/verify.jsx').write_text('#target '+probe['specifier']+'\nvar CFG='+json.dumps(cfg,ensure_ascii=False)+';\nvar W=CFG.workspace,A=W+"/assets/",EXPECTED_BETA_ROOT='+json.dumps(probe['app_path'].replace('\\','/'))+';\n'+assets+verification,encoding='utf-8')
 manifest.update(outputs=outputs,status='layout_ready',layout_file=str(Path(layout_path).resolve()));write(ws/'manifest.json',manifest);print(out)
 return cfg
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--layout',required=True);p.add_argument('--probe');a=p.parse_args();compile_layout(a.workspace,a.layout,a.probe)

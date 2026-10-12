"""Create a path-guarded probe; launch through launch_beta.ps1 and inspect its result."""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--beta-executable',default=r'C:\Program Files\Adobe\Adobe Photoshop (Beta)\Photoshop.exe');a=p.parse_args();ws=Path(a.workspace).resolve();exe=Path(a.beta_executable).resolve()
if not exe.is_file():raise ValueError('Beta executable not found')
if 'beta' not in str(exe.parent).lower():raise ValueError('Executable path does not identify a Beta installation; do not route to Photoshop2020 or stable Photoshop')
(ws/'checks').mkdir(parents=True,exist_ok=True);(ws/'scripts').mkdir(exist_ok=True)
code="""app.displayDialogs=DialogModes.NO;
var EXPECTED_BETA_ROOT=%s, OUT=%s;
var result={status:'error'};
try {
 if(new Folder(app.path).fsName.toLowerCase()!==new Folder(EXPECTED_BETA_ROOT).fsName.toLowerCase())throw Error('Script routed to another Photoshop installation; aborted');
 result={status:'verified',app_path:app.path.fsName,version:app.version,specifier:BridgeTalk.appSpecifier,fonts:[]};
 for(var i=0;i<app.fonts.length;i++)result.fonts.push(app.fonts[i].postScriptName);
} catch(e){result.error=e.message;}
var f=new File(OUT);f.encoding='UTF8';f.open('w');
function q(s){return '\"'+String(s).replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"').replace(/\\r/g,'\\\\r').replace(/\\n/g,'\\\\n')+'\"';}
var v='{';for(var k in result){if(v.length>1)v+=',';v+=q(k)+':';if(result[k] instanceof Array){var items=[];for(var j=0;j<result[k].length;j++)items.push(q(result[k][j]));v+='['+items.join(',')+']';}else v+=q(result[k]);}f.write(v+'}');f.close();
"""%(json.dumps(str(exe.parent).replace('\\','/'),ensure_ascii=False),json.dumps(str(ws/'checks/beta_probe.json').replace('\\','/'),ensure_ascii=False))
out=ws/'scripts/probe_beta.jsx';out.write_text(code,encoding='utf-8');print(out)

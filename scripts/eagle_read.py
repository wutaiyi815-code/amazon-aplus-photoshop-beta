"""Read-only fallback for the configured Eagle Streamable HTTP MCP route."""
from pathlib import Path
import argparse,json,os,tomllib,urllib.request,urllib.error,re
ALLOW={'get_app_info','folder_get','item_query','item_get','ai_search_status','ai_search_by_text','ai_search_by_item','tag_get'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',default=str(Path.home()/'.codex/config.toml'));p.add_argument('--server',default='eagle-mcp');p.add_argument('--call');p.add_argument('--out',required=True);a=p.parse_args()
 servers=tomllib.loads(Path(a.config).read_text(encoding='utf-8-sig')).get('mcp_servers',{})
 if a.server not in servers:raise RuntimeError('Eagle configuration missing')
 cfg=servers[a.server]
 if cfg.get('enabled',True) is False:raise RuntimeError('Eagle server disabled')
 url=cfg.get('url')
 if not url:raise RuntimeError('Route is not Streamable HTTP; use directly exposed tools')
 def expand(s):return re.sub(r'\$\{([^}]+)\}',lambda m:os.environ[m[1]],s)
 url=expand(url);headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 headers.update({k:expand(v) for k,v in cfg.get('http_headers',{}).items()})
 for k,v in cfg.get('env_http_headers',{}).items():headers[k]=os.environ[v]
 def request(method,params,notification=False):
  body={'jsonrpc':'2.0','method':method,'params':params}
  if not notification:body['id']=1
  try:
   with urllib.request.urlopen(urllib.request.Request(url,json.dumps(body).encode(),headers=headers),timeout=25) as r:
    raw=r.read().decode();sid=r.headers.get('Mcp-Session-Id')
    if sid:headers['Mcp-Session-Id']=sid
  except urllib.error.HTTPError as e:raise RuntimeError('Eagle MCP HTTP status '+str(e.code)) from None
  except urllib.error.URLError:raise RuntimeError('Eagle MCP connection/handshake failed') from None
  if not raw.strip():return {}
  try:return json.loads(raw)
  except json.JSONDecodeError:
   events=[json.loads(line[5:].strip()) for line in raw.splitlines() if line.startswith('data:')]
   return next((x for x in events if 'result' in x or 'error' in x),{})
 request('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'aplus-psd','version':'1.0'}})
 request('notifications/initialized',{},True)
 catalog=request('tools/list',{});names={x['name'] for x in catalog.get('result',{}).get('tools',[])}
 if a.call:
  call=json.loads(Path(a.call).read_text(encoding='utf-8-sig'))
  if call['name'] not in ALLOW or call['name'] not in names:raise RuntimeError('Tool is not a discovered read-only Eagle operation')
  result=request('tools/call',call)
 else:result=catalog
 if 'error' in result or result.get('result',{}).get('isError'):raise RuntimeError('Eagle returned a tool error')
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print('SAVED',str(out),'DISCOVERED_TOOLS',len(names))
if __name__=='__main__':main()

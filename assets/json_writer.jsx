function jsonString(v){
 if(v===null)return 'null';
 if(typeof v==='string')return '"'+v.replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\r/g,'\\r').replace(/\n/g,'\\n').replace(/\t/g,'\\t')+'"';
 if(typeof v==='number'||typeof v==='boolean')return String(v);
 var a=[],k;
 if(v instanceof Array){for(var i=0;i<v.length;i++)a.push(jsonString(v[i]));return '['+a.join(',')+']';}
 for(k in v)if(v.hasOwnProperty(k))a.push(jsonString(k)+':'+jsonString(v[k]));
 return '{'+a.join(',')+'}';
}
function writeJSON(file,value){var f=new File(file);f.encoding='UTF8';f.open('w');f.write(jsonString(value));f.close();}

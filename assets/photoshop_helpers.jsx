app.displayDialogs=DialogModes.NO;
app.preferences.rulerUnits=Units.PIXELS;
app.preferences.typeUnits=TypeUnits.POINTS;
function note(s){var f=new File(W+'/checks/build_status.txt');f.encoding='UTF8';f.open('a');f.writeln(s);f.close();}
function rgb(hex){var c=new SolidColor();c.rgb.hexValue=hex;return c;}
var D,G;
function shape(name,x,y,w,h,color,ellipse){
 var mk=new ActionDescriptor(),ref=new ActionReference();ref.putClass(stringIDToTypeID('contentLayer'));mk.putReference(charIDToTypeID('null'),ref);
 var use=new ActionDescriptor(),col=new ActionDescriptor(),c=rgb(color);col.putDouble(charIDToTypeID('Rd  '),c.rgb.red);col.putDouble(charIDToTypeID('Grn '),c.rgb.green);col.putDouble(charIDToTypeID('Bl  '),c.rgb.blue);
 var solid=new ActionDescriptor();solid.putObject(charIDToTypeID('Clr '),charIDToTypeID('RGBC'),col);use.putObject(charIDToTypeID('Type'),stringIDToTypeID('solidColorLayer'),solid);
 var sh=new ActionDescriptor();sh.putUnitDouble(charIDToTypeID('Top '),charIDToTypeID('#Pxl'),y);sh.putUnitDouble(charIDToTypeID('Left'),charIDToTypeID('#Pxl'),x);sh.putUnitDouble(charIDToTypeID('Btom'),charIDToTypeID('#Pxl'),y+h);sh.putUnitDouble(charIDToTypeID('Rght'),charIDToTypeID('#Pxl'),x+w);use.putObject(charIDToTypeID('Shp '),ellipse?charIDToTypeID('Elps'):charIDToTypeID('Rctn'),sh);mk.putObject(charIDToTypeID('Usng'),stringIDToTypeID('contentLayer'),use);executeAction(charIDToTypeID('Mk  '),mk,DialogModes.NO);
 var l=D.activeLayer;l.name=name;l.move(G,ElementPlacement.INSIDE);return l;
}
function text(name,value,x,y,size,color,bold,tracking){var l=D.artLayers.add();l.kind=LayerKind.TEXT;l.name=name;var t=l.textItem;t.contents=value;t.position=[x,y];t.size=size;t.color=rgb(color);t.font=bold?'Arial-BoldMT':'ArialMT';t.tracking=tracking||0;t.antiAliasMethod=AntiAlias.SHARP;l.move(G,ElementPlacement.INSIDE);return l;}
function mask(x,y,w,h){D.selection.select([[x,y],[x+w,y],[x+w,y+h],[x,y+h]]);var d=new ActionDescriptor(),r=new ActionReference();d.putClass(charIDToTypeID('Nw  '),charIDToTypeID('Chnl'));r.putEnumerated(charIDToTypeID('Chnl'),charIDToTypeID('Chnl'),charIDToTypeID('Msk '));d.putReference(charIDToTypeID('At  '),r);d.putEnumerated(charIDToTypeID('Usng'),charIDToTypeID('UsrM'),charIDToTypeID('RvlS'));executeAction(charIDToTypeID('Mk  '),d,DialogModes.NO);D.selection.deselect();}
function image(name,file,x,y,w,h,region,contain){
 var d=new ActionDescriptor();d.putPath(charIDToTypeID('null'),new File(file));executeAction(charIDToTypeID('Plc '),d,DialogModes.NO);var l=D.activeLayer;l.name=name;var b=l.bounds,bw=b[2].as('px')-b[0].as('px'),bh=b[3].as('px')-b[1].as('px');var r=region||[0,0,1,1];var rw=bw*r[2],rh=bh*r[3],s=contain?Math.min(w/rw,h/rh):Math.max(w/rw,h/rh);
 l.resize(s*100,s*100,AnchorPosition.MIDDLECENTER);b=l.bounds;var tx=x+(w-rw*s)/2-r[0]*bw*s,ty=y+(h-rh*s)/2-r[1]*bh*s;l.translate(tx-b[0].as('px'),ty-b[1].as('px'));if(contain)mask(x+(w-rw*s)/2,y+(h-rh*s)/2,rw*s,rh*s);else mask(x,y,w,h);l.move(G,ElementPlacement.INSIDE);return l;
}
function frame(name,x,y,w,h,c){shape(name+' top',x,y,w,1,c);shape(name+' bottom',x,y+h-1,w,1,c);shape(name+' left',x,y,1,h,c);shape(name+' right',x+w-1,y,1,h,c);}

function group(name){G=D.layerSets.add();G.name=name;}



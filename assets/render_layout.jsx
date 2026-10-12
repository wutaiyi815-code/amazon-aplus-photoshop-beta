function setAppearance(l,n){
 if(n.opacity!==undefined)l.opacity=n.opacity;
 if(n.blend)l.blendMode=BlendMode[n.blend];
 if(n.clip_to_previous)l.grouped=true;
}
function stretchImage(n,x,y){
 var a=new ActionDescriptor();a.putPath(charIDToTypeID('null'),new File(n.file));executeAction(charIDToTypeID('Plc '),a,DialogModes.NO);
 var l=D.activeLayer,b=l.bounds;l.name=n.name;var w=n.box[2],h=n.box[3];
 l.resize(w/(b[2].as('px')-b[0].as('px'))*100,h/(b[3].as('px')-b[1].as('px'))*100,AnchorPosition.MIDDLECENTER);
 b=l.bounds;l.translate(x-b[0].as('px'),y-b[1].as('px'));mask(x,y,w,h);l.move(G,ElementPlacement.INSIDE);return l;
}
function polygonMask(l,points,ox,oy){
 D.activeLayer=l;var d=new ActionDescriptor(),r=new ActionReference();
 r.putEnumerated(charIDToTypeID('Chnl'),charIDToTypeID('Chnl'),charIDToTypeID('Msk '));d.putReference(charIDToTypeID('null'),r);executeAction(charIDToTypeID('Dlt '),d,DialogModes.NO);
 var p=[];for(var i=0;i<points.length;i++)p.push([points[i][0]+ox,points[i][1]+oy]);D.selection.select(p);
 d=new ActionDescriptor();r=new ActionReference();d.putClass(charIDToTypeID('Nw  '),charIDToTypeID('Chnl'));r.putEnumerated(charIDToTypeID('Chnl'),charIDToTypeID('Chnl'),charIDToTypeID('Msk '));d.putReference(charIDToTypeID('At  '),r);d.putEnumerated(charIDToTypeID('Usng'),charIDToTypeID('UsrM'),charIDToTypeID('RvlS'));executeAction(charIDToTypeID('Mk  '),d,DialogModes.NO);D.selection.deselect();
}
function nodes(list,ox,oy){
 for(var i=0;i<list.length;i++){
  var n=list[i],l;
  if(n.type==='group'){
   var parent=G;G=G.layerSets.add();G.name=n.name;var g=G,o=n.offset||[0,0];nodes(n.layers,ox+o[0],oy+o[1]);G=parent;l=g;
  }else if(n.type==='text'){
   l=text(n.name,n.text,ox+n.position[0],oy+n.position[1],n.size,n.color,n.bold,n.tracking);l.textItem.font=n.font||((n.bold)?'Arial-BoldMT':'ArialMT');l.textItem.useAutoLeading=false;l.textItem.leading=n.leading||n.size*1.22;
  }else if(n.type==='shape'){
   l=shape(n.name,ox+n.box[0],oy+n.box[1],n.box[2],n.box[3],n.color,n.ellipse||false);
  }else if(n.type==='image'){
   var x=ox+n.box[0],y=oy+n.box[1];
   l=(n.fit==='stretch')?stretchImage(n,x,y):image(n.name,n.file,x,y,n.box[2],n.box[3],n.crop_fraction,n.fit==='contain');
   if(n.mask_points)polygonMask(l,n.mask_points,ox,oy);
  }else throw Error('Unknown layer type '+n.type);
  setAppearance(l,n);if(n.angle)l.rotate(n.angle,AnchorPosition.MIDDLECENTER);
 }
}
function countLayers(g,result){for(var i=0;i<g.layers.length;i++){var l=g.layers[i];if(l.typename==='LayerSet')countLayers(l,result);else if(l.kind===LayerKind.TEXT)result.text++;else if(l.kind===LayerKind.SMARTOBJECT)result.smartobjects++;}}
function png(doc,file){doc.saveAs(new File(file),new PNGSaveOptions(),true,Extension.LOWERCASE);}
function recolor(l,hex){
 D.activeLayer=l;var d=new ActionDescriptor(),r=new ActionReference();r.putProperty(charIDToTypeID('Prpr'),charIDToTypeID('Lefx'));r.putEnumerated(charIDToTypeID('Lyr '),charIDToTypeID('Ordn'),charIDToTypeID('Trgt'));d.putReference(charIDToTypeID('null'),r);
 var fx=new ActionDescriptor();fx.putUnitDouble(charIDToTypeID('Scl '),charIDToTypeID('#Prc'),100);var f=new ActionDescriptor();f.putBoolean(charIDToTypeID('enab'),true);f.putEnumerated(charIDToTypeID('Md  '),charIDToTypeID('BlnM'),charIDToTypeID('Nrml'));f.putUnitDouble(charIDToTypeID('Opct'),charIDToTypeID('#Prc'),100);
 var c=rgb(hex),col=new ActionDescriptor();col.putDouble(charIDToTypeID('Rd  '),c.rgb.red);col.putDouble(charIDToTypeID('Grn '),c.rgb.green);col.putDouble(charIDToTypeID('Bl  '),c.rgb.blue);f.putObject(charIDToTypeID('Clr '),charIDToTypeID('RGBC'),col);fx.putObject(charIDToTypeID('SoFi'),charIDToTypeID('SoFi'),f);d.putObject(charIDToTypeID('T   '),charIDToTypeID('Lefx'),fx);executeAction(charIDToTypeID('setd'),d,DialogModes.NO);
}
function findLayer(g,name){for(var i=0;i<g.layers.length;i++){var l=g.layers[i];if(l.name===name)return l;if(l.typename==='LayerSet'){var found=findLayer(l,name);if(found)return found;}}return null;}

"""Public drawing/label counterfactuals, with no edits to original fixtures."""
import argparse,hashlib,json,zipfile
from copy import deepcopy
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[2]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
V='urn:schemas-microsoft-com:vml'
def q(ns,s):return '{'+ns+'}'+s
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'evidence/business-map-232/drawing-probes-r1');args=parser.parse_args();out=args.out.absolute();out.mkdir(exist_ok=False);parent=ROOT/'evidence/format-expansion/complex_clean.docx';rows=[]
 with zipfile.ZipFile(parent) as src:base=src.read('word/document.xml')
 cases=[('inline501','inline',25,20.04,0),('anchor499','anchor',25,19.96,0),('anchor500','anchor',25,20,0),('anchor501','anchor',25,20.04,0),('body7','body',0,0,0),('labels1','label',1,5,1),('labels10','label',1,5,10),('labels11','label',1,5,11),('labels2mm','label',2,5,11),('labelsHeight1','label',5,1,11),('labelsHeight2','label',5,2,11),('anchors2Equal','anchor',25,10,2),('anchors2Above','anchor',25,10.02,2),('anchorSquare499','anchorSquare',25,19.96,0),('anchorSquare501','anchorSquare',25,20.04,0)]
 for name,kind,width,height,count in cases:
  root=etree.fromstring(base);body=root.find(q(W,'body'));section=body.find(q(W,'sectPr'))
  if kind in ['inline','anchor','anchorSquare']:
   inline=root.find('.//'+q(WP,'inline'));inline.find(q(WP,'extent')).set('cx',str(round(width*36000)));inline.find(q(WP,'extent')).set('cy',str(round(height*36000)))
   for ext in inline.findall('.//'+q(A,'ext')):ext.set('cx',str(round(width*36000)));ext.set('cy',str(round(height*36000)))
   if kind in ['anchor','anchorSquare']:
    anchor=etree.Element(q(WP,'anchor'),nsmap=inline.nsmap);anchor.attrib.update({'distT':'0','distB':'0','distL':'0','distR':'0','simplePos':'0','relativeHeight':'0','behindDoc':'0','locked':'0','layoutInCell':'1','allowOverlap':'1'})
    etree.SubElement(anchor,q(WP,'simplePos'),x='0',y='0')
    for axis,relative in [('H','column'),('V','paragraph')]:etree.SubElement(etree.SubElement(anchor,q(WP,'position'+axis),relativeFrom=relative),q(WP,'posOffset')).text='0'
    for child in list(inline):
     anchor.append(deepcopy(child))
     if child.tag==q(WP,'extent'):
      wrap=etree.SubElement(anchor,q(WP,'wrapSquare' if kind=='anchorSquare' else 'wrapNone'))
      if kind=='anchorSquare':wrap.set('wrapText','bothSides')
    inline.getparent().replace(inline,anchor)
    if count==2:
     drawing=anchor.getparent();duplicate=deepcopy(drawing);duplicate.find('.//'+q(WP,'docPr')).set('id','2');drawing.getparent().append(duplicate)
  if kind=='body':
   p=etree.Element(q(W,'p'));r=etree.SubElement(p,q(W,'r'));pr=etree.SubElement(r,q(W,'rPr'));etree.SubElement(pr,q(W,'sz')).set(q(W,'val'),'14');etree.SubElement(r,q(W,'t')).text='small body text with enough characters for the old heuristic';body.insert(list(body).index(section),p)
  if kind=='label':
   for index in range(count):
    p=etree.Element(q(W,'p'));r=etree.SubElement(p,q(W,'r'));pict=etree.SubElement(r,q(W,'pict'));shape=etree.SubElement(pict,q(V,'shape'),id='Label'+str(index),type='#_x0000_t202',style=f'position:absolute;width:{width}mm;height:{height}mm;margin-left:0;margin-top:0')
    tx=etree.SubElement(etree.SubElement(shape,q(V,'textbox')),q(W,'txbxContent'));tp=etree.SubElement(tx,q(W,'p'));tr=etree.SubElement(tp,q(W,'r'));etree.SubElement(tr,q(W,'t')).text='X';body.insert(list(body).index(section),p)
  path=out/(name+'.docx')
  with zipfile.ZipFile(parent) as src,zipfile.ZipFile(path,'w') as dst:
   for info in src.infolist():dst.writestr(info,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else src.read(info.filename))
  rows.append({'case':name,'input':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'kind':kind,'width_mm':width,'height_mm':height,'label_count':count})
 (out/'inputs.json').write_text(json.dumps({'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'cases':rows,'limits':'Synthetic OpenXML probes; validity and native classification require actual checks.'},indent=2),encoding='utf-8');print(json.dumps({'cases':len(rows)}))
if __name__=='__main__':main()

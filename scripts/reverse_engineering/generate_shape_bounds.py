"""Synthetic VML shape bounds including strict/equal and rotation counterfactuals."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[2];V='urn:schemas-microsoft-com:vml';W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);base=ROOT/'evidence/business-map-232/drawing-probes-r3/labels11.docx';rows=[]
 with zipfile.ZipFile(base) as src:xml=src.read('word/document.xml')
 cases=[('widthBelow',176.99,5,0,None),('widthEqual',177,5,0,None),('widthAbove',177.01,5,0,None),('heightBelow',5,252.99,0,None),('heightEqual',5,253,0,None),('heightAbove',5,253.01,0,None),('rotated90',253,5,90,None),('rotated180',253,5,180,None),('rotated270',253,5,270,None),('rotated45',177,5,45,None),('insetZero',177,5,0,'0,0,0,0'),('insetLarge',177,5,0,'2mm,2mm,2mm,2mm')]
 cases += [('rotated44',177,5,44,None),('rotated46',177,5,46,None)]
 cases += [('landscapeWidthBelow',263.99,5,0,None),('landscapeWidthEqual',264,5,0,None),('landscapeWidthAbove',264.01,5,0,None),('landscapeHeightBelow',5,165.99,0,None),('landscapeHeightEqual',5,166,0,None),('landscapeHeightAbove',5,166.01,0,None)]
 for name,width,height,rotation,inset in cases:
  intended_width,intended_height=width,height
  root=etree.fromstring(xml)
  if name.startswith('landscape'):
   size=root.find('.//{'+W+'}sectPr/{'+W+'}pgSz');page_width_twips=size.get('{'+W+'}w');size.set('{'+W+'}w',size.get('{'+W+'}h'));size.set('{'+W+'}h',page_width_twips);size.set('{'+W+'}orient','landscape')
  for shape in root.findall('.//{'+V+'}shape'):
   shape.set('style',f'position:absolute;width:{width}mm;height:{height}mm;margin-left:0;margin-top:0'+(f';rotation:{rotation}' if rotation else ''))
   if inset is not None:shape.find('{'+V+'}textbox').set('inset',inset)
  assert width==intended_width and height==intended_height and isinstance(width,(int,float)) and isinstance(height,(int,float))
  path=out/(name+'.docx')
  with zipfile.ZipFile(base) as src,zipfile.ZipFile(path,'w') as dst:
   for info in src.infolist():dst.writestr(info,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else src.read(info.filename))
  rows.append({'case':name,'input':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width_mm':width,'height_mm':height,'rotation':rotation,'inset':inset})
 (out/'inputs.json').write_text(json.dumps({'parent_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'cases':rows},indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'cases':len(rows)}))
if __name__=='__main__':main()

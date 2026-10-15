"""Isolate native textbox dimension bounds, position and page orientation."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[2];V='urn:schemas-microsoft-com:vml';W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);base=ROOT/'evidence/business-map-232/drawing-probes-r3/labels11.docx';rows=[]
 with zipfile.ZipFile(base) as src:xml=src.read('word/document.xml')
 cases=[('control',5,5,0,0,'portrait'),('widthBelow',176.99,5,0,0,'portrait'),('widthEqual',177,5,0,0,'portrait'),('widthAbove',177.01,5,0,0,'portrait'),('heightBelow',5,253.99,0,0,'portrait'),('heightEqual',5,254,0,0,'portrait'),('heightAbove',5,254.01,0,0,'portrait'),('smallWidthTall',1,300,0,0,'portrait'),('smallHeightWide',300,1,0,0,'portrait'),('positionRight',5,5,300,0,'portrait'),('positionBelow',5,5,0,300,'portrait'),('landscapeWide',250,5,0,0,'landscape'),('landscapeTall',5,200,0,0,'landscape')]
 for name,width,height,left,top,orientation in cases:
  root=etree.fromstring(xml)
  for shape in root.findall('.//{'+V+'}shape'):shape.set('style',f'position:absolute;width:{width}mm;height:{height}mm;margin-left:{left}mm;margin-top:{top}mm' if left or top else f'position:absolute;width:{width}mm;height:{height}mm;margin-left:0;margin-top:0')
  if orientation=='landscape':
   size=root.find('.//{'+W+'}sectPr/{'+W+'}pgSz');oldw=size.get('{'+W+'}w');size.set('{'+W+'}w',size.get('{'+W+'}h'));size.set('{'+W+'}h',oldw);size.set('{'+W+'}orient','landscape')
  path=out/(name+'.docx')
  with zipfile.ZipFile(base) as src,zipfile.ZipFile(path,'w') as dst:
   for info in src.infolist():dst.writestr(info,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else src.read(info.filename))
  rows.append({'case':name,'input':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width_mm':width,'height_mm':height,'left_mm':left,'top_mm':top,'orientation':orientation})
 (out/'inputs.json').write_text(json.dumps({'parent_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'cases':rows},indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'cases':len(rows)}))
if __name__=='__main__':main()

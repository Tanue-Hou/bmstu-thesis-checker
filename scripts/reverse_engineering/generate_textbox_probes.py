"""One-variable counterfactuals for units, content, fit and inset exclusions."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[2]
V='urn:schemas-microsoft-com:vml';W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False)
 base=ROOT/'evidence/business-map-232/drawing-probes-r3/labels11.docx';rows=[]
 cases=[('cm','width:1mm','width:0.1cm'),('pt','width:1mm','width:2.834645669pt'),('in','width:1mm','width:0.03937007874in'),('px','width:1mm','width:3.779527559px'),('unitless','width:1mm','width:1'),('tall','height:5mm','height:50mm'),('wide','width:1mm;height:5mm','width:50mm;height:1mm'),('fitWidth','width:1mm;height:5mm','width:1mm;height:5mm'),('fitHeight','width:1mm;height:5mm','width:5mm;height:1mm'),('fitFalse','width:1mm','width:1mm'),('insetZero','width:1mm','width:1mm'),('insetLarge','width:1mm','width:1mm'),('empty','width:1mm','width:1mm'),('longText','width:1mm','width:1mm')]
 cases += [(name,'width:1mm;height:5mm','width:5mm;height:1mm') for name in ['fitHeightTrue','fitHeightFalse','shapeFitHeightTrue','shapeFitHeightT']]
 cases += [('shapeFitWidthT','width:1mm','width:1mm'),('shapeFitHeightFalse','width:1mm;height:5mm','width:5mm;height:1mm')]
 for unit,values in [('cm',['0.199','0.2','0.201']),('pt',['5.65','5.66929133858','5.69']),('in',['0.0783','0.07874015748','0.0792']),('', ['1.99','2','2.01'])]:
  cases += [('boundary'+(unit or 'unitless')+str(i),'width:1mm','width:'+value+unit) for i,value in enumerate(values)]
 with zipfile.ZipFile(base) as src:xml=src.read('word/document.xml')
 for name,old,new in cases:
  root=etree.fromstring(xml)
  for shape in root.findall('.//{'+V+'}shape'):
   shape.set('style',shape.get('style').replace(old,new));textbox=shape.find('{'+V+'}textbox')
   if name.startswith('fit'):textbox.set('style','mso-fit-shape-to-text:'+('f' if name=='fitFalse' else 't'))
   if name in ['fitHeightTrue','fitHeightFalse']:textbox.set('style','mso-fit-shape-to-text:'+('true' if name.endswith('True') else 'false'))
   if name.startswith('shapeFit'):shape.set('style',shape.get('style')+';mso-fit-shape-to-text:'+('true' if name.endswith('True') else 'false' if name.endswith('False') else 't'))
   if name.startswith('inset'):textbox.set('inset','0,0,0,0' if name=='insetZero' else '2mm,2mm,2mm,2mm')
   if name in ['empty','longText']:textbox.find('.//{'+W+'}t').text='' if name=='empty' else 'ordinary textbox content '*30
  target=out/(name+'.docx')
  with zipfile.ZipFile(base) as src,zipfile.ZipFile(target,'w') as dst:
   for info in src.infolist():dst.writestr(info,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else src.read(info.filename))
  rows.append({'case':name,'input':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'variable':name})
 (out/'inputs.json').write_text(json.dumps({'parent_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'cases':rows},indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'cases':len(rows)}))
if __name__=='__main__':main()

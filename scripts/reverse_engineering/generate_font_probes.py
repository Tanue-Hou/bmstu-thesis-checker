"""Isolate native font boundaries, counting and role exclusions."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[2];W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';V='urn:schemas-microsoft-com:vml'
def q(ns,name):return '{'+ns+'}'+name
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);base=ROOT/'evidence/dynamic-master/baseline.docx';rows=[]
 with zipfile.ZipFile(base) as src:xml=src.read('word/document.xml');style_xml=src.read('word/styles.xml')
 cases=[('small10',15,10,'body'),('small11',15,11,'body'),('smallEqual',16,11,'body'),('tinyEqual',8,11,'body'),('tinyAbove',9,11,'body'),('large10',37,10,'body'),('large11',37,11,'body'),('largeEqual',36,11,'body'),('smallSpacePad',15,10,'pad'),('smallSpaces',15,11,'spaces'),('smallAscii',15,11,'ascii'),('smallEmoji',15,6,'emoji'),('smallSuper',15,11,'super'),('largeTable',37,11,'table'),('smallTable',15,11,'table'),('largeTextbox',37,11,'textbox'),('largeTextbox101',37,101,'textbox'),('largeAfter100',37,11,'after100'),('largeAfter101',37,11,'after101')]
 cases += [('paragraphInheritedSmall',15,11,'paragraphStyle'),('characterInheritedLarge',37,11,'characterStyle')]
 for name,size,n,role in cases:
  root=etree.fromstring(xml);body=root.find(q(W,'body'));section=body.find(q(W,'sectPr'));paragraph=etree.Element(q(W,'p'));target=paragraph
  if role=='table':
   table=etree.Element(q(W,'tbl'));etree.SubElement(table,q(W,'tblPr'));col=etree.SubElement(etree.SubElement(table,q(W,'tblGrid')),q(W,'gridCol'));col.set(q(W,'w'),'9000');cell=etree.SubElement(etree.SubElement(table,q(W,'tr')),q(W,'tc'));cell.append(paragraph);target=table
  elif role in ['textbox','after100','after101']:
   outer=etree.Element(q(W,'p'));pict=etree.SubElement(etree.SubElement(outer,q(W,'r')),q(W,'pict'));shape=etree.SubElement(pict,q(V,'shape'),id='FontProbe',type='#_x0000_t202',style='position:absolute;width:50mm;height:50mm;margin-left:0;margin-top:0');content=etree.SubElement(etree.SubElement(shape,q(V,'textbox')),q(W,'txbxContent'));content.append(paragraph);target=outer
   if role.startswith('after'):
    run=etree.SubElement(paragraph,q(W,'r'));pr=etree.SubElement(run,q(W,'rPr'));etree.SubElement(pr,q(W,'sz')).set(q(W,'val'),'28');etree.SubElement(run,q(W,'t')).text='Ж'*int(role[5:])
  styles=etree.fromstring(style_xml);run=etree.SubElement(paragraph,q(W,'r'));pr=etree.SubElement(run,q(W,'rPr'))
  if role.endswith('Style'):
   kind='paragraph' if role=='paragraphStyle' else 'character';parent_style=etree.SubElement(styles,q(W,'style'));parent_style.set(q(W,'type'),kind);parent_style.set(q(W,'styleId'),'FontParentProbe');etree.SubElement(parent_style,q(W,'name')).set(q(W,'val'),'FontParentProbe');etree.SubElement(parent_style,q(W,'basedOn')).set(q(W,'val'),'Normal' if kind=='paragraph' else 'DefaultParagraphFont');etree.SubElement(etree.SubElement(parent_style,q(W,'rPr')),q(W,'sz')).set(q(W,'val'),str(size));child=etree.SubElement(styles,q(W,'style'));child.set(q(W,'type'),kind);child.set(q(W,'styleId'),'FontChildProbe');etree.SubElement(child,q(W,'name')).set(q(W,'val'),'FontChildProbe');etree.SubElement(child,q(W,'basedOn')).set(q(W,'val'),'FontParentProbe')
   if kind=='paragraph':pp=etree.Element(q(W,'pPr'));paragraph.insert(0,pp);etree.SubElement(pp,q(W,'pStyle')).set(q(W,'val'),'FontChildProbe')
   else:etree.SubElement(pr,q(W,'rStyle')).set(q(W,'val'),'FontChildProbe')
  else:etree.SubElement(pr,q(W,'sz')).set(q(W,'val'),str(size))
  if role=='super':etree.SubElement(pr,q(W,'vertAlign')).set(q(W,'val'),'superscript')
  text=(' '*n if role=='spaces' else 'X'*n if role=='ascii' else '😀'*n if role=='emoji' else 'Ж'*n);text=' '+text+' ' if role=='pad' else text
  element=etree.SubElement(run,q(W,'t'));element.text=text;element.set('{http://www.w3.org/XML/1998/namespace}space','preserve');body.insert(list(body).index(section),target);path=out/(name+'.docx')
  with zipfile.ZipFile(base) as src,zipfile.ZipFile(path,'w') as dst:
   for info in src.infolist():dst.writestr(info,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else etree.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/styles.xml' and role.endswith('Style') else src.read(info.filename))
  rows.append({'case':name,'input':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'half_points':size,'text_utf16_units':len(text.encode('utf-16le'))//2,'role':role})
 (out/'inputs.json').write_text(json.dumps({'parent_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'cases':rows},indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'cases':len(rows)}))
if __name__=='__main__':main()

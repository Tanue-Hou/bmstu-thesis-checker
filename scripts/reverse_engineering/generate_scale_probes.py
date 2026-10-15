"""Synthetic font-scale controls; existing papers and native EXE remain untouched."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
V = 'urn:schemas-microsoft-com:vml'


def q(name):
    return '{%s}%s' % (W, name)


def paragraph(text, scale=100):
    p = etree.Element(q('p'))
    etree.SubElement(etree.SubElement(p, q('pPr')), q('spacing')).set(q('line'), '360')
    run = etree.SubElement(p, q('r'))
    prop = etree.SubElement(run, q('rPr'))
    etree.SubElement(prop, q('sz')).set(q('val'), '28')
    etree.SubElement(prop, q('w')).set(q('val'), str(scale))
    etree.SubElement(run, q('t')).text = text
    return p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.absolute()
    out.mkdir(exist_ok=False)
    baseline = ROOT / 'evidence/dynamic-master/baseline.docx'
    specs = [('normal100',100,11,'body'), ('small69_10',69,10,'body'),
             ('small69_11',69,11,'body'), ('small70_11',70,11,'body'),
             ('tiny30_11',30,11,'body'), ('small31_11',31,11,'body'),
             ('large130_11',130,11,'body'), ('large131_10',131,10,'body'),
             ('large131_11',131,11,'body'), ('scale1_11',1,11,'body'),
             ('scale2_11',2,11,'body'), ('beforeSmall',69,11,'before'),
             ('beforeLarge',131,11,'before'), ('fallback60Small',69,11,'fallback60'),
             ('fallback61Small',69,11,'fallback61'), ('tableSmall',69,11,'table'),
             ('tableLarge',131,11,'table'), ('textboxSmall',69,11,'textbox'),
             ('textboxLarge',131,11,'textbox'), ('emojiSmall',69,12,'emoji'),
             ('spacesSmall',69,11,'spaces'),
             ('paragraphInheritedSmall',69,11,'paragraphStyle'),
             ('characterInheritedLarge',131,11,'characterStyle'),
             ('linkedLarge',131,11,'linkedStyle'),
             ('linkedDirect100',100,11,'linkedDirect'),
             ('inheritedDirect100',100,11,'paragraphDirect')]
    rows = []
    for name, scale, length, placement in specs:
        with zipfile.ZipFile(baseline) as src:
            root = etree.fromstring(src.read('word/document.xml'))
            styles = etree.fromstring(src.read('word/styles.xml'))
            body = root.find(q('body'))
            section = body.find(q('sectPr'))
            # A minimal explicit marker makes activation/role the only variant.
            for child in list(body):
                if child is not section:
                    body.remove(child)
            if placement.startswith('fallback'):
                for i in range(int(placement.removeprefix('fallback'))):
                    body.insert(i, paragraph('X'))
            elif placement != 'before':
                body.insert(0, paragraph('\u0412\u0412\u0415\u0414\u0415\u041d\u0418\u0415'))
            text = '\U0001f600' * 6 if placement == 'emoji' else ' ' * length if placement == 'spaces' else '\u0416' * length
            probe = paragraph(text, scale)
            if placement in {'paragraphStyle','characterStyle','linkedStyle','linkedDirect','paragraphDirect'}:
                # Explicit styles isolate inheritance without altering defaults.
                kind = 'character' if placement=='characterStyle' else 'paragraph'
                parent = etree.SubElement(styles,q('style'))
                parent.set(q('type'),kind);parent.set(q('styleId'),'ScaleBase')
                etree.SubElement(parent,q('name')).set(q('val'),'ScaleBase')
                pr = etree.SubElement(parent,q('rPr'))
                etree.SubElement(pr,q('sz')).set(q('val'),'28')
                etree.SubElement(pr,q('w')).set(q('val'),'131' if kind=='character' else '69')
                child = etree.SubElement(styles,q('style'))
                child.set(q('type'),kind);child.set(q('styleId'),'ScaleChild')
                etree.SubElement(child,q('name')).set(q('val'),'ScaleChild')
                etree.SubElement(child,q('basedOn')).set(q('val'),'ScaleBase')
                if placement in {'linkedStyle','linkedDirect'}:
                    etree.SubElement(child,q('link')).set(q('val'),'ScaleLinkedChar')
                    linked = etree.SubElement(styles,q('style'))
                    linked.set(q('type'),'character');linked.set(q('styleId'),'ScaleLinkedChar')
                    etree.SubElement(linked,q('name')).set(q('val'),'ScaleLinkedChar')
                    pr = etree.SubElement(linked,q('rPr'))
                    etree.SubElement(pr,q('sz')).set(q('val'),'28')
                    etree.SubElement(pr,q('w')).set(q('val'),'131')
                run_pr = probe.find('./w:r/w:rPr',{'w':W})
                if placement not in {'linkedDirect','paragraphDirect'}:
                    run_pr.remove(run_pr.find(q('w')))
                container = run_pr if kind=='character' else probe.find(q('pPr'))
                etree.SubElement(container,q('rStyle') if kind=='character' else q('pStyle')).set(q('val'),'ScaleChild')
            target = probe
            if placement == 'table':
                target = etree.Element(q('tbl'))
                etree.SubElement(target,q('tblPr'))
                etree.SubElement(etree.SubElement(target,q('tblGrid')),q('gridCol')).set(q('w'),'9000')
                etree.SubElement(etree.SubElement(target,q('tr')),q('tc')).append(probe)
            elif placement == 'textbox':
                target = etree.Element(q('p'))
                pict = etree.SubElement(etree.SubElement(target,q('r')),q('pict'))
                shape = etree.SubElement(pict,'{%s}shape'%V,id='ScaleProbe',type='#_x0000_t202',style='position:absolute;width:50mm;height:50mm;margin-left:0;margin-top:0')
                etree.SubElement(etree.SubElement(shape,'{%s}textbox'%V),q('txbxContent')).append(probe)
            body.insert(list(body).index(section), target)
            path = out / (name+'.docx')
            with zipfile.ZipFile(path,'w') as dst:
                for info in src.infolist():
                    payload = etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else etree.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/styles.xml' and placement in {'paragraphStyle','characterStyle','linkedStyle','linkedDirect','paragraphDirect'} else src.read(info.filename)
                    dst.writestr(info,payload)
        rows.append({'case':name,'input':path.relative_to(ROOT).as_posix(),
                     'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'scale_pct':scale,'text_utf16_units':length,'placement':placement})
    (out/'inputs.json').write_text(json.dumps({'parent_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'cases':rows},indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'cases':len(rows)}))


if __name__=='__main__':
    main()

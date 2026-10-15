"""Test font counters before, at and after native paragraph activation."""
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


def paragraph(text, size=28):
    p = etree.Element(q('p'))
    etree.SubElement(etree.SubElement(p, q('pPr')), q('spacing')).set(q('line'), '360')
    run = etree.SubElement(p, q('r'))
    etree.SubElement(etree.SubElement(run, q('rPr')), q('sz')).set(q('val'), str(size))
    etree.SubElement(run, q('t')).text = text
    return p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.absolute()
    out.mkdir(exist_ok=False)
    base = ROOT / 'evidence/dynamic-master/baseline.docx'
    specs = [('beforeSmall', 15, 'before', 0), ('beforeLarge', 37, 'before', 0),
             ('unactivatedSmall', 15, 'minimal', 0), ('fallback59Small', 15, 'minimal', 59),
             ('fallback60Small', 15, 'minimal', 60), ('fallback61Small', 15, 'minimal', 61),
             ('fallback60Large', 37, 'minimal', 60), ('fallback61Large', 37, 'minimal', 61),
             ('exactSmallMarker', 15, 'exact', 0), ('prefixSmallMarker', 15, 'prefix', 0),
             ('tableBeforeSmall', 15, 'tableBefore', 0), ('textboxBeforeSmall', 15, 'textboxBefore', 0),
             ('textboxBeforeLarge101', 37, 'textbox101Before', 0), ('fallback1000Small', 15, 'minimal', 1000),
             ('beforeTiny', 8, 'before', 0), ('fallback61Tiny', 8, 'minimal', 61),
             ('tableMarker', 15, 'tableMarker', 0), ('textboxMarker', 15, 'textboxMarker', 0),
             ('fallback59Table',15,'lateTable',59),('fallback60Table',15,'lateTable',60),
             ('fallback59Textbox',15,'lateTextbox',59),('fallback60Textbox',15,'lateTextbox',60),
             ('fallback58Table',15,'lateTable',58),('fallback58Textbox',15,'lateTextbox',58)]
    rows = []
    for name, size, placement, fillers in specs:
        with zipfile.ZipFile(base) as src:
            root = etree.fromstring(src.read('word/document.xml'))
            body = root.find(q('body'))
            section = body.find(q('sectPr'))
            if placement in {'minimal', 'exact', 'prefix', 'tableMarker', 'textboxMarker','lateTable','lateTextbox'}:
                for child in list(body):
                    if child is not section:
                        body.remove(child)
                for index in range(fillers):
                    body.insert(index, paragraph('X'))
                if placement in {'exact', 'prefix'}:
                    body.insert(0, paragraph('\u0420\u0415\u0424\u0415\u0420\u0410\u0422' + (' EXTRA' if placement == 'prefix' else ''), size))
            if placement in {'tableMarker','textboxMarker'}:
                marker=paragraph('\u0420\u0415\u0424\u0415\u0420\u0410\u0422')
                if placement=='tableMarker':
                    container=etree.Element(q('tbl'));etree.SubElement(container,q('tblPr'))
                    etree.SubElement(etree.SubElement(container,q('tblGrid')),q('gridCol')).set(q('w'),'9000')
                    etree.SubElement(etree.SubElement(container,q('tr')),q('tc')).append(marker)
                else:
                    container=etree.Element(q('p'));pict=etree.SubElement(etree.SubElement(container,q('r')),q('pict'))
                    shape=etree.SubElement(pict,'{%s}shape'%V,id='ActivationProbe',type='#_x0000_t202',style='position:absolute;width:50mm;height:50mm;margin-left:0;margin-top:0')
                    etree.SubElement(etree.SubElement(shape,'{%s}textbox'%V),q('txbxContent')).append(marker)
                body.insert(0,container)
            probe = paragraph('\u0416' * 11, size)
            target = probe
            if placement in {'tableBefore','lateTable'}:
                target = etree.Element(q('tbl'))
                etree.SubElement(target, q('tblPr'))
                etree.SubElement(etree.SubElement(target, q('tblGrid')), q('gridCol')).set(q('w'), '9000')
                etree.SubElement(etree.SubElement(target, q('tr')), q('tc')).append(probe)
            if (placement.startswith('textbox') and placement!='textboxMarker') or placement=='lateTextbox':
                target = etree.Element(q('p'))
                pict = etree.SubElement(etree.SubElement(target, q('r')), q('pict'))
                shape = etree.SubElement(pict, '{%s}shape' % V, id='ActivationProbe', type='#_x0000_t202',
                                         style='position:absolute;width:50mm;height:50mm;margin-left:0;margin-top:0')
                content = etree.SubElement(etree.SubElement(shape, '{%s}textbox' % V), q('txbxContent'))
                if placement == 'textbox101Before':
                    normal = paragraph('\u0416' * 101).find(q('r'))
                    probe.insert(1, normal)
                content.append(probe)
            before = placement == 'before' or placement.endswith('Before') or placement == 'tableBefore'
            body.insert(0 if before else list(body).index(section), target)
            if placement in {'lateTable','lateTextbox'}:body.insert(list(body).index(section),paragraph('\u0416'*11,size))
            path = out / (name + '.docx')
            with zipfile.ZipFile(path, 'w') as dst:
                for info in src.infolist():
                    dst.writestr(info, etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                                 if info.filename == 'word/document.xml' else src.read(info.filename))
        rows.append({'case': name, 'input': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'half_points': size, 'text_utf16_units': 11, 'role': placement, 'filler_paragraphs': fillers})
    (out / 'inputs.json').write_text(json.dumps({'parent_sha256': hashlib.sha256(base.read_bytes()).hexdigest(), 'cases': rows}, indent=2) + '\n',
                                      encoding='utf-8', newline='\n')
    print(json.dumps({'cases': len(rows)}))


if __name__ == '__main__':
    main()

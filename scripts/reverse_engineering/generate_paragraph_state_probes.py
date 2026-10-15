"""Isolate paragraph activation, property inheritance and a single-cell table."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from lxml import etree
ROOT = Path(__file__).resolve().parents[2]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def q(name):
    return '{%s}%s' % (W, name)


def paragraph(text, anomalous=False):
    p = etree.Element(q('p'))
    pp = etree.SubElement(p, q('pPr'))
    etree.SubElement(pp, q('spacing')).set(q('line'), '179' if anomalous else '360')
    etree.SubElement(pp, q('ind')).set(q('left'), '-6' if anomalous else '0')
    r = etree.SubElement(p, q('r'))
    etree.SubElement(etree.SubElement(r, q('rPr')), q('sz')).set(q('val'), '28')
    etree.SubElement(r, q('t')).text = text
    return p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.absolute()
    out.mkdir(exist_ok=False)
    base = ROOT / 'evidence/dynamic-master/baseline.docx'
    rows = []
    specs = [('fallback58', 58, 'plain'), ('fallback59', 59, 'plain'),
             ('fallback60', 60, 'plain'), ('fallback61', 61, 'plain'),
             ('blankFallback60', 60, 'blank'), ('exactActivator', 0, 'exact'),
             ('prefixActivator', 0, 'prefix'), ('inheritedBoth', 0, 'style'),
             ('directOverridesStyle', 0, 'override'), ('tableBoth', 0, 'table'),
             ('tableControl', 0, 'tableControl'), ('fallback100', 100, 'plain'),
             ('fallback1000', 1000, 'plain')]
    for name, count, role in specs:
        with zipfile.ZipFile(base) as src:
            root = etree.fromstring(src.read('word/document.xml'))
            styles = etree.fromstring(src.read('word/styles.xml'))
            body = root.find(q('body'))
            for child in list(body):
                if child.tag != q('sectPr'):
                    body.remove(child)
            pre = [paragraph('' if role == 'blank' else 'X') for _ in range(count)]
            if role not in {'plain', 'blank'}:
                pre.append(paragraph('\u0420\u0415\u0424\u0415\u0420\u0410\u0422' + (' EXTRA' if role == 'prefix' else '')))
            probe = paragraph('\u0416', anomalous=role != 'tableControl')
            if role in {'style', 'override'}:
                parent = etree.SubElement(styles, q('style'))
                parent.set(q('type'), 'paragraph')
                parent.set(q('styleId'), 'ParagraphProbeParent')
                etree.SubElement(parent, q('name')).set(q('val'), 'ParagraphProbeParent')
                etree.SubElement(parent, q('basedOn')).set(q('val'), 'Normal')
                pp = etree.SubElement(parent, q('pPr'))
                etree.SubElement(pp, q('spacing')).set(q('line'), '179')
                etree.SubElement(pp, q('ind')).set(q('left'), '-6')
                child = etree.SubElement(styles, q('style'))
                child.set(q('type'), 'paragraph')
                child.set(q('styleId'), 'ParagraphProbeChild')
                etree.SubElement(child, q('name')).set(q('val'), 'ParagraphProbeChild')
                etree.SubElement(child, q('basedOn')).set(q('val'), 'ParagraphProbeParent')
                pp = probe.find(q('pPr'))
                if role == 'style':
                    for property_element in list(pp):
                        pp.remove(property_element)
                else:
                    pp.find(q('spacing')).set(q('line'), '360')
                    pp.find(q('ind')).set(q('left'), '0')
                style = etree.Element(q('pStyle'))
                style.set(q('val'), 'ParagraphProbeChild')
                pp.insert(0, style)
            if role in {'table', 'tableControl'}:
                table = etree.Element(q('tbl'))
                etree.SubElement(table, q('tblPr'))
                etree.SubElement(etree.SubElement(table, q('tblGrid')), q('gridCol')).set(q('w'), '9000')
                cell = etree.SubElement(etree.SubElement(table, q('tr')), q('tc'))
                cell.append(probe)
                pre.append(table)
            else:
                pre.append(probe)
            for index, p in enumerate(pre):
                body.insert(index, p)
            path = out / (name + '.docx')
            with zipfile.ZipFile(path, 'w') as dst:
                for info in src.infolist():
                    data = (etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                            if info.filename == 'word/document.xml' else
                            etree.tostring(styles, xml_declaration=True, encoding='UTF-8', standalone=True)
                            if info.filename == 'word/styles.xml' else src.read(info.filename))
                    dst.writestr(info, data)
        rows.append({'case': name, 'input': path.relative_to(ROOT).as_posix(),
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'filler_paragraphs': count,
                     'role': role, 'text_utf16_units': 1})
    (out / 'inputs.json').write_text(json.dumps({'parent_sha256': hashlib.sha256(base.read_bytes()).hexdigest(),
                                               'cases': rows}, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'cases': len(rows)}))


if __name__ == '__main__':
    main()

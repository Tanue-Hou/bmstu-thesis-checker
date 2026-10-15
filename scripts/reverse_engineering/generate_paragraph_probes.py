"""Create isolated paragraph-property counterexamples on a synthetic baseline."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.absolute()
    out.mkdir(exist_ok=False)
    base = ROOT / 'evidence/dynamic-master/baseline.docx'
    rows = []
    # Every candidate changes one property relative to a 200-unit body control.
    cases = [('control', 360, 'auto', 709, 0, 0, 'both', 200),
             ('single', 240, 'auto', 709, 0, 0, 'both', 200),
             ('double', 480, 'auto', 709, 0, 0, 'both', 200),
             ('exact24', 480, 'exact', 709, 0, 0, 'both', 200),
             ('atLeast24', 480, 'atLeast', 709, 0, 0, 'both', 200),
             ('noFirst', 360, 'auto', 0, 0, 0, 'both', 200),
             ('firstOneInch', 360, 'auto', 1440, 0, 0, 'both', 200),
             ('leftOneInch', 360, 'auto', 709, 1440, 0, 'both', 200),
             ('rightOneInch', 360, 'auto', 709, 0, 1440, 'both', 200),
             ('negativeLeft', 360, 'auto', 709, -1440, 0, 'both', 200),
             ('leftAlign', 360, 'auto', 709, 0, 0, 'left', 200),
             ('single40', 240, 'auto', 709, 0, 0, 'both', 40),
             ('single41', 240, 'auto', 709, 0, 0, 'both', 41),
             ('leftNegative5', 360, 'auto', 709, -5, 0, 'both', 200),
             ('leftNegative6', 360, 'auto', 709, -6, 0, 'both', 200),
             ('rightNegative5', 360, 'auto', 709, 0, -5, 'both', 200),
             ('rightNegative6', 360, 'auto', 709, 0, -6, 'both', 200),
             ('line62', 62, 'auto', 709, 0, 0, 'both', 200),
             ('line63', 63, 'auto', 709, 0, 0, 'both', 200),
             ('line64', 64, 'auto', 709, 0, 0, 'both', 200),
             ('line178', 178, 'auto', 709, 0, 0, 'both', 200),
             ('line179', 179, 'auto', 709, 0, 0, 'both', 200),
             ('line180', 180, 'auto', 709, 0, 0, 'both', 200),
             ('line181', 181, 'auto', 709, 0, 0, 'both', 200),
             ('preambleNegative', 360, 'auto', 709, -1440, 0, 'both', 200),
             ('unactivatedNegative', 360, 'auto', 709, -1440, 0, 'both', 200),
             ('shortNegative', 360, 'auto', 709, -1440, 0, 'both', 1),
             ('shortLine179', 179, 'auto', 709, 0, 0, 'both', 1),
             ('blankNegative', 360, 'auto', 709, -1440, 0, 'both', 0)]
    for name, line, rule, first, left, right, align, length in cases:
        with zipfile.ZipFile(base) as src:
            root = etree.fromstring(src.read('word/document.xml'))
            body = root.find('{%s}body' % W)
            if name == 'unactivatedNegative':
                for child in list(body):
                    if child.tag != '{%s}sectPr' % W:
                        body.remove(child)
            paragraph = etree.Element('{%s}p' % W)
            prop = etree.SubElement(paragraph, '{%s}pPr' % W)
            spacing = etree.SubElement(prop, '{%s}spacing' % W)
            spacing.set('{%s}line' % W, str(line))
            spacing.set('{%s}lineRule' % W, rule)
            ind = etree.SubElement(prop, '{%s}ind' % W)
            for key, value in [('firstLine', first), ('left', left), ('right', right)]:
                ind.set('{%s}%s' % (W, key), str(value))
            etree.SubElement(prop, '{%s}jc' % W).set('{%s}val' % W, align)
            run = etree.SubElement(paragraph, '{%s}r' % W)
            etree.SubElement(etree.SubElement(run, '{%s}rPr' % W), '{%s}sz' % W).set('{%s}val' % W, '28')
            etree.SubElement(run, '{%s}t' % W).text = '\u0416' * length
            body.insert(0 if name == 'preambleNegative' else list(body).index(body.find('{%s}sectPr' % W)), paragraph)
            path = out / (name + '.docx')
            with zipfile.ZipFile(path, 'w') as dst:
                for info in src.infolist():
                    dst.writestr(info, etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                                 if info.filename == 'word/document.xml' else src.read(info.filename))
        rows.append({'case': name, 'input': path.relative_to(ROOT).as_posix(),
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'line': line, 'line_rule': rule, 'first_line_twips': first,
                     'left_twips': left, 'right_twips': right, 'alignment': align,
                     'text_utf16_units': length})
    (out / 'inputs.json').write_text(json.dumps({'parent_sha256': hashlib.sha256(base.read_bytes()).hexdigest(),
                                               'cases': rows}, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'cases': len(rows)}))


if __name__ == '__main__':
    main()

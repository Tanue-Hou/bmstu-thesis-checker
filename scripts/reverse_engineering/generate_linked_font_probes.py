"""Generate and capture three linked paragraph/character-style font probes."""
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'evidence/business-map-232'
SOURCE = BASE / 'font-inputs-r1/small10.docx'
INPUT_DIR = BASE / 'linked-font-inputs-r1'
OUTPUT = BASE / 'linked-font-native-r1'
NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W = '{' + NS + '}'
ET.register_namespace('w', NS)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_case(name, change):
    destination = INPUT_DIR / f'{name}.docx'
    with zipfile.ZipFile(SOURCE) as source, zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename in {'word/document.xml', 'word/styles.xml'}:
                root = ET.fromstring(data)
                change(info.filename, root)
                data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            target.writestr(info, data)
    return destination


def title_char_50(part, root):
    if part == 'word/styles.xml':
        style = next(s for s in root.findall(W + 'style') if s.get(W + 'styleId') == 'TitleChar')
        style.find(W + 'rPr/' + W + 'sz').set(W + 'val', '50')


def unlink_title(part, root):
    if part == 'word/styles.xml':
        style = next(s for s in root.findall(W + 'style') if s.get(W + 'styleId') == 'Title')
        link = style.find(W + 'link')
        if link is not None:
            style.remove(link)


def title_char_50_direct_30(part, root):
    title_char_50(part, root)
    if part == 'word/document.xml':
        paragraphs = root.findall('.//' + W + 'body/' + W + 'p')
        for paragraph in paragraphs[:2]:
            run = paragraph.find(W + 'r')
            rpr = run.find(W + 'rPr')
            if rpr is None:
                rpr = ET.Element(W + 'rPr')
                run.insert(0, rpr)
            size = rpr.find(W + 'sz')
            if size is None:
                size = ET.SubElement(rpr, W + 'sz')
            size.set(W + 'val', '30')


def main():
    INPUT_DIR.mkdir(exist_ok=False)
    cases = [
        ('titleChar50', title_char_50),
        ('unlinkTitle', unlink_title),
        ('titleChar50Direct30', title_char_50_direct_30),
    ]
    rows = []
    for name, transform in cases:
        path = make_case(name, transform)
        rows.append({'case': name, 'input': path.relative_to(ROOT).as_posix(), 'sha256': digest(path)})
    manifest = {'parent_input': SOURCE.relative_to(ROOT).as_posix(), 'parent_sha256': digest(SOURCE), 'cases': rows}
    (INPUT_DIR / 'inputs.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    subprocess.run([
        sys.executable, str(ROOT / 'scripts/reverse_engineering/verify_native_fonts.py'),
        '--inputs', str(INPUT_DIR / 'inputs.json'), '--out', str(OUTPUT),
        '--cases', *(row['case'] for row in rows),
    ], check=True, timeout=240)
    print(json.dumps({'cases': len(rows), 'input_dir': INPUT_DIR.relative_to(ROOT).as_posix(),
                      'native_dir': OUTPUT.relative_to(ROOT).as_posix(), 'parent_sha256': manifest['parent_sha256']}))


if __name__ == '__main__':
    main()

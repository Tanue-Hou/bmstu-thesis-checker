"""Experimental independent DOCX paragraph model; never grants repair permission."""
import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/testvkr-service'))
from parsers.docx_parser import DocxParser
from docx.oxml.ns import qn


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


FACTOR = struct.unpack('<f', bytes.fromhex('6e7f903c'))[0]
INVERSE = struct.unpack('<f', bytes.fromhex('8bc56242'))[0]
NEGATIVE_LIMIT = struct.unpack('<f', bytes.fromhex('cdccccbd'))[0]
ACTIVATORS = ['\u0440\u0435\u0444\u0435\u0440\u0430\u0442',
              '\u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u044f',
              '\u0432\u0432\u0435\u0434\u0435\u043d\u0438\u0435',
              '\u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435']


def predict(source):
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    parser = DocxParser(str(source))
    data = parser.parse_all()
    supported = (data['native232_font_profile_supported'] and not data['tables'] and not data['labels']
                 and not data['images'] and len(data['paragraphs']) <= 60
                 and all(p['style_name'] in {'Normal', 'Title', 'Heading 1'} for p in data['paragraphs']))
    active = False
    counters = {'left': 0, 'right': 0, 'line': 0}
    records = []
    for index, paragraph in enumerate(parser.doc.paragraphs):
        text = paragraph.text.strip()
        if text.lower() in ACTIVATORS:
            active = True
        effective, provenance = parser.effective_paragraph(paragraph)
        prop = effective._p.pPr
        raw = {}
        for name, element_name, attribute in [('line', 'spacing', 'line'),
                                               ('left', 'ind', 'left'), ('right', 'ind', 'right')]:
            element = prop.find(qn('w:' + element_name)) if prop is not None else None
            value = element.get(qn('w:' + attribute)) if element is not None else None
            try:
                raw[name] = int(value) if value is not None else (None if name == 'line' else 0)
            except ValueError:
                raw[name] = None
        if active and text and any(v is None for v in raw.values()):
            supported = False
        measured = {k: f32(v * FACTOR) if v is not None else None for k, v in raw.items()}
        line_candidate = math.trunc(measured['line'] * INVERSE + 0.5) if measured['line'] is not None else None
        matches = {'left': active and bool(text) and measured['left'] is not None and measured['left'] < NEGATIVE_LIMIT,
                   'right': active and bool(text) and measured['right'] is not None and measured['right'] < NEGATIVE_LIMIT,
                   'line': active and bool(text) and line_candidate is not None and line_candidate < 180}
        for key, value in matches.items():
            counters[key] += int(value)
        records.append({'paragraph': index + 1, 'xml_path': paragraph._p.getroottree().getpath(paragraph._p),
                        'active': active, 'trimmed_text_units': len(text.encode('utf-16le')) // 2,
                        'raw_twips': raw, 'resolved_float32': measured, 'line_integer': line_candidate,
                        'matches': matches, 'property_provenance': provenance})
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    return {'experimental': True, 'native_build': 232, 'format': 'docx', 'source_sha256': before,
            'profile_supported': supported, 'counters': counters, 'paragraphs': records,
            'limits': ['Independent model for a bounded plain DOCX profile of at most60 paragraphs using the synthetic Normal/Title/Heading1 style families.',
                       'Exact recognized heading activation only; the >60-paragraph fallback and complex stories remain unverified.',
                       'First-line-indent producer is unresolved and is not assigned an invented predicate.',
                       'No native executable invoked; no repair permission; ordinary policy checker remains separate until acceptance.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = predict(args.input.absolute())
    value = json.dumps(result, ensure_ascii=True, indent=2) + '\n'
    if args.out:
        args.out.absolute().write_text(value, encoding='utf-8', newline='\n')
    else:
        print(value, end='')


if __name__ == '__main__':
    main()

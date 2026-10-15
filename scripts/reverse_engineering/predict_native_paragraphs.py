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
    from checkers.native_paragraph_counts import count_paragraph_candidates
    counters, records, supported = count_paragraph_candidates(data)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    return {'experimental': True, 'native_build': 232, 'format': 'docx', 'source_sha256': before,
            'profile_supported': supported, 'counters': counters, 'paragraphs': records,
            'limits': ['Independent model for plain resolved DOCX paragraphs through the tested1001-paragraph and single-cell-table profile.',
                       'Exact heading activation and >60-paragraph fallback; complex stories and pre-activation tables remain unverified.',
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

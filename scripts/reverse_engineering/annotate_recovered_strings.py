"""Attach raw UTF-16 literals to focused pseudocode, preserving file provenance."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('binary', type=Path)
    parser.add_argument('focused', type=Path)
    args = parser.parse_args()
    binary = args.binary.read_bytes()
    pe = struct.unpack_from('<I', binary, 60)[0]
    number = struct.unpack_from('<H', binary, pe + 6)[0]
    optsize = struct.unpack_from('<H', binary, pe + 20)[0]
    base = struct.unpack_from('<I', binary, pe + 52)[0]
    sections = [struct.unpack_from('<8sIIII', binary, pe + 24 + optsize + i * 40) for i in range(number)]
    literals = {}
    for path in args.focused.glob('????????.c'):
        code = path.read_text(encoding='utf-8')
        def replace(match):
            symbol = match.group(0)
            va = int(symbol.removeprefix('DAT_'), 16)
            rva = va - base
            sec = next((s for s in sections if s[2] <= rva < s[2] + s[3]), None)
            if sec is None:
                return symbol
            offset = sec[4] + rva - sec[2]
            units = []
            for pos in range(offset, min(offset + 1200, len(binary) - 1), 2):
                val = struct.unpack_from('<H', binary, pos)[0]
                if val == 0:
                    break
                if val < 32 and val not in (9, 10, 13):
                    return symbol
                units.append(val)
            if len(units) < 4 or not any(0x400 <= n <= 0x4ff for n in units):
                return symbol
            try:
                text = struct.pack('<' + 'H' * len(units), *units).decode('utf-16le')
            except UnicodeDecodeError:
                return symbol
            record = literals.setdefault(symbol, {'va': hex(va), 'file_offset': hex(offset), 'text': text, 'functions': []})
            if path.stem not in record['functions']:
                record['functions'].append(path.stem)
            return symbol + ' /* UTF16 ' + json.dumps(text, ensure_ascii=False).replace('*/', '* /') + ' */'
        annotated = re.sub(r'DAT_[0-9a-f]{8}', replace, code)
        path.with_suffix('.annotated.c').write_text(annotated, encoding='utf-8')
    result = {'target_sha256': hashlib.sha256(binary).hexdigest(),
              'scope': 'Heuristic UTF-16 literal decoding at explicit data addresses; no inferred execution.',
              'literals': literals}
    (args.focused / 'string-provenance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'decoded_russian_literals': len(literals)}))


if __name__ == '__main__':
    main()

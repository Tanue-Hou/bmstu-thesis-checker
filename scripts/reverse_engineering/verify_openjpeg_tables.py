"""Compare complete upstream DWT tables to file-backed PE bytes, not nearby values."""
import hashlib
import json
import re
import struct
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('binary', type=Path)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    binary = args.binary.read_bytes()
    source = args.source.read_text(encoding='utf-8-sig')
    pe = struct.unpack_from('<I', binary, 60)[0]
    number = struct.unpack_from('<H', binary, pe + 6)[0]
    optsize = struct.unpack_from('<H', binary, pe + 20)[0]
    base = struct.unpack_from('<I', binary, pe + 24 + 28)[0]
    sections = [struct.unpack_from('<8sIIII', binary, pe + 24 + optsize + i * 40) for i in range(number)]
    result = {'target_sha256': hashlib.sha256(binary).hexdigest(),
              'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(), 'tables': []}
    for name in ('opj_dwt_norms', 'opj_dwt_norms_real'):
        match = re.search(r'\b' + name + r'\[4\]\[10\]\s*=\s*\{(.*?)\n\};', source, re.S)
        if not match:
            raise ValueError('Upstream table missing: ' + name)
        rows = re.findall(r'\{([^{}]+)\}', match.group(1))
        values = []
        for row in rows:
            nums = [float(n.strip()) for n in row.split(',') if n.strip()]
            values.extend(nums + [0.0] * (10 - len(nums)))
        if len(values) != 40:
            raise ValueError('Expected 4 x 10 values')
        packed = struct.pack('<40d', *values)
        offset = binary.find(packed)
        if offset < 0:
            raise ValueError('Complete table does not match binary: ' + name)
        sec = next(s for s in sections if s[4] <= offset < s[4] + s[3])
        rva = sec[2] + offset - sec[4]
        result['tables'].append({'name': name, 'values': values, 'double_count': len(values),
                                 'byte_count': len(packed), 'file_offset': hex(offset),
                                 'rva': hex(rva), 'va': hex(base + rva), 'match': 'byte_exact',
                                 'second_match_offset': binary.find(packed, offset + 1),
                                 'role': 'JPEG2000 wavelet normalization coefficients, not thesis-format thresholds'})
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'tables_verified': len(result['tables']), 'double_values_verified': sum(t['double_count'] for t in result['tables'])}))


if __name__ == '__main__':
    main()

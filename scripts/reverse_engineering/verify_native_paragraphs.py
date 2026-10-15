"""Observe actual paragraph report gates without assuming DOCX has producers."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_native_pixels import publish


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--cases', nargs='*')
    parser.add_argument('--work-type', choices=['master', 'phd'], default='master')
    args = parser.parse_args()
    out = args.out.absolute()
    out.mkdir(exist_ok=False)
    rows = []
    for row in json.loads(args.inputs.absolute().read_text())['cases']:
        if args.cases and row['case'] not in args.cases:
            continue
        source = ROOT / row['input']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['sha256']
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/native_reference_cli.py'),
                                 '--trace-paragraphs', '--work-type', args.work_type, '--input', str(source)],
                                capture_output=True, timeout=55)
        assert result.returncode == 0, result.stderr.decode(errors='replace')
        report = json.loads(result.stdout)
        directory = out / row['case']
        publish(Path(report['evidence_directory']), directory)
        hits = json.loads((directory / 'trace.json').read_text())['breakpoint_hits']
        gates = [h for h in hits if h['label'].startswith('paragraph_') and h['label'].endswith('_gate')]
        assert len(gates) == 4
        state = gates[0]['paragraph_report_state']
        assert all(h['paragraph_report_state'] == state for h in gates)
        item = {**row, 'work_type': args.work_type, 'native_counters': state,
                'native_emit_labels': [h['label'] for h in hits if h['label'].startswith('paragraph_') and h['label'].endswith('_emit')],
                'native_diagnostic_count': report['diagnostic_count'],
                'evidence_directory': directory.relative_to(ROOT).as_posix()}
        rows.append(item)
        print(json.dumps(item), flush=True)
    (out / 'matrix.json').write_text(json.dumps({'build': 232, 'cases': rows}, indent=2) + '\n',
                                      encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()

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
from native_reference_cli import validate_native_run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--cases', nargs='*')
    parser.add_argument('--work-type', choices=['master', 'phd'], default='master')
    parser.add_argument('--resume', action='store_true', help='Reuse already published valid captures; append only missing cases.')
    args = parser.parse_args()
    out = args.out.absolute()
    out.mkdir(exist_ok=args.resume)
    matrix_path = out / 'matrix.json'
    rows = json.loads(matrix_path.read_text())['cases'] if args.resume and matrix_path.exists() else []
    for row in json.loads(args.inputs.absolute().read_text())['cases']:
        if args.cases and row['case'] not in args.cases:
            continue
        source = ROOT / row['input']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['sha256']
        directory = out / row['case']
        if any(c['case'] == row['case'] for c in rows):
            continue
        if args.resume and directory.exists():
            report = json.loads((directory / 'report.json').read_text())
        else:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/native_reference_cli.py'),
                                     '--trace-paragraphs', '--work-type', args.work_type, '--input', str(source)],
                                    capture_output=True, timeout=55)
            assert result.returncode == 0, (result.stderr + result.stdout).decode(errors='replace')
            report = json.loads(result.stdout)
            publish(Path(report['evidence_directory']), directory)
        trace = json.loads((directory / 'trace.json').read_text())
        assert report['source_sha256'] == row['sha256'] and report['work_type'] == args.work_type
        validate_native_run(trace, (directory / 'native-result.txt').read_bytes().decode('utf-8'),
                            args.work_type, 'docx', row['sha256'], True)
        hits = trace['breakpoint_hits']
        gates = [h for h in hits if h['label'].startswith('paragraph_') and h['label'].endswith('_report_gate')]
        assert len(gates) == 4
        state = gates[0]['paragraph_report_state']
        assert all(h['paragraph_report_state'] == state for h in gates)
        item = {**row, 'work_type': args.work_type, 'native_counters': state,
                'native_emit_labels': [h['label'] for h in hits if h['label'].startswith('paragraph_') and h['label'].endswith('_emit')],
                'native_diagnostic_count': report['diagnostic_count'],
                'evidence_directory': directory.relative_to(ROOT).as_posix()}
        rows.append(item)
        matrix_path.write_text(json.dumps({'build': 232, 'cases': rows}, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps(item), flush=True)
    (out / 'matrix.json').write_text(json.dumps({'build': 232, 'cases': rows}, indent=2) + '\n',
                                      encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()

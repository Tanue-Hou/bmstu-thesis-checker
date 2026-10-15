"""Sequential native complex-section observations; resumable, no promotion."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from native_reference_cli import validate_native_run


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', default='complex-section-r1',
                        choices=['complex-section-r1', 'complex-section-r2-final'])
    args = parser.parse_args()
    out = ROOT / 'evidence' / args.evidence
    private = ROOT.parent / 'private_trials' / args.evidence / 'native'
    manifest_path = out / 'manifest.json'
    manifest = json.loads(manifest_path.read_bytes())
    rows = []
    factor = struct.unpack('<f', bytes.fromhex('6e7f903c'))[0]
    for mode in ('master', 'phd'):
        for case in manifest['cases']:
            name = mode + '-' + case['case_id']
            source = out / case['path']
            assert sha(source) == case['sha256'], name
            run = private / name
            if not run.exists():
                private.mkdir(parents=True, exist_ok=True)
                result = subprocess.run([sys.executable, '-X', 'utf8',
                    str(ROOT / 'scripts/native_reference_cli.py'), '--input', str(source),
                    '--work-type', mode, '--trace-sections', '--out', str(run)], capture_output=True)
                (private / (name + '.log')).write_bytes(result.stdout + result.stderr)
                if result.returncode:
                    raise RuntimeError('Native run failed; retain and inspect: ' + name)
            report = json.loads((run / 'report.json').read_bytes())
            trace = json.loads((run / 'native/trace.json').read_bytes())
            text = (run / 'native/native-result.txt').read_bytes().decode('utf8')
            validate_native_run(trace, text, mode, 'docx', sha(source), True)
            assert report['trace_sha256'] == sha(run / 'native/trace.json')
            assert report['native_text_sha256'] == sha(run / 'native/native-result.txt')
            hits = {h['label']: h for h in trace['breakpoint_hits'] if h['label'].startswith('section_')}
            expected = 0
            for field in ('header', 'footer'):
                twips = case['section'][field + '_twips']
                mismatch = not 698 <= twips <= 720
                expected += mismatch
                compare = hits['section_' + field + '_compare']['section_state']
                assert compare['target_and_actual_mm'] == [12.5, struct.unpack('<f', struct.pack('<f', twips * factor))[0]], name
                assert bool(hits['section_' + field + '_result']['section_state']['comparison_return_al']) != mismatch, name
                assert ('section_' + field + '_increment' in hits) == mismatch, name
            final = hits['section_distance_report_gate']['section_state']
            assert final['addresses_match'] and final['final_count'] == expected, name
            groups = sum('Размеры колонтитулов должны быть' in d['message'] for d in report['diagnostics'])
            assert groups == int(expected > 0), name
            assert sha(source) == case['sha256'], name
            public = out / 'native' / name
            public.mkdir(parents=True, exist_ok=True)
            files = [('trace.json', 'native/trace.json'), ('native-result.txt', 'native/native-result.txt'),
                     ('report.json', 'report.json'), ('tracer-source.py.txt', 'native/tracer-source.py.txt')]
            for filename, original in files:
                dest = public / filename
                raw = (run / original).read_bytes()
                if dest.exists():
                    assert dest.read_bytes() == raw, str(dest)
                else:
                    dest.write_bytes(raw)
            rows.append({'case': name, 'family': case['family'], 'mode': mode,
                'source_sha256': sha(source), 'expected_count': expected, 'final_counter': final,
                'target_diagnostic_groups': groups,
                'artifact_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in public.iterdir()}})
            receipt = {'status': 'in_progress', 'manifest_sha256': sha(manifest_path), 'cases': rows,
                       'limits': 'Synthetic single-section inputs only. No school-standard, Word-rendering, repair or broad equivalence claim.'}
            (out / 'native-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
            print(name + ' passed', flush=True)
    receipt['status'] = 'passed_native_complex_section_observations'
    receipt['native_runs'] = len(rows)
    (out / 'native-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()

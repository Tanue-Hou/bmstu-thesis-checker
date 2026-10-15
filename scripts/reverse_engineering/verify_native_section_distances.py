"""Boundary cases with actual section comparison/branch observations, no rule promotion."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from differential_mutations import mutate_docx
from native_reference_cli import validate_native_run


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'evidence/differential-platform-r1/section-boundaries-r2'
    private = ROOT.parent / 'private_trials/section-distance-branches-r2'
    out.mkdir(exist_ok=False)
    baseline = ROOT / 'evidence/dynamic-master/baseline.docx'
    raw = baseline.read_bytes()
    rows = []
    for mode in ('master', 'phd'):
        for field in ('header', 'footer'):
            for value in (697, 698, 720, 721):
                name = f'{mode}-{field}-{value}'
                source = out / (name + '.docx')
                source.write_bytes(mutate_docx(raw, {'kind': 'section_page_margin',
                                                   'attribute': field, 'value': value, 'section_index': 0}))
                run = private / name
                execution = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/native_reference_cli.py'),
                                            '--input', str(source), '--work-type', mode, '--trace-sections',
                                            '--out', str(run)], capture_output=True)
                private.mkdir(parents=True, exist_ok=True)
                (private / (name + '.log')).write_bytes(execution.stdout + execution.stderr)
                if execution.returncode:
                    raise RuntimeError(f'Native boundary failed: {name}')
                report = json.loads((run / 'report.json').read_bytes())
                trace = json.loads((run / 'native/trace.json').read_bytes())
                text = (run / 'native/native-result.txt').read_bytes().decode('utf8')
                validate_native_run(trace, text, mode, 'docx', sha(source), True)
                hits = [h for h in trace['breakpoint_hits'] if h['label'].startswith('section_')]
                compare = next(h for h in hits if h['label'] == f'section_{field}_compare')
                result = next(h for h in hits if h['label'] == f'section_{field}_result')
                actual = result['section_state']['comparison_return_al']
                increment = any(h['label'] == f'section_{field}_increment' for h in hits)
                expected = value in (697, 721)
                diagnostic = any('Размеры колонтитулов должны быть' in d['message'] for d in report['diagnostics'])
                assert increment == expected and diagnostic == expected and bool(actual) != expected, name
                increments = [h for h in hits if h['label'].endswith('_increment')]
                assert all(h['registers']['Eax'] == h['section_state']['parser_address'] for h in increments), name
                assert compare['section_state']['target_and_actual_mm'][0] == 12.5, name
                public = out / name
                public.mkdir()
                for filename, original in [('trace.json', run / 'native/trace.json'),
                                            ('native-result.txt', run / 'native/native-result.txt'),
                                            ('report.json', run / 'report.json'),
                                            ('tracer-source.py.txt', run / 'native/tracer-source.py.txt')]:
                    (public / filename).write_bytes(original.read_bytes())
                rows.append({'case': name, 'work_type': mode, 'field': field, 'twips': value,
                             'input_sha256': sha(source), 'comparison': compare['section_state'],
                             'return_al': actual, 'increment_branch_observed': increment,
                             'diagnostic_observed': diagnostic,
                             'artifact_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in public.iterdir()}})
                (out / 'receipt.json').write_text(json.dumps({'status': 'in_progress', 'cases': rows}, ensure_ascii=False, indent=2), encoding='utf8')
                print(name, 'passed', flush=True)
    assert baseline.read_bytes() == raw
    receipt = {'status': 'passed_section_distance_boundary_branches', 'cases': rows,
               'baseline_sha256': sha(baseline), 'source_unchanged': True,
               'limits': 'One-section synthetic DOCX only; first observed section predicate invocation. No rule or repair promotion. Modes master and NKR phd; not general dissertation compliance.'}
    (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()

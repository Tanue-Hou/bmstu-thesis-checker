"""Freeze v0.2.21 measured changes; do not claim a full regression rerun."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    core = ['scripts/check_document.py', 'scripts/repair_build232.py',
            'scripts/testvkr-service/rules/rules_verified.json']
    for name in core:
        prior = subprocess.check_output(['git', 'show', 'v0.2.20:' + name], cwd=ROOT)
        assert (ROOT / name).read_bytes() == prior, name
    metrics = json.loads((ROOT / 'evidence/optimization-audit-r1/metrics.json').read_bytes())
    assert metrics['registry']['context_evidence_valid_counts'] == {'valid': 23}
    logs = ['release-targeted-tests.log', 'final-interface-tests.log']
    for name, count in zip(logs, [40, 11]):
        text = (ROOT / 'evidence/optimization-audit-r1' / name).read_text(encoding='utf8')
        assert f'Ran {count} tests' in text and text.rstrip().endswith('OK'), name
    files = set()
    for args in [['diff', '--name-only', '-z'], ['ls-files', '--others', '--exclude-standard', '-z']]:
        files.update(p for p in subprocess.check_output(['git', *args], cwd=ROOT).decode('utf8').split('\0') if p)
    target = 'evidence/optimization-audit-r1/release-freeze.json'
    files.discard(target)
    assert not any(p.startswith('private_trials/') or p.lower().endswith(('.exe', '.asm')) for p in files)
    receipt = {'version': '0.2.21', 'status': 'passed_bounded_release_checks',
               'targeted_tests': 40, 'final_interface_recheck_tests': 11,
               'full_suite_rerun': False, 'core_unchanged_from': 'v0.2.20',
               'core_sha256': {p: sha(ROOT / p) for p in core},
               'changed_file_sha256': {p: sha(ROOT / p) for p in sorted(files)},
               'limits': 'No detection promotion, repair expansion, accuracy claim or full equivalence claim. Historical published decompilation and license remain separate unresolved work.'}
    (ROOT / target).write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
    print(json.dumps({'status': receipt['status'], 'frozen_files': len(files)}))


if __name__ == '__main__':
    main()

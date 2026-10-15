"""Bounded v0.2.22 acceptance; no whole-suite or equivalence claim."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import context_evidence_valid


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = ROOT / 'evidence/differential-platform-r1'
    log = (evidence / 'release-tests.log').read_text(encoding='utf8')
    assert 'Ran 38 tests' in log and log.rstrip().endswith('OK')
    mcp = json.loads((evidence / 'mcp-receipt.json').read_bytes())
    assert mcp['status'] == 'passed_actual_stdio_mcp_differential' and mcp['tool_count'] == 11
    core = ['scripts/check_document.py', 'scripts/repair_build232.py',
            'scripts/testvkr-service/rules/rules_verified.json',
            'scripts/testvkr-service/checkers/word_format.py',
            'scripts/testvkr-service/parsers/docx_parser.py']
    for name in core:
        assert (ROOT / name).read_bytes() == subprocess.check_output(['git', 'show', 'v0.2.21:' + name], cwd=ROOT), name
    registry = json.loads((ROOT / core[2]).read_bytes())
    contexts = [context for rule in registry['rules'] for build in rule.get('verification_by_build', {}).values()
                for context in build.values()]
    assert len(contexts) == 23 and all(context_evidence_valid(c) for c in contexts)
    target = 'evidence/differential-platform-r1/release-freeze.json'
    names = set()
    for args in [['diff', 'HEAD', '--name-only', '-z'], ['ls-files', '--others', '--exclude-standard', '-z']]:
        names.update(p for p in subprocess.check_output(['git', *args], cwd=ROOT).decode('utf8').split('\0') if p)
    names.discard(target)
    assert not any(p.startswith('private_trials/') or p.lower().endswith(('.exe', '.asm')) for p in names)
    receipt = {'version': '0.2.22', 'status': 'passed_bounded_differential_release', 'targeted_tests': 38,
               'full_suite_rerun': False, 'valid_existing_contexts': len(contexts),
               'core_unchanged_from': 'v0.2.21', 'core_sha256': {p: sha(ROOT / p) for p in core},
               'changed_file_sha256': {p: sha(ROOT / p) for p in sorted(names)},
               'limits': 'Platform and bounded source/branch evidence only. Section tolerance discrepancy remains pending integration. No school accuracy, full equivalence, minimality certification or repair expansion.'}
    (ROOT / target).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'status': receipt['status'], 'contexts': len(contexts), 'files': len(names)}))


if __name__ == '__main__':
    main()

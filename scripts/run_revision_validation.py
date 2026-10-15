"""Retain reproducible local regression inputs, results, logs and source hashes."""
import hashlib
import os
import json
import platform
import subprocess
import sys
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests')]
from test_regression import sample
from check_document import check_file


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',default='evidence/2026-10-15')
    out=(ROOT/parser.parse_args().output_dir).resolve()
    if not out.is_relative_to(ROOT/'evidence'):raise ValueError('Validation output must stay in evidence')
    inputs = out / 'regression_inputs'
    inputs.mkdir(parents=True, exist_ok=True)
    run = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                         cwd=ROOT, capture_output=True, text=True, encoding='utf-8', env={**os.environ,'PYTHONUTF8':'1'})
    (out / 'regression-test.log').write_text(run.stdout + run.stderr, encoding='utf-8')
    args = Namespace(work_type='bachelor', skip_structure=True, skip_pictures=False,
                     skip_word_format=False, skip_dictionary=True)
    cases = []
    for mode in ('inherited', 'direct', 'override', 'character', 'hidden_off', 'exact', 'default', 'partial', 'table'):
        path = sample(mode, inputs / (mode + '.docx'))
        result = check_file(path, args)
        result_path = out / (mode + '.local-result.json')
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        cases.append({'case': mode, 'input': str(path.relative_to(ROOT)), 'input_sha256': digest(path),
                      'result': str(result_path.relative_to(ROOT)), 'result_sha256': digest(result_path),
                      'findings': result['summary']['total']})
    source_paths = sorted(p for folder in ('scripts', 'mcp', 'skills', 'tests', 'templates', 'docs', 'releases', '.codex-plugin')
                          for p in (ROOT / folder).rglob('*')
                          if p.is_file() and p.suffix in ('.py', '.json', '.md', '.java', '.ps1') and '__pycache__' not in p.parts)
    record = {'generated_at_utc': datetime.now(timezone.utc).isoformat(),
              'python': sys.version, 'platform': platform.platform(),
              'test_exit_code': run.returncode, 'cases': cases,
              'scope': 'local regression only; not proof of TestVkr equivalence',
              'source_hashes': {str(p.relative_to(ROOT)): digest(p) for p in source_paths}}
    (out / 'validation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'test_exit_code': run.returncode, 'cases': len(cases), 'evidence': str(out)}))
    return run.returncode


if __name__ == '__main__':
    raise SystemExit(main())

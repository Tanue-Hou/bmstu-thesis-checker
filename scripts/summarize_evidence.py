"""Build a reviewable evidence index without claiming full behavioral equivalence."""
import csv
import hashlib
import json
import re
import sys
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import check_file


def main():
    out = ROOT / 'evidence' / '2026-10-14'
    recovered = out / 'decompilation'
    rows = list(csv.DictReader((recovered / 'functions.tsv').open(encoding='utf-8'), delimiter='\t'))
    focus = list(csv.DictReader((recovered / 'focused' / 'focused-status.tsv').open(encoding='utf-8'), delimiter='\t'))
    statuses = {r['address']: r['status'] for r in rows}
    for row in focus:
        statuses[row['address']] = row['status']
    original = json.loads((out / 'original-line-spacing-1.0.accessibility.json').read_text(encoding='utf-8'))
    match = re.search(r'编辑 Value: (Файл:.*?) ID:', original['tree'])
    if match is None:
        raise ValueError('Original document result not found in retained accessibility capture')
    text = match[1]
    original_path = out / 'regression_inputs' / 'original-body-line-spacing-1.0.docx'
    args = Namespace(work_type='bachelor', skip_structure=False, skip_pictures=False, skip_word_format=False, skip_dictionary=False)
    local = check_file(original_path, args)
    (out / 'original-sample.local-result.json').write_text(json.dumps(local, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    comparison = {'original_output': text,
                  'input_sha256': hashlib.sha256(original_path.read_bytes()).hexdigest(),
                  'original_messages_count': len(re.findall(r'(?:^| )\d+\. ', text)),
                  'local_rule_ids': [f['rule_id'] for f in local['findings']],
                  'formatting_comparison': 'inconclusive',
                  'reason': 'Original output contains structural diagnostics; absence of a spacing diagnostic does not validate the local threshold or the original document-role gates.',
                  'original_evidence': 'original-line-spacing-1.0.accessibility.json'}
    (out / 'original-sample-comparison.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    registry = json.loads((ROOT / 'scripts' / 'testvkr-service' / 'rules' / 'rules_verified.json').read_text(encoding='utf-8'))
    summary = {'generated_at_utc': datetime.now(timezone.utc).isoformat(),
               'identified_functions': len(statuses),
               'functions_with_recovered_pseudocode': sum(s == 'decompiled' for s in statuses.values()),
               'focused_functions': len(focus),
               'original_dynamic_samples_with_saved_output': 1,
               'rules_verified_against_original': sum(r['verification_status'] == 'verified_against_original' for r in registry['rules']),
               'status': 'implementation_repaired_static_analysis_exported_dynamic_rule_verification_incomplete',
               'limitations': ['Recovered pseudocode is not original source', 'Compiler/library functions are included',
                              'Indirect calls and all document-role gates are not fully recovered',
                              'Complete original-program boundary matrix remains pending',
                              'Automatic thesis editing is not implemented in this revision'],
               'next_steps': ['Create structurally valid positive/negative document pairs',
                              'Trace formatting classification and document-role gates',
                              'Capture original outputs for thresholds and counting semantics before promoting rules']}
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    manifest = {str(p.relative_to(out)): {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'manifest.json'}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()

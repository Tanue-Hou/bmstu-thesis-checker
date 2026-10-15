"""Stage/replay/register a narrowly scoped section predicate, preserving migration evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evidence/native-section-integration-r1'
PRIVATE = ROOT.parent / 'private_trials/section-migration-r1'
REGISTRY = ROOT / 'scripts/testvkr-service/rules/rules_verified.json'
CHANGED = ['scripts/check_document.py', 'scripts/issue_locations.py',
           'scripts/testvkr-service/parsers/docx_parser.py',
           'scripts/testvkr-service/checkers/word_format.py']
HELPER = 'scripts/testvkr-service/checkers/native_section_counts.py'
sys.path.insert(0, str(ROOT / 'scripts'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')


def prepare():
    OUT.mkdir(exist_ok=True)
    baseline = subprocess.check_output(['git', 'show', 'v0.2.22:scripts/testvkr-service/rules/rules_verified.json'], cwd=ROOT)
    assert REGISTRY.read_bytes() == baseline, 'Refuse to rebind an already modified registry'
    before = json.loads((PRIVATE / 'before-receipt.json').read_bytes())
    assert before['cases'] == 317 and before['non_target_changed_cases'] == 0
    (PRIVATE / 'registry-before.json').write_bytes(baseline)
    data = json.loads(baseline)
    updated = []
    for rule in data['rules']:
        for name, context in rule.get('verification_by_build', {}).get('232', {}).items():
            implementations = context['implementation_hashes']
            edits = {}
            for file in CHANGED:
                if file not in implementations:
                    continue
                old = hashlib.sha256(subprocess.check_output(['git', 'show', 'v0.2.22:' + file], cwd=ROOT)).hexdigest()
                assert implementations[file] == old, (rule['rule_id'], file)
                edits[file] = {'before': old, 'after': sha(ROOT / file)}
                implementations[file] = edits[file]['after']
            implementations[HELPER] = sha(ROOT / HELPER)
            updated.append({'rule_id': rule['rule_id'], 'context': name, 'changes': edits})
    assert len(updated) == 23
    write(PRIVATE / 'staged-binding-changes.json', updated)
    write(REGISTRY, data)
    print('Staged 23 implementation bindings for mandatory non-target replay; not a completed release')


def audit():
    from argparse import Namespace
    from check_document import check_file
    from native_reference_cli import validate_native_run
    from compare_native_trial import parse_diagnostics
    proof = ROOT / 'evidence/differential-platform-r1/section-boundaries-r2/receipt.json'
    native = json.loads(proof.read_bytes())
    assert native['status'] == 'passed_section_distance_boundary_branches' and len(native['cases']) == 16
    rows = []
    sources = {proof.relative_to(ROOT).as_posix(): sha(proof)}
    for case in native['cases']:
        for name, digest in case['artifact_sha256'].items():
            assert sha(ROOT / name) == digest, name
            sources[name] = digest
        directory = proof.parent / case['case']
        source = proof.parent / (case['case'] + '.docx')
        assert sha(source) == case['input_sha256']
        sources[source.relative_to(ROOT).as_posix()] = sha(source)
        trace = json.loads((directory / 'trace.json').read_bytes())
        diagnostics = validate_native_run(trace, (directory / 'native-result.txt').read_bytes().decode('utf8'),
                                         case['work_type'], 'docx', sha(source), True)
        options = Namespace(work_type=case['work_type'], native_build=232, document_kind='auto', template_id=None,
                            skip_structure=False, skip_pictures=False, skip_word_format=False, skip_dictionary=False)
        local = check_file(source, options)
        matched = [f for f in local['findings'] if f['rule_id'] == 'Word.HeaderFooterDistanceInvalid']
        native_matched = [d for d in diagnostics if any(x['rule_id'] == 'Word.HeaderFooterDistanceInvalid'
                          for x in parse_diagnostics('1. ' + d['message'], 'docx'))]
        assert len(matched) == len(native_matched) == int(case['increment_branch_observed'])
        observations = local['native_section_observations']
        assert observations['supported'] and observations['count'] == int(case['increment_branch_observed'])
        for finding in matched:
            assert finding['threshold']['native_section_predicate_supported']
            assert finding['precise_locations']['occurrence_count'] == 1
        rows.append({'case': case['case'], 'mode': case['work_type'], 'field': case['field'],
                     'twips': case['twips'], 'family_count': len(matched),
                     'native_counter': observations['count'], 'matched': True})
    write(OUT / 'audit.json', {'status': 'passed_native_section_model_boundary_parity', 'cases': rows,
                             'sources': sources, 'implementations': {p: sha(ROOT / p) for p in [*CHANGED, HELPER]},
                             'limits': 'Reuse of 16 retained actual native branch executions; this phase runs the changed local engine only. Single explicit ordinary A4 DOCX section, master/NKR; no repair expansion.'})
    print('Local model matched 16 retained native boundary branches')


def register():
    proof = OUT / 'audit.json'
    audit = json.loads(proof.read_bytes())
    assert audit['status'] == 'passed_native_section_model_boundary_parity'
    for name, digest in {**audit['sources'], **audit['implementations']}.items():
        assert sha(ROOT / name) == digest, name
    data = json.loads(REGISTRY.read_bytes())
    rule = next(r for r in data['rules'] if r['rule_id'] == 'Word.HeaderFooterDistanceInvalid')
    assert not rule.get('verification_by_build', {}).get('232')
    refs = {proof.relative_to(ROOT).as_posix(): sha(proof), **audit['sources']}
    contexts = {}
    for mode in ('master', 'phd'):
        contexts['docx:' + mode] = {'verification_status': 'verified_against_original', 'confidence': 'high',
            'threshold_origin': 'native232_explicit_section_float32_distance_and_counter_branches',
            'verification_evidence_sha256': sha(proof), 'evidence_refs': list(refs), 'evidence_hashes': refs,
            'implementation_hashes': audit['implementations'], 'verified_policy': {},
            'scope': {'build': 232, 'format': 'docx', 'work_type': mode,
                      'profile': 'native232_single_explicit_section_distances',
                      'limits': 'One ordinary portrait A4 DOCX section, explicit integer header/footer distances0..1440twips; no tables, drawings, math, fields/revisions or extra stories. Native anomaly predicate, not school compliance or repair authorization.'}}
    rule.setdefault('verification_by_build', {})['232'] = contexts
    rule.setdefault('predicate_by_build', {})['232'] = {'expected_mm': 12.5,
        'float32_tolerance_mm': 0.20000000298023224, 'twips_float32_factor': 0.017638888210058212,
        'report': 'Each mismatched header/footer increments parser+0x28c; main report slot0x4d>0',
        'limits': 'Does not validate header/footer content, PAGE fields or page-number placement.'}
    write(REGISTRY, data)
    print('Registered two section detection contexts; existing23 still require migration replay finalization')


def finalize():
    from check_document import context_evidence_valid
    before = json.loads((PRIVATE / 'before-receipt.json').read_bytes())
    after = json.loads((PRIVATE / 'after-receipt.json').read_bytes())
    assert before['cases'] == after['cases'] == 317 and after['non_target_changed_cases'] == 0
    assert sha(PRIVATE / 'before.jsonl') == before['result_sha256']
    assert sha(PRIVATE / 'after.jsonl') == after['result_sha256']
    receipt = {'status': 'passed_section_integration_non_target_golden_replay',
               'unique_input_mode_pairs': after['cases'], 'non_target_changed_cases': 0,
               'before_output_sha256': before['result_sha256'], 'after_output_sha256': after['result_sha256'],
               'rebound_contexts': json.loads((PRIVATE / 'staged-binding-changes.json').read_bytes()),
               'implementations': {p: sha(ROOT / p) for p in [*CHANGED, HELPER]},
               'limits': 'Local golden replay preserves all non-target finding semantics, locations and verification status; not fresh native execution. Header/footer target intentionally changed.'}
    path = OUT / 'migration-receipt.json'
    write(path, receipt)
    data = json.loads(REGISTRY.read_bytes())
    for rule in data['rules']:
        for context in rule.get('verification_by_build', {}).get('232', {}).values():
            context['implementation_hashes'][path.relative_to(ROOT).as_posix()] = sha(path)
    assert sum(len(r.get('verification_by_build', {}).get('232', {})) for r in data['rules']) == 25
    assert all(context_evidence_valid(c) for r in data['rules'] for c in r.get('verification_by_build', {}).get('232', {}).values())
    write(REGISTRY, data)
    print('Finalized 25 valid contexts with golden migration receipt binding')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['prepare', 'audit', 'register', 'finalize'])
    arguments = parser.parse_args()
    globals()[arguments.phase]()

"""Register six scoped native232 paragraph contexts without repair expansion."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proof = ROOT / 'evidence/business-map-232/paragraph-acceptance-r1/audit.json'
    audit = json.loads(proof.read_text())
    assert audit['native_executions'] == 68 and all(r['three_families_agree'] for r in audit['cases'])
    for name, digest in audit['sources'].items():
        assert sha(ROOT / name) == digest, name
    refs = {proof.relative_to(ROOT).as_posix(): sha(proof), **audit['sources']}
    implementations = ['scripts/check_document.py', 'scripts/issue_locations.py',
                       'scripts/testvkr-service/checkers/word_format.py',
                       'scripts/testvkr-service/checkers/native_paragraph_counts.py',
                       'scripts/testvkr-service/parsers/docx_parser.py', 'scripts/testvkr-service/parsers/style_resolver.py',
                       'scripts/testvkr-service/config.py']
    impl = {name: sha(ROOT / name) for name in implementations}
    path = ROOT / 'scripts/testvkr-service/rules/rules_verified.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    for rule_id in ['Word.LeftIndentInvalid', 'Word.RightIndentInvalid', 'Word.LineSpacingInvalid']:
        rule = next((r for r in data['rules'] if r['rule_id'] == rule_id), None)
        if rule is None:
            rule = {'rule_id':rule_id,'confidence':'low','verification_status':'pending_original_program_comparison',
                    'verified_formats':[],'verified_work_types':[],'source_va':None}
            data['rules'].append(rule)
        rule.setdefault('observed_message',None)
        contexts = {}
        for mode in ['master', 'phd']:
            contexts['docx:' + mode] = {
                'verification_status': 'verified_against_original', 'confidence': 'high',
                'threshold_origin': 'native232_paragraph_activation_float32_and_trunc_branches',
                'verification_evidence_sha256': sha(proof), 'evidence_refs': list(refs), 'evidence_hashes': refs,
                'implementation_hashes': impl, 'verified_policy': {},
                'scope': {'build': 232, 'format': 'docx', 'work_type': mode,
                          'profile': 'native232_plain_docx_paragraphs',
                          'limits': 'Plain resolved paragraphs through1001 paragraphs, tested inherited/direct properties and at most one single-cell table after activation; no fields/math/numbering/complex stories, no new repair permission.'}}
        rule.setdefault('verification_by_build', {})['232'] = contexts
        rule.setdefault('predicate_by_build', {})['232'] = {
            'activation': 'Exact normalized marker or native paragraph list ordinal>60; empty paragraphs count.',
            'left_right': 'float32(raw_twips * float32(0.017638888210058212)) < float32(-0.1)',
            'line': 'Trunc(resolved_float32 * float32(56.69291305541992) +0.5) <180',
            'text_gate': 'Nonempty native trimmed paragraph text; no arbitrary40-character minimum.',
            'report': 'Selected paragraph count>0; native wording does not define the predicate.'}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'new_contexts': 6, 'rule_ids': len(data['rules'])}))


if __name__ == '__main__':
    main()

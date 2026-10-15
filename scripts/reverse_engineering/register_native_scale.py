"""Register four native232 scale detection contexts, never repair actions."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proof=ROOT/'evidence/business-map-232/scale-audit-r1/audit.json'
    audit=json.loads(proof.read_text())
    assert audit['status']=='passed_native232_scale_branch_counter_report_and_run_audit'
    assert audit['native_executions']==52 and audit['unique_inputs']==26
    assert audit['native_modes']=={'master':26,'phd':26}
    for name,digest in audit['sources'].items():
        assert sha(ROOT/name)==digest,name
    refs={proof.relative_to(ROOT).as_posix():sha(proof),**audit['sources']}
    implementations=['scripts/check_document.py','scripts/issue_locations.py',
        'scripts/testvkr-service/checkers/word_format.py','scripts/testvkr-service/checkers/native_scale_counts.py',
        'scripts/testvkr-service/checkers/native_font_counts.py','scripts/testvkr-service/checkers/native_paragraph_counts.py',
        'scripts/testvkr-service/parsers/docx_parser.py','scripts/testvkr-service/parsers/style_resolver.py','scripts/testvkr-service/config.py']
    impl={name:sha(ROOT/name) for name in implementations}
    path=ROOT/'scripts/testvkr-service/rules/rules_verified.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    for rule_id in ['Word.FontScaleTooSmall','Word.FontScaleTooLarge']:
        rule=next(r for r in data['rules'] if r['rule_id']==rule_id)
        contexts={}
        for mode in ['master','phd']:
            contexts['docx:'+mode]={'verification_status':'verified_against_original','confidence':'high',
                'threshold_origin':'native232_scale_integer_activation_UTF16_counter_and_report_branches',
                'verification_evidence_sha256':sha(proof),'evidence_refs':list(refs),'evidence_hashes':refs,
                'implementation_hashes':impl,'verified_policy':{'FONT_SCALE_MIN_PCT':70.0,'FONT_SCALE_MAX_PCT':130.0,'FONT_VIOLATION_MIN_CHARS':10},
                'scope':{'build':232,'format':'docx','work_type':mode,'profile':'native232_plain_docx_scale',
                    'limits':'Plain integer-scale DOCX runs with traced activation order, resolved direct/inherited/linked properties; at most one simple single-cell table or one single-paragraph absolute50x50mm VML textbox. Conditional table styles, mixed structures, fields/math/extra stories, PDF and repair are unverified.'}}
        rule.setdefault('verification_by_build',{})['232']=contexts
        rule.setdefault('predicate_by_build',{})['232']={'ordinary_small':'30<integer_percent<70',
            'tiny_unreported_bucket':'1<integer_percent<=30','ignored_small':'integer_percent<=1',
            'large':'integer_percent>130; no font-size textbox prior100 gate',
            'report':'UTF16 units including whitespace >10','activation':'Run classification precedes paragraph-end activation; native font activation order is shared.'}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'registered_contexts':4,'rule_ids':len(data['rules'])}))


if __name__=='__main__':
    main()

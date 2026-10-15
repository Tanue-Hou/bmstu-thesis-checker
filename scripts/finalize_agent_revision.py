"""Publish anonymous source-bound progress; retain individual private decisions locally."""
import json,hashlib,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT.parent/'private_trials/2026-10-15'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'evidence/agent-v027'
    decisions=json.loads((PRIVATE/'adjudication-pass1/summary.private.json').read_text(encoding='utf-8'))
    records=json.loads((PRIVATE/'results_adjudication_v027/summary.private.json').read_text(encoding='utf-8'))
    assert len(records)==17 and all(r['status']=='checked' and r['source_unchanged'] for r in records)
    old=PRIVATE/'results_build232_final';new=PRIVATE/'results_adjudication_v027';differences=[]
    for record in records:
        a=json.loads((old/(record['id']+'.report.private.json')).read_text(encoding='utf-8'))
        b=json.loads((new/(record['id']+'.report.private.json')).read_text(encoding='utf-8'))
        from collections import Counter
        before=Counter(f['rule_id'] for f in a['findings']);after=Counter(f['rule_id'] for f in b['findings'])
        differences.append({'removed':dict(before-after),'added':dict(after-before)})
    assert sum(sum(d['removed'].values()) for d in differences)==13
    assert all(set(d['removed'])<={'Graduate.WorkNameInvalid'} and not d['added'] for d in differences)
    summary={'original_review_rows':decisions['rows'],'dispositions':decisions['dispositions'],
             'school_compliance_fully_adjudicated':False,'accuracy':None,'cases_rechecked':17,
             'before_candidate_groups':218,'after_candidate_groups':sum(r['findings'] for r in records),
             'removed_confirmed_recognition_defects':13,'originals_unchanged':True,'build232_repair_open':False,
             'limits':'Evidence dispositions are not final school compliance verdicts; 164 require further clause/source/page review. No private identifiers or source hashes are published.'}
    (out/'review-progress.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    manifest={}
    for folder in ['adjudication-pass1','results_adjudication_v027','cross_adjudication_v027']:
        for p in (PRIVATE/folder).rglob('*'):
            if p.is_file():manifest[str(p.relative_to(PRIVATE))]={'sha256':sha(p),'bytes':p.stat().st_size}
    (PRIVATE/'adjudication-v027-evidence.private.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary))
if __name__=='__main__':main()

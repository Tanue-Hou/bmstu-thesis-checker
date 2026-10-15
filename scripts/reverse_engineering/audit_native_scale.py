"""Audit actual native scale branches against the independent CLI model."""
import argparse
import hashlib
import json
import sys
from argparse import Namespace
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from check_document import check_file,parse_document
from checkers.native_scale_counts import count_scale_candidates
from native_reference_cli import validate_native_run


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.absolute();out.mkdir(exist_ok=False)
    base=ROOT/'evidence/business-map-232';sources={};rows=[]
    for folder in ['scale-native-r1','scale-inheritance-native-r1','scale-phd-native-r1']:
        matrix=base/folder/'matrix.json';sources[matrix.relative_to(ROOT).as_posix()]=sha(matrix)
        for row in json.loads(matrix.read_text())['cases']:
            source=ROOT/row['input'];directory=ROOT/row['evidence_directory']
            assert sha(source)==row['sha256']
            trace=json.loads((directory/'trace.json').read_text())
            native=validate_native_run(trace,(directory/'native-result.txt').read_bytes().decode('utf-8'),row['work_type'],'docx',row['sha256'],True)
            args=Namespace(work_type=row['work_type'],native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False)
            report=check_file(source,args);obs=report['native_scale_observations'];hits=trace['breakpoint_hits']
            assert obs['profile_supported'],row['case']
            counts=obs['counters'];found={f['rule_id']:f for f in report['findings']}
            for bucket in ['small','tiny','large']:
                assert counts[bucket]==row['scale_state'][bucket+'_count'],(row['case'],bucket,counts,row['scale_state'])
                assert sum(h['scale_state']['text']['length'] for h in hits if h['label']=='scale_'+bucket+'_add')==counts[bucket]
            for bucket,rule,phrase in [('small','Word.FontScaleTooSmall','масштаб шрифта меньше 70%'),('large','Word.FontScaleTooLarge','масштаб шрифта больше 130%')]:
                triggered=counts[bucket]>10
                assert (rule in found)==triggered==any(phrase in n['message'] for n in native),(row['case'],rule,native)
                assert triggered==any(h['label']=='scale_'+bucket+'_report_emit' for h in hits)
                if triggered:
                    locations=found[rule]['precise_locations']['occurrences']
                    assert sum(l['utf16_units'] for l in locations)==counts[bucket]
                    assert all(l['native_font_enabled'] and l['part']=='word/document.xml' and l['run_xml_path'] for l in locations)
            _,data=parse_document(source);_,records=count_scale_candidates(data)
            run_hits=[h['font_state'] for h in hits if h['label']=='font_run_state']
            assert len(run_hits)<256,'All scale cases require complete run sampling'
            actual=Counter((h['scale_pct'],h['text']['length'],h['text']['prefix'],bool(h['enabled_flag']),h['textbox_gate_f0']!=0)
                           for h in run_hits if h['text']['length'])
            expected=Counter((r['scale_pct'],r['utf16_units'],r['text'],r['native_font_enabled'],r['role']=='textbox') for r in records if r['text'])
            assert actual==expected,(row['case'],actual,expected)
            rows.append({**row,'local_scale_counters':counts,'both_diagnostic_families_match':True,'all_run_states_match':True})
            for path in [source,*directory.iterdir()]:
                if path.is_file():sources[path.relative_to(ROOT).as_posix()]=sha(path)
    for path in (base/'scale-function-map-r1').iterdir():
        if path.is_file():sources[path.relative_to(ROOT).as_posix()]=sha(path)
    result={'status':'passed_native232_scale_branch_counter_report_and_run_audit','native_executions':len(rows),
            'unique_inputs':len({r['sha256'] for r in rows}),
            'native_modes':{m:sum(r['work_type']==m for r in rows) for m in ['master','phd']},
            'cases':rows,'sources':sources,'repair_permission_expanded':False,
            'limits':['Synthetic plain DOCX controls only; real-paper accuracy is not implied.',
                      'No PDF scale, complex stories, fields/math/conditional table styles or new repair permission.',
                      'Tiny2..30 and ignored<=1 observations are not ordinary small-scale reports.',
                      'First-line-indent producer is still unresolved; separate static search evidence is not proof of absence.']}
    (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ['status','native_executions','unique_inputs','native_modes']}))


if __name__=='__main__':
    main()

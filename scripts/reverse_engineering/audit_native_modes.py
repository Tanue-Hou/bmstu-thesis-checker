"""Recompute retained mode/format evidence and bounded historical comparisons."""
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from native_reference_cli import validate_native_run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(s):return re.sub(r'\s+',' ',re.sub(r'^.*?(?=1\.|\u0417\u0430\u043c\u0435\u0447\u0430\u043d\u0438\u0439 \u043d\u0435\u0442\.)','',s,flags=re.S)).strip()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'evidence/business-map-232/native-modes-audit-r1');a=p.parse_args()
 base=ROOT/'evidence/business-map-232';rows=[]
 for suite in ['native-modes-r1','native-complex-phd-r1']:
  folder=base/suite;matrix=json.loads((folder/'matrix.json').read_text(encoding='utf-8'))
  for row in matrix['cases']:
   d=folder/row['case'];report=json.loads((d/'report.json').read_text(encoding='utf-8'));trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));text=(d/'native-result.txt').read_bytes().decode('utf-8')
   source=ROOT/report['source_fixture'];assert sha(source)==row['input_sha256']==report['source_sha256']==trace['probe_document']['sha256']
   assert sha(d/'trace.json')==report['trace_sha256'] and sha(d/'native-result.txt')==report['native_text_sha256']
   assert sha(d/'sender-source.cs.txt')==report['sender_source_sha256']==trace['probe_document']['sender_source_sha256']
   assert sha(d/'tracer-source.py.txt')==trace['tracer_sha256']
   diagnostics=validate_native_run(trace,text,row['work_type'],row['file_type']);assert len(diagnostics)==row['diagnostic_count']
   state=next(h['volume_state'] for h in trace['breakpoint_hits'] if h['label']=='volume_decision')
   item=dict(row,native_state=state,validated_report=True)
   comparison=source.parent/'comparison.json'
   if comparison.exists() and row['work_type']=='phd':
    historical=json.loads(comparison.read_text(encoding='utf-8')).get('cases',{}).get(source.stem)
    if historical:
     capture=source.with_suffix('.original.json')
     assert historical['input_sha256']==sha(source) and historical['capture_sha256']==sha(capture)
     old_capture=json.loads(capture.read_text(encoding='utf-8'));assert '230' in old_capture['window']['title']
     item['historical_build230_comparison']={'same_input_and_mode':historical['work_type']==row['work_type'],'diagnostic_count':len(re.findall(r'(?:^|\s)\d+\.\s',historical['original_text'])),'normalized_full_diagnostics_equal':normalize(text)==normalize(historical['original_text']),'capture_sha256':sha(capture)}
   rows.append(item)
 result={'status':'passed_retained_native_mode_audit','cases':rows,'limits':['Finite synthetic fixtures, instrumented native232 only.','Historical230 equality is per input; not full version equivalence.','No new repair permissions or school-standard claims.']}
 out=a.out.absolute();out.mkdir(exist_ok=False);(out/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'cases':len(rows),'historical_pairs':sum('historical_build230_comparison' in r for r in rows)}))
if __name__=='__main__':main()

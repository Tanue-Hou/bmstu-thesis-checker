"""Audit font producer branches, UTF16 counters, report gates and reconstruction."""
import argparse,hashlib,json,re,sys
from pathlib import Path
from argparse import Namespace
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import check_file
from native_reference_cli import validate_native_run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);base=ROOT/'evidence/business-map-232';rows=[];sources={}
 for folder in ['font-native-r1','font-native-r2','font-inheritance-native-r1','font-phd-native-r1']:
  matrix=base/folder/'matrix.json';sources[matrix.relative_to(ROOT).as_posix()]=sha(matrix)
  for row in json.loads(matrix.read_text())['cases']:
   source=ROOT/row['input'];d=ROOT/row['evidence_directory'];trace=json.loads((d/'trace.json').read_text());assert sha(source)==row['sha256'];native=validate_native_run(trace,(d/'native-result.txt').read_bytes().decode('utf-8'),row['work_type'],'docx',sha(source),True);hits=trace['breakpoint_hits']
   report=check_file(source,Namespace(work_type=row['work_type'],native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False));obs=report['native_word_observations'];assert obs['profile_supported'];counts=obs['font_counters'];expected=row['font_state'];found={f['rule_id']:f for f in report['findings']}
   for bucket in ['small','tiny','large']:
    assert counts[bucket]==expected[bucket+'_count'],(row['case'],bucket,counts,expected)
    assert sum(h['font_state']['text']['length'] for h in hits if h['label']=='font_'+bucket+'_add')==counts[bucket]
   for bucket,rule,phrase in [('small','Word.FontSizeTooSmall','размер которых меньше 8'),('large','Word.FontSizeTooLarge','размер которых превышает 18')]:
    emit=counts[bucket]>10;assert (rule in found)==emit==any(phrase in diag['message'] for diag in native)==any(h['label']=='font_'+bucket+'_report_emit' for h in hits)
    if emit:assert sum(l['utf16_units'] for l in found[rule]['precise_locations']['occurrences'])==counts[bucket]
   assert sum(h['label']=='font_run_state' for h in hits)<256
   rows.append({**row,'local_font_counters':counts,'both_font_families_agree':True,'font_run_hits':sum(h['label']=='font_run_state' for h in hits)})
   for f in [source,*d.iterdir()]:
    if f.is_file():sources[f.relative_to(ROOT).as_posix()]=sha(f)
 assert len(rows)==29 and sum(r['work_type']=='master' for r in rows)==21
 (out/'audit.json').write_text(json.dumps({'status':'passed_native232_font_counter_role_and_inheritance_audit','cases':rows,'sources':sources,'limits':['Twenty-one master and eight NKR DOCX executions; PDF and other modes unverified.','Ordinary text, single-cell table and one simple VML textbox with at most two runs.','Tiny bucket is observed but not assigned a new native diagnostic. Detection evidence does not expand repair permission.']},indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'native_cases':len(rows),'both_families_agree':True}))
if __name__=='__main__':main()

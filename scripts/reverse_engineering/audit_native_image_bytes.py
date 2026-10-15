"""Recompute raw-header, native-branch and local-rule agreement for image bytes."""
import hashlib,json,sys,zipfile
from argparse import Namespace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from check_document import check_file
from native_reference_cli import validate_native_run
from verify_native_pixels import publish
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'evidence/business-map-232';matrix_path=base/'image-bytes-boundaries-r1/matrix.json';matrix=json.loads(matrix_path.read_text(encoding='utf-8'));out=base/'image-bytes-audit-r1';out.mkdir(exist_ok=False)
 descriptor=out/'descriptor';report=publish(ROOT.parent/'private_trials/native-reference/image-bytes-descriptor-r1',descriptor)
 rows=matrix['cases']+[{'case':'descriptor','input':'evidence/business-map-232/image-bytes-boundaries-r1/inputs/descriptor.docx','input_sha256':report['source_sha256'],'evidence_directory':descriptor.relative_to(ROOT).as_posix()}];verified=[];sources={matrix_path.relative_to(ROOT).as_posix():sha(matrix_path)}
 for row in rows:
  source=ROOT/row['input'];d=ROOT/row['evidence_directory'];trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));text=(d/'native-result.txt').read_bytes().decode('utf-8');assert sha(source)==row['input_sha256']
  diagnostics=validate_native_run(trace,text,'phd','docx',sha(source),True)
  raw=source.read_bytes();entries=[]
  with zipfile.ZipFile(source) as z:
   assert z.testzip() is None
   for info in z.infolist():
    if info.filename.startswith('word/media/'):
     header=raw[info.header_offset:info.header_offset+30];assert header[:4]==b'PK\x03\x04';entries.append({'entry':info.filename,'local_size':int.from_bytes(header[22:26],'little'),'central_size':info.file_size,'compressed_size':info.compress_size,'flags':int.from_bytes(header[6:8],'little')})
  comparisons=[h['image_bytes_state']['size_unsigned32'] for h in trace['breakpoint_hits'] if h['label']=='image_bytes_compare'];assert sorted(comparisons)==sorted(e['local_size'] for e in entries)
  expected=sum(e['local_size']>30000000 for e in entries);counter=next(h['image_bytes_counter'] for h in trace['breakpoint_hits'] if h['label']=='image_bytes_report_gate');assert counter==expected==sum(h['label']=='image_bytes_emit' for h in trace['breakpoint_hits'])
  assert bool([d for d in diagnostics if '40 Mb' in d['message']])==bool(expected)
  local=check_file(source,Namespace(work_type='phd',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False));findings=[f for f in local['findings'] if f['rule_id']=='Pic.FileSizeTooLarge'];assert bool(findings)==bool(expected)
  if findings:assert findings[0]['threshold']['count_images']==expected and findings[0]['precise_locations']['occurrence_count']==expected
  legacy=check_file(source,Namespace(work_type='phd',native_build=230,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False));old=bool([f for f in legacy['findings'] if f['rule_id']=='Pic.FileSizeTooLarge'])
  verified.append({'case':row['case'],'input':row['input'],'input_sha256':sha(source),'entries':entries,'observed_sizes':comparisons,'native_counter':counter,'local_native_predicate_agree':True,'legacy_local_40MiB_sum_finding':old,'legacy_local_differs_from_native232':old!=bool(expected),'evidence_directory':row['evidence_directory']})
  for p in [source,d/'trace.json',d/'native-result.txt',d/'tracer-source.py.txt',d/'sender-source.cs.txt']:sources[p.relative_to(ROOT).as_posix()]=sha(p)
 result={'status':'passed_native232_docx_image_bytes_audit','native_build':232,'rule_id':'Pic.FileSizeTooLarge','cases':verified,'sources':sources,'predicate':{'per_entry_local_zip_header_uncompressed_size':True,'threshold_bytes':30000000,'comparison':'unsigned_strict_greater','native_message':'40 Mb','report_counter_offset':'0x90','native_compare_va':'00438dd8','native_emit_va':'00438ddf','local_header_read_va':'0044405a','report_gate_va':'0047c5e7'},'limits':['Five synthetic NKR DOCX inputs, ordinary RGB8 PNGs, one/two inline images, flags0/8.','No forged ZIP sizes or malformed-header interventions. Error sentinelffffffff, ZIP64, vector paths and other modes remain unverified.','Legacy comparison is local230 policy, not original230 behavior. No image repair permission.']}
 (out/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'cases':len(verified),'legacy_local_differences':sum(r['legacy_local_differs_from_native232'] for r in verified)}))
if __name__=='__main__':main()

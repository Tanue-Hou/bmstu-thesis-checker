"""Retain final default-wrapper image counter and conversion observations."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from native_reference_cli import validate_native_run
from verify_native_pixels import publish
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'evidence/business-map-232/pixel-final-r1';out.mkdir(exist_ok=False);rows=[]
 for private_name,kind,expected in [('pixel-final-equal-r1','docx',0),('pixel-final-above-docx-r1','docx',1),('pixel-final-above-pdf-r1','pdf',1)]:
  dest=out/private_name;report=publish(ROOT.parent/'private_trials/native-reference'/private_name,dest);trace=json.loads((dest/'trace.json').read_text(encoding='utf-8'));text=(dest/'native-result.txt').read_bytes().decode('utf-8')
  diagnostics=validate_native_run(trace,text,'phd',kind,report['source_sha256'],True);assert trace['cleanup_verified']
  counter=next(h['pixel_counter_state']['count'] for h in trace['breakpoint_hits'] if h['label']=='image_counter_report_gate');assert counter==expected
  if kind=='docx':assert next(h['pixel_output_flag'] for h in trace['breakpoint_hits'] if h['label']=='docx_image_flag_result')==expected
  assert sha(dest/'tracer-source.py.txt')==sha(ROOT/'scripts/reverse_engineering/trace_startup_windows.py')==trace['tracer_sha256']
  rows.append({'case':private_name,'file_type':kind,'source_sha256':report['source_sha256'],'counter':counter,'native_diagnostic_count':len(diagnostics),'cleanup_verified':True,'pixel_fix_default_enabled':report['pixel_unit_codepage_fix_enabled']})
 (out/'receipt.json').write_text(json.dumps({'status':'passed_final_default_pixel_wrapper','cases':rows,'limits':'Only these default-wrapper cases and explicit process-local conversion interventions.'},indent=2),encoding='utf-8');print(json.dumps({'final_cases':len(rows)}))
if __name__=='__main__':main()

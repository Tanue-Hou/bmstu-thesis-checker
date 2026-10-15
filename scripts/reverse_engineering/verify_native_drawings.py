"""Execute each public drawing probe and retain original branches/counters."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_native_pixels import publish
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--cases',nargs='*');p.add_argument('--inputs',type=Path,default=ROOT/'evidence/business-map-232/drawing-probes-r1/inputs.json');a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);inputs=a.inputs.absolute();data=json.loads(inputs.read_text(encoding='utf-8'));rows=[]
 for row in data['cases']:
  if a.cases and row['case'] not in a.cases:continue
  source=ROOT/row['input'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
  run=subprocess.run([sys.executable,str(ROOT/'scripts/native_reference_cli.py'),'--trace-drawings','--work-type','phd','--input',str(source)],capture_output=True,timeout=55);report=json.loads(run.stdout);assert run.returncode==0,report
  d=out/row['case'];publish(Path(report['evidence_directory']),d);trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));labels={h['label'] for h in trace['breakpoint_hits']};state=next(h['drawing_state'] for h in trace['breakpoint_hits'] if h['label']=='drawing_report_state')
  result={**row,'drawing_state':state,'floating_image_emit':'floating_image_emit' in labels,'small_labels_emit':'small_labels_emit' in labels,'native_diagnostic_count':report['diagnostic_count'],'evidence_directory':d.relative_to(ROOT).as_posix()};rows.append(result);print(json.dumps(result),flush=True)
 (out/'matrix.json').write_text(json.dumps({'native_build':232,'work_type':'phd','cases':rows,'limits':['Synthetic VML label and DrawingML anchor cases; no general-shape or PDF equivalence claim.']},indent=2),encoding='utf-8')
if __name__=='__main__':main()

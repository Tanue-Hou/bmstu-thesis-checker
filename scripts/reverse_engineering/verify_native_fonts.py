"""Execute font probes, retaining original branches, runs and final counters."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from verify_native_pixels import publish
def main():
 p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--cases',nargs='*');p.add_argument('--work-type',choices=['master','phd'],default='master');a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);rows=[]
 for row in json.loads(a.inputs.absolute().read_text())['cases']:
  if a.cases and row['case'] not in a.cases:continue
  source=ROOT/row['input'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256'];run=subprocess.run([sys.executable,str(ROOT/'scripts/native_reference_cli.py'),'--trace-fonts','--work-type',a.work_type,'--input',str(source)],capture_output=True,timeout=55);report=json.loads(run.stdout);assert run.returncode==0,report;d=out/row['case'];publish(Path(report['evidence_directory']),d);trace=json.loads((d/'trace.json').read_text());hits=trace['breakpoint_hits'];state=next(h['font_report_state'] for h in hits if h['label']=='font_small_report_gate')
  result={**row,'work_type':a.work_type,'font_state':state,'small_branch_hits':sum(h['label']=='font_small_add' for h in hits),'tiny_branch_hits':sum(h['label']=='font_tiny_add' for h in hits),'large_branch_hits':sum(h['label']=='font_large_add' for h in hits),'native_diagnostic_count':report['diagnostic_count'],'evidence_directory':d.relative_to(ROOT).as_posix()};rows.append(result);print(json.dumps(result),flush=True)
 (out/'matrix.json').write_text(json.dumps({'native_build':232,'work_type':a.work_type,'cases':rows},indent=2)+'\n',encoding='utf-8',newline='\n')
if __name__=='__main__':main()

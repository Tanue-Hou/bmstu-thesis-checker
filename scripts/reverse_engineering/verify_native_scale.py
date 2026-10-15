"""Retain scale producer branches and report gates on exact synthetic inputs."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from verify_native_pixels import publish
from native_reference_cli import validate_native_run


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--work-type',choices=['master','phd'],default='master')
    p.add_argument('--cases',nargs='*')
    p.add_argument('--seed',type=Path,help='Reuse one completed exact source/mode capture instead of rerunning it.')
    a = p.parse_args()
    out = a.out.absolute()
    out.mkdir(exist_ok=False)
    rows = []
    seed = json.loads((a.seed/'report.json').read_text()) if a.seed else None
    for row in json.loads(a.inputs.absolute().read_text())['cases']:
        if a.cases and row['case'] not in a.cases:
            continue
        source = ROOT/row['input']
        assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
        if seed and seed['source_sha256']==row['sha256'] and seed['work_type']==a.work_type:
            private = a.seed.absolute()
        else:
            result = subprocess.run([sys.executable,str(ROOT/'scripts/native_reference_cli.py'),
                '--trace-scale','--work-type',a.work_type,'--input',str(source)],capture_output=True,timeout=55)
            assert result.returncode==0,(result.stdout+result.stderr).decode(errors='replace')
            private = Path(json.loads(result.stdout)['evidence_directory'])
        directory = out/row['case']
        report = publish(private,directory)
        trace = json.loads((directory/'trace.json').read_text())
        validate_native_run(trace,(directory/'native-result.txt').read_bytes().decode('utf-8'),a.work_type,'docx',row['sha256'],True)
        hits = trace['breakpoint_hits']
        gates = [h for h in hits if h['label'] in {'scale_small_report_gate','scale_large_report_gate'}]
        assert len(gates)==2
        state = gates[0]['scale_report_state']
        assert gates[1]['scale_report_state']==state
        item = {**row,'work_type':a.work_type,'scale_state':state,
            'branch_hits':{bucket:sum(h['label']=='scale_'+bucket+'_add' for h in hits) for bucket in ['small','tiny','large']},
            'emit_labels':[h['label'] for h in hits if h['label'].startswith('scale_') and h['label'].endswith('_emit')],
            'native_diagnostic_count':report['diagnostic_count'],'evidence_directory':directory.relative_to(ROOT).as_posix()}
        rows.append(item)
        (out/'matrix.json').write_text(json.dumps({'native_build':232,'cases':rows},indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({'case':row['case'],'work_type':a.work_type,'scale_state':state}),flush=True)


if __name__=='__main__':
    main()

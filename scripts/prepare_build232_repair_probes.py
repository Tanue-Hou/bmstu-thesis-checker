"""Prepare experimental copies using historical machinery; NOT repair validation."""
import hashlib,json,shutil
from pathlib import Path
from repair_document import repair_copy
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'evidence/agent-v027/repair-probes'
    out.mkdir(parents=True,exist_ok=False)
    staging=Path('D:/TestVkrCases20261015')
    records=[]
    for original,id in [('Z01','R01'),('Z04','R02')]:
        source=ROOT/'evidence/build-232/controls'/(original+'.docx')
        result=repair_copy(source,out,actions=['font_size_anomalies'],body_font_pt=14,work_type='master',native_build=230)
        destination=out/(id+'.docx');shutil.copyfile(result['output_file'],destination)
        shutil.copyfile(destination,staging/destination.name)
        records.append({'id':id,'source_control':original,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'copy_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'changes':len(result['changes']),'scope':'Experimental candidate generated with historical230 repair; native232 validation pending'})
    (out/'inputs.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    print(json.dumps(records))
if __name__=='__main__':main()

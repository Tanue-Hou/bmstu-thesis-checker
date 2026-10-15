"""Controlled valid PNGs padded after IEND: actual ZIP entry size boundaries."""
import argparse,hashlib,json,subprocess,sys,zipfile
from io import BytesIO,UnsupportedOperation
from pathlib import Path
from docx import Document
from docx.shared import Cm
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_native_pixels import publish
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Streaming(BytesIO):
 def seekable(self):return False
 def seek(self,*args):raise UnsupportedOperation('Streaming ZIP writer')
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(parents=True,exist_ok=False);inputs=out/'inputs';inputs.mkdir();rows=[]
 parent=ROOT/'evidence/format-expansion/complex_clean.docx'
 with zipfile.ZipFile(parent) as z:png=z.read('word/media/image1.png')
 for name,sizes in [('below',[29999999]),('equal',[30000000]),('above',[30000001]),('aggregate',[22000000,22000000]),('descriptor',[30000001])]:
  source=inputs/(name+'.docx');seed=parent
  if len(sizes)==2:
   d=Document(parent);d.add_picture(BytesIO(png+b'\0'),width=Cm(12));seed=inputs/'aggregate-seed.docx';d.save(seed)
  entries={}
  with zipfile.ZipFile(seed) as src,zipfile.ZipFile(source,'w') as dst:
   for info in src.infolist():
    payload=src.read(info.filename)
    if info.filename.startswith('word/media/'):
     index=len(entries);assert index<len(sizes)
     payload=png+b'\0'*(sizes[index]-len(png)-1)+bytes([index]);entries[info.filename]=len(payload)
    dst.writestr(info,payload)
  assert len(entries)==len(sizes)
  if name=='descriptor':
   stream=Streaming()
   with zipfile.ZipFile(source) as src,zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as dst:
    for info in src.infolist():dst.writestr(info,src.read(info.filename))
   source.write_bytes(stream.getvalue())
  run=subprocess.run([sys.executable,str(ROOT/'scripts/native_reference_cli.py'),'--input',str(source),'--work-type','phd','--trace-image-bytes'],capture_output=True,timeout=55)
  report=json.loads(run.stdout);assert run.returncode==0,report;dest=out/name;report=publish(Path(report['evidence_directory']),dest)
  trace=json.loads((dest/'trace.json').read_text(encoding='utf-8'));hits=trace['breakpoint_hits'];observed=[h['image_bytes_state']['size_unsigned32'] for h in hits if h['label']=='image_bytes_compare']
  counter=next((h['image_bytes_counter'] for h in hits if h['label']=='image_bytes_report_gate'),None)
  row={'case':name,'input':source.relative_to(ROOT).as_posix(),'input_sha256':sha(source),'parent_sha256':sha(parent),'actual_image_entry_sizes':entries,'observed_sizes':observed,'emitted_branches':sum(h['label']=='image_bytes_emit' for h in hits),'report_counter':counter,'diagnostic_count':report['diagnostic_count'],'diagnostics':report['diagnostics'],'zip_bytes':source.stat().st_size,'evidence_directory':dest.relative_to(ROOT).as_posix()};rows.append(row);print(json.dumps(row,ensure_ascii=True),flush=True)
 (out/'matrix.json').write_text(json.dumps({'native_build':232,'cases':rows,'limits':['Synthetic valid PNGs padded after IEND; no forged ZIP sizes or malformed-header interventions.','Native file parser and declared ZIP size values must both be checked before promoting a predicate.']},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()

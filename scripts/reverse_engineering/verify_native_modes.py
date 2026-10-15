"""Run public fixtures against the original 232 checker; retain full receipts.

Historical 230 captures are comparison context, never 232 acceptance truth.
"""
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CASES=[
 ('phd_heading','graduate-structure/g_phd_correct_heading.docx','phd'),
 ('phd_left25','graduate-structure/g_phd_left25.docx','phd'),
 ('master_complex','v028/complex-repair/C01A.docx','master'),
 ('phd_pdf_clean','multipage-phd-repair/mp_clean.pdf','phd'),
 ('phd_pdf_font72','multipage-phd-repair/mp_font72.pdf','phd'),
 ('phd_pdf_structure','multipage-phd-repair/structure_clean.pdf','phd'),
 ('phd_pdf_no_abstract','multipage-phd-repair/structure_no_abstract.pdf','phd'),
 ('master_pdf_clean','multipage-phd-repair/mp_clean.pdf','master'),
]
COMPLEX_CASES=[
 ('phd_complex_clean','format-expansion/complex_clean.docx','phd'),
 ('phd_complex_table7','format-expansion/complex_table7.docx','phd'),
 ('phd_complex_image','format-expansion/complex_image_above.docx','phd'),
 ('phd_combined','multipage-phd-repair/phd_combined.docx','phd'),
]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--suite',choices=['modes','complex'],default='modes');a=p.parse_args()
 out=a.out.absolute();out.mkdir(parents=True,exist_ok=False)
 rows=[]
 for name,relative,mode in (CASES if a.suite=='modes' else COMPLEX_CASES):
  source=ROOT/'evidence'/relative
  command=[sys.executable,str(ROOT/'scripts/native_reference_cli.py'),'--input',str(source),'--work-type',mode]
  run=subprocess.run(command,capture_output=True,timeout=55)
  report=json.loads(run.stdout)
  if run.returncode:raise RuntimeError(name+': '+str(report))
  private=Path(report['evidence_directory']);dest=out/name;dest.mkdir()
  for f in ['trace.json','native-result.txt','collection-length.txt','selected-mode.txt','tracer-source.py.txt']:
   shutil.copyfile(private/'native'/f,dest/f)
  shutil.copyfile(private/'sender-source.cs.txt',dest/'sender-source.cs.txt')
  report['evidence_directory']=str(dest.relative_to(ROOT));report['source_fixture']='evidence/'+relative
  (dest/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
  rows.append({'case':name,'work_type':mode,'file_type':source.suffix[1:],'input_sha256':sha(source),'diagnostic_count':report['diagnostic_count'],'report':str((dest/'report.json').relative_to(ROOT))})
  print(json.dumps(rows[-1]),flush=True)
 (out/'matrix.json').write_text(json.dumps({'native_build':232,'cases':rows,'limits':['Instrumented original, not an independent replica.','Public synthetic fixtures only; no school-standard inference.']},indent=2),encoding='utf-8')
if __name__=='__main__':main()

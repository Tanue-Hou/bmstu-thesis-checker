"""Native232 PNG boundary / branch / codepage experiments on public fixtures."""
import argparse,hashlib,json,re,shutil,subprocess,sys,zipfile
from io import BytesIO
from pathlib import Path
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from native_reference_cli import validate_native_run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\s+',' ',re.sub(r'^.*?(?=1\.|Замечаний нет\.)','',s,flags=re.S)).strip()
def publish(private,dest):
 dest.mkdir()
 for f in ['trace.json','native-result.txt','collection-length.txt','selected-mode.txt','tracer-source.py.txt']:shutil.copyfile(private/'native'/f,dest/f)
 shutil.copyfile(private/'sender-source.cs.txt',dest/'sender-source.cs.txt')
 report=json.loads((private/'report.json').read_text(encoding='utf-8'));report['evidence_directory']=dest.relative_to(ROOT).as_posix()
 (dest/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 return report
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(parents=True,exist_ok=False)
 inputs=out/'inputs';inputs.mkdir();rows=[]
 for width in [3999,4000,4001]:
  buf=BytesIO();Image.new('RGB',(width,4000),'white').save(buf,format='PNG');png=buf.getvalue()
  for kind in ['docx','pdf']:
   name=f'{kind}_{width}x4000';path=inputs/(name+'.'+kind)
   parent=ROOT/'evidence/format-expansion'/('complex_clean.docx' if kind=='docx' else 'pdf_complex_clean.pdf')
   if kind=='docx':
    with zipfile.ZipFile(parent) as src,zipfile.ZipFile(path,'w') as dst:
     for info in src.infolist():dst.writestr(info,png if info.filename=='word/media/image1.png' else src.read(info.filename))
    with zipfile.ZipFile(parent) as src,zipfile.ZipFile(path) as dst:assert [n for n in src.namelist() if src.read(n)!=dst.read(n)]==['word/media/image1.png']
   else:
    with fitz.open(parent) as doc:
     assert len(doc)==1 and len(doc[0].get_images())==1
     doc[0].replace_image(doc[0].get_images()[0][0],stream=png);doc.save(path,garbage=4,deflate=True)
   run=subprocess.run([sys.executable,str(ROOT/'scripts/native_reference_cli.py'),'--input',str(path),'--work-type','phd','--trace-images']+(['--pixel-cp1251'] if width>4000 else []),capture_output=True,timeout=55)
   report=json.loads(run.stdout);assert run.returncode==0,report
   dest=out/name;report=publish(Path(report['evidence_directory']),dest)
   trace=json.loads((dest/'trace.json').read_text(encoding='utf-8'));text=(dest/'native-result.txt').read_bytes().decode('utf-8')
   diagnostics=validate_native_run(trace,text,'phd',kind,sha(path),width>4000)
   comparisons=[h['pixel_state'] for h in trace['breakpoint_hits'] if h['label']==kind+'_image_area_compare'];assert len(comparisons)==1
   state=comparisons[0];assert state['area_signed32']==width*4000
   if kind=='docx':assert (state['width_px'],state['height_px'])==(width,4000)
   else:assert sorted([state['dimension_1bc'],state['dimension_1c0']])==sorted([width,4000])
   emitted=any(h['label']==('docx_large_image_flag' if kind=='docx' else 'pdf_large_image_emit') for h in trace['breakpoint_hits']);assert emitted==(width>4000)
   image_diagnostics=[d for d in diagnostics if '16000000' in d['message']];assert bool(image_diagnostics)==emitted
   if emitted:assert 'пикселей' in image_diagnostics[0]['message']
   row={'case':name,'input':path.relative_to(ROOT).as_posix(),'input_sha256':sha(path),'parent_sha256':sha(parent),'format':kind,'work_type':'phd','native_build':232,'dimensions':[width,4000],'pixel_state':state,'large_branch_observed':emitted,'native_image_diagnostic_count':len(image_diagnostics),'native_total_diagnostic_count':len(diagnostics),'evidence_directory':dest.relative_to(ROOT).as_posix(),'trace_sha256':sha(dest/'trace.json'),'native_text_sha256':sha(dest/'native-result.txt')}
   rows.append(row);print(json.dumps({'case':name,'large_branch':emitted,'native_diagnostics':len(diagnostics)}),flush=True)
 result={'status':'passed_native_pixel_boundary_experiments','cases':rows,'limits':['Finite RGB PNG fixtures; signed32 multiplication observed, no overflow input executed.','DOCX virtual getter +0x24 is height and +0x30 width on these asymmetric PNGs.','Native232 reference is instrumented; no image repair permission.']}
 (out/'matrix.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()

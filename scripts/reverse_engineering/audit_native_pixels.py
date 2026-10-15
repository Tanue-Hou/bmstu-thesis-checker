"""Verify native image branches, local agreement, and a same-input encoding pair."""
import argparse,hashlib,json,shutil,sys
from argparse import Namespace
from pathlib import Path
import pefile,capstone
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from native_reference_cli import validate_native_run,IDENTITY
from check_document import check_file
from verify_native_pixels import publish,norm
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();base=ROOT/'evidence/business-map-232';out=a.out.absolute();out.mkdir(exist_ok=False)
 matrix=base/'pixel-boundaries-r1/matrix.json';data=json.loads(matrix.read_text(encoding='utf-8'));rows=[];sources={matrix.relative_to(ROOT).as_posix():sha(matrix)}
 for row in data['cases']:
  source=ROOT/row['input'];d=ROOT/row['evidence_directory'];trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));text=(d/'native-result.txt').read_bytes().decode('utf-8')
  assert sha(source)==row['input_sha256'] and sha(d/'trace.json')==row['trace_sha256'] and sha(d/'native-result.txt')==row['native_text_sha256']
  assert sha(d/'tracer-source.py.txt')==trace['tracer_sha256']
  native=validate_native_run(trace,text,'phd',row['format'],sha(source),row['large_branch_observed'])
  local=check_file(source,Namespace(work_type='phd',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False))
  pixels=[f for f in local['findings'] if f['rule_id']=='Pic.PixelSizeTooLarge'];assert bool(pixels)==row['large_branch_observed']
  assert all(f['threshold']['count_images']==row['native_image_diagnostic_count'] for f in pixels)
  rows.append(dict(row,local_pixel_finding_count=len(pixels),local_pixel_image_count=sum(f['threshold']['count_images'] for f in pixels),local_native_pixel_predicate_agrees=True))
  for p in [source,d/'trace.json',d/'native-result.txt',d/'tracer-source.py.txt',d/'sender-source.cs.txt']:sources[p.relative_to(ROOT).as_posix()]=sha(p)
 pair=[]
 for name,fix in [('pixel-control-r1',False),('pixel-treatment-r1',True)]:
  private=ROOT.parent/'private_trials/native-reference'/name;dest=out/name;report=publish(private,dest);trace=json.loads((dest/'trace.json').read_text(encoding='utf-8'));text=(dest/'native-result.txt').read_bytes().decode('utf-8')
  diagnostics=validate_native_run(trace,text,'phd','docx',report['source_sha256'],fix);assert len(diagnostics)==1
  pair.append((trace,text,report))
  for p in dest.iterdir():sources[p.relative_to(ROOT).as_posix()]=sha(p)
 assert pair[0][2]['source_sha256']==pair[1][2]['source_sha256']
 old_literal=next(h['converted_literal']['prefix'] for h in pair[0][0]['breakpoint_hits'] if h['label']=='pixel_literal_return')
 good_literal=bytes.fromhex('20efe8eaf1e5ebe5e9293a20').decode('cp1251');assert old_literal!=good_literal
 assert pair[0][1].replace(old_literal,good_literal)==pair[1][1].replace(pair[1][0]['probe_document']['path'],pair[0][0]['probe_document']['path'])
 historical=ROOT/'evidence/format-expansion/comparison.json';h=json.loads(historical.read_text(encoding='utf-8'))['cases']['complex_image_above'];assert h['input_sha256']==pair[1][2]['source_sha256'] and norm(h['original_text'])==norm(pair[1][1])
 source_capture=ROOT/'evidence/format-expansion/complex_image_above.original.json';assert sha(source_capture)==h['capture_sha256']
 for p in [historical,source_capture]:sources[p.relative_to(ROOT).as_posix()]=sha(p)
 binary=ROOT.parent/'runtime/TestVkr232.exe';assert sha(binary)==IDENTITY
 raw=binary.read_bytes();pe=pefile.PE(data=raw);md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
 assembly=[]
 for va,size in [(0x42ae30,48),(0x472bce,43),(0x47c78a,21)]:
  for ins in md.disasm(raw[pe.get_offset_from_rva(va-0x400000):][:size],va):assembly.append({'va':hex(ins.address),'bytes':ins.bytes.hex(),'instruction':ins.mnemonic+' '+ins.op_str})
 (out/'assembly.json').write_text(json.dumps({'target_sha256':IDENTITY,'instructions':assembly},indent=2),encoding='utf-8');sources[(out/'assembly.json').relative_to(ROOT).as_posix()]=sha(out/'assembly.json')
 result={'status':'passed_bounded_native232_pixel_predicate_and_encoding_audit','target_sha256':IDENTITY,'cases':rows,'same_input_encoding_pair':{'source_sha256':pair[0][2]['source_sha256'],'control_codepage':936,'treatment_codepage':1251,'call_return_va':'005746f5','literal_va':'006e5f6c','literal_hex':'20efe8eaf1e5ebe5e9293a20','only_pixel_unit_changed':True,'treated_full_diagnostics_equal_historical230':True,'limits':'Control snapshot used reversed width/height labels; getter registers/product and flag are authoritative. Final boundary snapshots correct getter24=height/getter30=width.'},'sources':sources,'limits':['Only tested ordinary single RGB8 PNG DOCX and one-page unrotated PDF profile.','No signed-overflow inputs or vector/WMF/JPEG/alpha images validated.','Only detection predicate and pixel-unit conversion; no new repair actions.']}
 (out/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'cases':len(rows),'same_input_encoding_pair':True,'sources':len(sources)}))
if __name__=='__main__':main()

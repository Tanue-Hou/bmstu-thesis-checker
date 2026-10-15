"""Retain small static instruction slices/constants, not the executable."""
import argparse,hashlib,json,struct
from pathlib import Path
import pefile,capstone
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);binary=ROOT.parent/'runtime/TestVkr232.exe';raw=binary.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0'
 pe=pefile.PE(data=raw);cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);slices={}
 for start,end,name in [(0x41a204,0x41a3a2,'vml_unit_conversion'),(0x41d645,0x41d866,'small_label_flags_and_branches'),(0x41d581,0x41d645,'overflow_branch'),(0x41d537,0x41d581,'dimension_bounds_compare'),(0x4389ab,0x438b3d,'shape_selected_geometry_and_bounds')]:
  offset=pe.get_offset_from_rva(start-0x400000);lines=['%08x %s %s'%(i.address,i.mnemonic,i.op_str) for i in cs.disasm(raw[offset:offset+end-start],start)];(out/(name+'.asm')).write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n');slices[name]={'start_va':hex(start),'end_va_exclusive':hex(end),'instruction_count':len(lines)}
 constants={}
 for unit,va,literal_va in [('pt',0x41a3a8,0x6c2bcf),('in',0x41a3ac,0x6c2bd2),('cm',0x41a3b0,0x6c2bd8),('pc',0x41a3b4,0x6c2bdb),('px',0x41a3b8,0x6c2bde)]:
  off=pe.get_offset_from_rva(va-0x400000);lo=pe.get_offset_from_rva(literal_va-0x400000);assert raw[lo:lo+3]==unit.encode()+b'\0';constants[unit]={'va':hex(va),'raw_float32_hex':raw[off:off+4].hex(),'multiplier':struct.unpack('<f',raw[off:off+4])[0]}
 provenance=ROOT/'evidence/agent-v027/decompilation/provenance.json';data=json.loads(provenance.read_text());assert data['target_sha256']==digest
 result={'target_sha256':digest,'slices':slices,'native_unit_constants':constants,'static_decompilation_provenance':{'path':provenance.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(provenance.read_bytes()).hexdigest()},'analyst_names':{'0041a204':'parse_vml_length_with_native_units','0041dee0':'dispatch_vml_or_wps_textbox_content','0041c6ac':'parse_textbox_content_and_update_geometry_diagnostics'},'limits':['Names are analyst interpretations; float constants and branch instructions are static binary observations.','Runtime proof is in textbox-boundaries and textbox-fit-boundaries; no overflow execution proof.','px multiplier is native behavior, not a screen DPI conversion.']}
 result['dimension_bounds_constants']={}
 for va,kind in [(0x6e51e8,'i'),(0x6e51ec,'i'),(0x41dc08,'f'),(0x41dc10,'f'),(0x438eb4,'f'),(0x438eb8,'f')]:
  off=pe.get_offset_from_rva(va-0x400000);result['dimension_bounds_constants'][hex(va)]={'raw_hex':raw[off:off+4].hex(),'value':struct.unpack('<'+kind,raw[off:off+4])[0]}
 result['limits'][1]='Dynamic overflow proof now exists separately in textbox-bounds-native-r1/r2 and the bounds audit; other overflow paths remain unverified.'
 result['analyst_names']['00438304']='classify_drawing_geometry_and_update_shape_or_image_counters'
 result['shape_bounds']={'parser_counter_offset':'0x200','main_report_slot':'0x2a','comparison':'inclusive overflow; strict in-bounds predicate is negated','unknown_adjustment_fields':['0x138','0x13c','0x140','0x144'],'dynamic_evidence':'shape-bounds-audit-r2/audit.json','limits':'Early trace keys call fields inset; that semantic label is unconfirmed. Raw offsets/values are authoritative.'}
 (out/'map.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'functions_named':len(result['analyst_names']),'slices':len(slices),'unit_constants':len(constants)}))
if __name__=='__main__':main()

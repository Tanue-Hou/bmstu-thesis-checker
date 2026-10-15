"""Retain actual native font instructions/constants and analyst reconstruction."""
import argparse,hashlib,json,struct
from pathlib import Path
import pefile,capstone
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);raw=(ROOT.parent/'runtime/TestVkr232.exe').read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0';pe=pefile.PE(data=raw);cs=capstone.Cs(3,4);slices={}
 for name,start,end in [('font_producer_gates',0x409a8b,0x409b84),('small_report_gate',0x47b5dd,0x47b5f6),('large_report_gate',0x47b7c7,0x47b7e0)]:
  off=pe.get_offset_from_rva(start-0x400000);lines=['%08x %s %s'%(i.address,i.mnemonic,i.op_str) for i in cs.disasm(raw[off:off+end-start],start)];(out/(name+'.asm')).write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n');slices[name]={'start_va':hex(start),'end_va_exclusive':hex(end),'instructions':len(lines)}
 constants={}
 for va in [0x6e519c,0x6e51a0]:
  off=pe.get_offset_from_rva(va-0x400000);constants[hex(va)]={'raw_hex':raw[off:off+4].hex(),'integer':struct.unpack('<i',raw[off:off+4])[0]}
 result={'target_sha256':digest,'slices':slices,'integer_thresholds':constants,'analyst_names':{'004098f8':'classify_run_font_and_role_gates','00402f08':'accumulate_text_in_selected_diagnostic_bucket','00436c68':'prepare_run_character_properties','0047a528':'check_file_and_construct_reports'},'counter_map':{'small':{'parser_offset':'0x184','main_slot':'0xb'},'tiny_observation':{'parser_offset':'0x188','main_slot':'0xc'},'large':{'parser_offset':'0x18c','main_slot':'0xd'}},'evidence':'font-audit-r1/audit.json','unknowns':['AC flag full semantics: early trace calls it vertical_align but superscript control stayed0.','c8 flag full semantics: single-cell table control stayed0; it is not proven to be a general table flag.','Tiny reporting/use outside the ordinary small-font main branch; PDF and complex-story paths.']}
 (out/'map.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');(out/'reconstruction.c').write_text('''/* Analyst reconstruction, not original author source. Exact target in map.json. */
if (enabled && half_points > 0 && half_points < 2*minimum_pt) {
    if (half_points > minimum_pt) add_utf16_text(small_bucket);
    else add_utf16_text(tiny_bucket);
}
if (enabled && half_points > 2*maximum_pt && c8 == 0 &&
    (f0 == 0 || previous_textbox_units > 100)) add_utf16_text(large_bucket);
if (small_count > 10) report_small();
if (large_count > 10) report_large();
/* The producer has an outer AC/enabled gate; unknown flags are not generalized. */
''',encoding='utf-8',newline='\n');print(json.dumps({'functions_named':len(result['analyst_names']),'slices':len(slices)}))
if __name__=='__main__':main()

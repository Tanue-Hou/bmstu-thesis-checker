import hashlib,json,struct
from pathlib import Path
import capstone,pefile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'evidence/format-expansion/static'
TARGET=Path('C:/Users/Tanue Hou/Downloads/TestVkr (1).exe')
if __name__=='__main__':
    raw=TARGET.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='0bb43cebc4c7ee196913d2ea2240f7bc53aaac1e6b8f6394e6201024a108b8cb'
    pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase;offset=pe.get_offset_from_rva(0x4db650-base)
    md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    lines=[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in md.disasm(raw[offset:offset+12000],0x4db650) if 0x4dc21e<=i.address<=0x4dc2fa]
    OUT.mkdir(exist_ok=True);(OUT/'phd-margin-targets.assembly.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    records={}
    for va in [0x4db64c,0x4dc720]:
        off=pe.get_offset_from_rva(va-base);records[hex(va)]={'file_offset':hex(off),'raw_hex':raw[off:off+4].hex(),'float32':struct.unpack_from('<f',raw,off)[0]}
    source=ROOT/'evidence/2026-10-14/decompilation/recovered_pseudocode.c';code=source.read_text(encoding='utf-8');a=code.index('/* ENTRY 004db60c');b=code.find('/* ENTRY ',a+10)
    (OUT/'004db60c.c').write_text(code[a:b],encoding='utf-8')
    (OUT/'margin-provenance.json').write_text(json.dumps({'target_sha256':digest,'pseudocode_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'work_code_test':'cmp [object+0x154],5 at VA 004dc221','targets_mm':{'left':25,'right':10,'top':20,'bottom':20},'constants':records,'comparator':'target - float32_tolerance <= actual <= target + float32_tolerance','limits':'Static bytes and pseudocode; runtime evidence retained separately.'},indent=2)+'\n',encoding='utf-8')

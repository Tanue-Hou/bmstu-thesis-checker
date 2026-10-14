"""Retain focused functions and TITUL resource from the already identified binary."""
import hashlib,json,zlib
from pathlib import Path
import pefile
ROOT=Path(__file__).resolve().parents[2]
TARGET=Path('C:/Users/Tanue Hou/Downloads/TestVkr (1).exe')
OUT=ROOT/'evidence/graduate-structure/static'
SOURCE=ROOT/'evidence/2026-10-14/decompilation/recovered_pseudocode.c'
ADDRESSES=['0049e6d0','0049cfd8','0049c3ec','0049771c','00499268','00495ee8','00494dd0','00495584','00496fc4','00498dfc','0049fa04']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    assert digest(TARGET)=='0bb43cebc4c7ee196913d2ea2240f7bc53aaac1e6b8f6394e6201024a108b8cb'
    code=SOURCE.read_text(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True)
    for addr in ADDRESSES:
        start=code.index('/* ENTRY '+addr);end=code.find('/* ENTRY ',start+10)
        (OUT/(addr+'.c')).write_text(code[start:end],encoding='utf-8')
    pe=pefile.PE(str(TARGET));resource=None
    for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        for name in kind.directory.entries:
            if str(name.name)!='TITUL':continue
            for lang in name.directory.entries:
                d=lang.data.struct;raw=pe.get_data(d.OffsetToData,d.Size)
                (OUT/'TITUL.raw').write_bytes(raw);decoded=zlib.decompress(raw)
                (OUT/'TITUL.decoded').write_bytes(decoded)
                (OUT/'TITUL.txt').write_text(decoded.decode('cp1251'),encoding='utf-8')
                resource={'name':'TITUL','rva':hex(d.OffsetToData),'file_offset':hex(pe.get_offset_from_rva(d.OffsetToData)),'compressed_sha256':digest(OUT/'TITUL.raw'),'decoded_sha256':digest(OUT/'TITUL.decoded'),'encoding':'cp1251','compression':'zlib'}
    work_codes={}
    for va in [0x6e4d44,0x6e4d48,0x6e4d4c,0x6e4648,0x6e4c24]:
        off=pe.get_offset_from_rva(va-pe.OPTIONAL_HEADER.ImageBase)
        work_codes[hex(va)]={'file_offset':hex(off),'utf16_first_character':pe.__data__[off:off+2].decode('utf-16-le')}
    record={'target_sha256':digest(TARGET),'recovered_pseudocode_sha256':digest(SOURCE),'functions':ADDRESSES,'resource':resource,'work_codes':work_codes,'limits':'Static recovered pseudocode and raw resource bytes; not original source code. Execution is evidenced separately by native captures.'}
    (OUT/'provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'functions':len(ADDRESSES),'resource':resource['name']}))

"""Retain native decompiler output and a bounded work-name function trace."""
import hashlib,json,re,shutil,argparse
from pathlib import Path
import pefile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('binary');p.add_argument('export_dir');a=p.parse_args()
    binary=Path(a.binary);source=Path(a.export_dir);out=ROOT/'evidence/agent-v027/decompilation'
    if sha(binary)!='5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0':raise ValueError('Wrong target')
    out.mkdir(parents=True,exist_ok=False)
    for name in ['coverage.txt','functions.tsv','calls.tsv','defined_strings.tsv','recovered_pseudocode.c']:shutil.copyfile(source/name,out/name)
    text=(out/'recovered_pseudocode.c').read_text(encoding='utf-8')
    function=re.search(r'/\* ENTRY 0044a748.*?(?=/\* ENTRY|\Z)',text,re.S).group()
    (out/'work-name.function.c').write_text(function,encoding='utf-8')
    pe=pefile.PE(str(binary));raw=binary.read_bytes();literals=[]
    for va in ['006d6a86','006d6a8a','006d6ac8','006d6b0c','006d6b5a','006d6bee']:
        offset=pe.get_offset_from_rva(int(va,16)-pe.OPTIONAL_HEADER.ImageBase)
        value=raw[offset:offset+250].decode('utf-16-le',errors='replace').split('\0')[0]
        literals.append({'va':va,'file_offset':offset,'utf16_text':value,'referencing_function':'0044a748'})
    receipt={'target_sha256':sha(binary),'tool':'Ghidra 12.1.4 headless + ExportTestVkr.java',
             'export_script':'scripts/reverse_engineering/ExportTestVkr.java',
             'export_script_sha256':sha(ROOT/'scripts/reverse_engineering/ExportTestVkr.java'),
             'files':{f.name:sha(f) for f in out.iterdir() if f.is_file()},'work_name_literals':literals,
             'limits':'Decompiled C-like text, not original source or compilable project. Function discovery/types/indirect calls incomplete. 10191/10192 refers only to discovered functions, not semantic coverage. Literal references are static evidence, not execution.',
             'work_name_trace':'0044a748 references both nominative and oblique VKR word lists; real-case native captures omit WorkNameInvalid for all 13 oblique covers. Adjacent paragraph matching/combinations remain bounded.'}
    (out/'provenance.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(out),'functions':10192,'decompiled':10191}))
if __name__=='__main__':main()

"""Recompute the narrow startup finding from retained traces and native bytes."""
import argparse, ctypes, hashlib, json, re
from pathlib import Path
import capstone
import pefile

ROOT=Path(__file__).resolve().parents[2]
SHA='5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(ROOT/'evidence'):raise ValueError('Evidence directory required')
    out.mkdir(parents=True,exist_ok=False)
    binary=ROOT.parent/'runtime/TestVkr232.exe'
    assert digest(binary)==SHA
    pe=pefile.PE(str(binary));base=pe.OPTIONAL_HEADER.ImageBase
    source=ROOT/'evidence/agent-v027/decompilation/recovered_pseudocode.c'
    text=source.read_text(encoding='utf-8');functions={}
    chunks=re.split(r'/\* ENTRY ([0-9a-fA-F]+) NAME (.*?) \*/',text)
    for i in range(1,len(chunks),3):functions[chunks[i]]=chunks[i+2]
    command_readers=[address for address,body in functions.items() if 'GetCommandLineW' in body]
    exports=[]
    for item in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        section=pe.get_section_by_rva(item.address)
        exports.append({'name':item.name.decode('ascii') if item.name else None,'va':hex(base+item.address),'section':section.Name.rstrip(b'\0').decode('ascii') if section else None,'executable_section':bool(section and section.Characteristics&0x20000000)})
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    instructions=[{'va':hex(i.address),'mnemonic':i.mnemonic,'operands':i.op_str} for i in decoder.disasm(pe.get_data(0x2db41,14),0x42db41)]
    assert instructions[-2]['va']=='0x42db4a'
    traces=[]
    for name in ['startup-fault-r2','startup-fault-r3']:
        path=ROOT/'evidence/business-map-232'/name/'trace.json';trace=json.loads(path.read_text())
        assert trace['target_sha256']==SHA and trace['binary_unchanged'] and trace['error'] is None
        fault=next(event for event in trace['events'] if event.get('preferred_va')=='0x42db4a')
        assert int(fault['registers']['Ecx'],16)==0x9141
        traces.append({'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path),'owned_pid':trace['owned_pid'],'fault':fault,'stop_reason':trace['stop_reason']})
    unit=0x9141+0x430;encoded=chr(unit).encode('cp936');russian=encoded.decode('cp1251')
    assert russian=='по' and ord(russian[0])-0x430==15
    result={'target_sha256':SHA,'sources':{source.relative_to(ROOT).as_posix():digest(source)},'current_ansi_codepage':ctypes.windll.kernel32.GetACP(),'exports':exports,'GetCommandLineW_referencing_functions':command_readers,'fault_instruction_sequence':instructions,'traces':traces,'encoding_candidate':{'observed_unit':hex(unit),'cp936_bytes':encoded.hex(),'same_bytes_cp1251':russian,'correct_first_letter_bucket':ord(russian[0])-0x430,'status':'Consistent mathematical encoding explanation, not a captured source-byte conversion path'},'confirmed':'Two owned startup executions reached a character-derived object-table lookup with index37185 and faulted while dereferencing its result.','unknown':['Original ANSI source bytes and exact decoding API not captured.','Russian-locale branch comparison remains required.','No existing callable headless checking interface established.'],'ABI_correction':'Observed EAX/EDX register arguments do not justify labeling the native routines MSVC thiscall.'}
    (out/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'README.zh.md').write_text('''# 启动异常定位：已确认范围

两次独立启动均在 `0042db4a` 读取无效对象指针。此前指令从对象表读取第 37185 项；伪代码显示索引来自首个 UTF-16 字符减去 `0x430`。第二次捕获的列表项首字符为 `镱`（U+9571），与该索引一致。原程序文件哈希未变，调试仅针对本次创建的进程；没有操作用户已有程序。

本机 ANSI 代码页为 936。`镱` 的 CP936 字节为 `EF EE`，相同字节按 CP1251 解码为俄语 `по`；其中首字母 `п` 对应正常索引 15。这支持代码页误解码的解释，但尚未捕获原始转换输入或完成俄语环境断点对照，因此还不能断言具体解码路径已证明，也不应据此修改原程序。

`analysis.json` 保留源哈希、两次动态记录、实际指令、导出所在节、命令行读取函数与限制。`_TstWndMain` 位于数据节，不能视为可调用接口；启动阶段未命中业务断点不能证明不存在后台入口。这里的诊断不进入论文格式判据，也不开启新修复动作。
''',encoding='utf-8')
    print(json.dumps({'target_verified':True,'trace_count':len(traces),'command_readers':command_readers,'exports':len(exports),'encoding_candidate':result['encoding_candidate']},ensure_ascii=True))
if __name__=='__main__':main()

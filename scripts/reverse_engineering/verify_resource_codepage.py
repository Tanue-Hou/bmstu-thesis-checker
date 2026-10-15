"""Verify compressed dictionary bytes against an actual startup argument."""
import ctypes,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    evidence=ROOT/'evidence/business-map-232'
    resource_path=evidence/'pe-resources-REA.json';record=json.loads(resource_path.read_text(encoding='utf-8'))
    target=record['normalized_result']['artifact'];binary=(ROOT.parent/'runtime/TestVkr232.exe').read_bytes();assert sha(binary)==target['sha256']
    resource=next(r for r in record['normalized_result']['resources'] if r['name'].get('name')=='RU_PREFS' and r['type'].get('name')=='TESTDATA')
    location=resource['payload']['location'];compressed=binary[location['offset']:location['offset']+location['bytes']];assert sha(compressed)==resource['payload']['sha256']
    decoder=zlib.decompressobj();raw=decoder.decompress(compressed,16*1024*1024)
    assert decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data
    line=raw.split(b'\r\n',1)[0]
    trace_path=evidence/'startup-system-input/trace.json';trace=json.loads(trace_path.read_text())
    assert trace['target_sha256']==target['sha256'] and trace['binary_unchanged'] and not trace['error']
    hit=next(h for h in trace['breakpoint_hits'] if h['label']=='startup_bucket_candidate')
    captured=hit['candidate_input_utf16_prefix'];current=line.decode('cp936');proper=line.decode('cp1251')
    assert captured==current and captured!=proper and line==b' - '+bytes.fromhex('efee')+b' |'
    fault=next(e for e in trace['events'] if e.get('preferred_va')=='0x42db4a')
    observed_index=ord(captured.split()[1][0])-0x430
    expected_index=ord(proper.split()[1][0])-0x430
    assert observed_index==fault['bucket_index']==37185 and expected_index==15
    result={'target_sha256':target['sha256'],'REA_evidence_id':record['evidence_id'],'sources':{resource_path.relative_to(ROOT).as_posix():sha(resource_path.read_bytes()),trace_path.relative_to(ROOT).as_posix():sha(trace_path.read_bytes())},'resource':{'type':'TESTDATA','name':'RU_PREFS','compressed_file_offset':location['offset'],'compressed_bytes':len(compressed),'compressed_sha256':sha(compressed),'decoded_bytes':len(raw),'decoded_sha256':sha(raw),'first_record_hex':line.hex()},'comparison':{'cp1251_first_record':proper,'cp936_first_record':current,'captured_argument':captured,'exact_cp936_match':True,'system_ACP':ctypes.windll.kernel32.GetACP(),'observed_index':observed_index,'cp1251_index':expected_index,'initialized_buckets_static':32},'finding':'The compressed resource first record, decoded with CP936, exactly reproduces the captured corrupted argument and out-of-range index. CP1251 produces a valid Cyrillic index.','limits':['The exact native conversion API/codepage argument is not yet captured.','Russian-locale debugger run has not reached business initialization successfully.','No original binary patch or system locale change was made; this is not a production fix.']}
    out=evidence/'resource-codepage-r1';out.mkdir(exist_ok=False)
    (out/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'README.zh.md').write_text('''# 词库代码页与启动异常的交叉证据

REA 资源树证据定位 `TESTDATA/RU_PREFS`。按文件范围读取并核对哈希，zlib 解压后首行字节为 `20 2D 20 EF EE 20 7C`。

按 CP1251 解码为 ` - по |`；按 CP936 解码为 ` - 镱 |`，与原进程进入 `0042d890` 时的实际参数完全一致。后续断点记录索引为 37185；按正确俄语首字母计算为 15，静态调用者初始化 32 个桶。

已证明原资源字节在 CP936 解码下可精确重现实际错误输入及索引。具体转换 API 的参数仍需断点捕获；俄语环境的业务断点对照尚未通过。未修改系统语言、原 EXE 或论文。`verify_resource_codepage.py` 可重算此结论，输出目录不允许覆盖。
''',encoding='utf-8')
    print(json.dumps(result['comparison'],ensure_ascii=True))
if __name__=='__main__':main()

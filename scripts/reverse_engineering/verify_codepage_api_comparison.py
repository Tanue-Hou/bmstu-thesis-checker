"""Audit the actual codepage-call intervention against its untreated control."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'evidence/business-map-232'
SHA='5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    rows=[];inputs={}
    for name,treated in [('codepage-api-control-r3',False),('codepage-api-intervention-r1',True),('codepage-api-intervention-r2',True)]:
        path=EVIDENCE/name/'trace.json';raw=path.read_bytes();trace=json.loads(raw)
        assert trace['target_sha256']==SHA and trace['argument']=='--help' and trace['binary_unchanged']
        assert trace['error'] is None and not trace['cleanup_errors']
        snapshot=path.parent/'tracer-source.py.txt';assert sha(snapshot.read_bytes())==trace['tracer_sha256']
        calls=trace['large_buffer_codepage_calls'];matched=[c for c in calls if c.get('matched_resource')]
        assert len(matched)==6 and {c['matched_resource'] for c in matched}=={'RU_FORMS','RU_PREFS','RU_ENDS'}
        assert all(c['codepage']==0 for c in matched)
        hashes={c['matched_resource']:c['input_sha256'] for c in matched}
        if inputs:assert hashes==inputs
        else:inputs=hashes
        changes=[c for c in calls if 'intervention_codepage' in c]
        assert len(changes)==(6 if treated else 0)
        assert all(c['intervention_codepage']==1251 and c['matched_resource'] for c in changes)
        hit=next(h for h in trace['breakpoint_hits'] if h['label']=='startup_bucket_candidate')
        assert hit['candidate_input_utf16_prefix']==(' - по |' if treated else ' - 镱 |')
        faults=[e for e in trace['events'] if e.get('exception_code')=='0xc0000005']
        form=int(trace['last_main_form_pointer'],16)
        assert (not faults and form>0) if treated else (len(faults)==8 and form==0)
        readers=[h for h in trace['breakpoint_hits'] if h['label']=='parameter_reader']
        if treated:assert len(readers)==1 and int(readers[0]['registers']['Eax'],16)==0
        rows.append({'trace':path.relative_to(ROOT).as_posix(),'trace_sha256':sha(raw),'tracer_sha256':trace['tracer_sha256'],'owned_pid':trace['owned_pid'],'treatment':treated,'verified_dictionary_conversions':len(matched),'changed_calls':len(changes),'access_violations':len(faults),'main_form_pointer_nonzero':form>0,'startup_argument':hit['candidate_input_utf16_prefix'],'command_parameter_reader_n':0 if readers else None,'elapsed_observation_ms':max(e.get('elapsed_ms',0) for e in trace['events'])})
    result={'target_sha256':SHA,'status':'verified_bounded_startup_codepage_cause_and_intervention','runs':rows,'same_decompressed_dictionary_hashes':inputs,'observation':'The untreated original selects CP_ACP at six matched dictionary conversion calls and crashes with corrupted input. Two independent treated owned processes select CP1251 for those exact calls, preserve correct input, reach main-form creation, and have no access violation in the observation windows.','reference':{'title':'Microsoft MultiByteToWideChar documentation','url':'https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-multibytetowidechar','meaning':'CP_ACP uses the system default Windows ANSI code page.'},'limits':['Six process-local API argument changes constitute an instrumented run, not unmodified native behavior.','Main-form creation and absence of observed AV do not prove complete UI readiness or correct thesis checking.','No production launcher, native checking CLI, or additional repair action is accepted by this verification.','Existing commandline observation only saw n=0; this is not proof of absence of other consumers.']}
    out=EVIDENCE/'codepage-api-verification-r1';out.mkdir(exist_ok=False)
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'README.zh.md').write_text('''# 已确认词库代码页调用与受控修正效果

1 次未干预对照、2 次独立干预均使用相同 EXE、参数及三份解压词库。每次实际进入 `MultiByteToWideChar` 的大小查询和转换各 3 次，代码页实参均为 0。输入缓冲区完整 SHA-256 与词库匹配。

对照进程产生 ` - 镱 |`、越界索引和访问异常。两个实验进程仅将这六次调用的栈上代码页实参改为 1251，恢复 ` - по |`，越过原崩溃点并创建非空主窗体对象，观察窗口内无访问异常。原 EXE 哈希未变，没有修改系统语言。

这是实际 API 参数、字符结果与执行路径的受控因果对照。尚不是正式启动器或无界面论文检查入口，也没有证明所有检查规则等价。后续原程序输出必须注明是否经过此干预，不能混入未修改运行的验证证据。

详细哈希、进程身份、观察窗口与限制见 `verification.json`；由 `verify_codepage_api_comparison.py` 重算。
''',encoding='utf-8')
    print(json.dumps({'status':result['status'],'runs':len(rows),'untreated_AV':rows[0]['access_violations'],'treated_AV':[r['access_violations'] for r in rows[1:]],'matched_resources':len(inputs)}))
if __name__=='__main__':main()

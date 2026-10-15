"""Freeze scale release with actual tests, MCP, and private same-hash receipts."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from check_document import load_rule_registry,verification_context,context_evidence_valid


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base=ROOT/'evidence/business-map-232'
    log=base/'regression-v0220-initial.log';text=log.read_text(encoding='utf-8-sig')
    assert re.search(r'\nOK\s*$',text) and not re.search(r'^(FAIL|ERROR):',text,re.M)
    tests=int(re.search(r'Ran (\d+) tests',text).group(1))
    audit_path=base/'scale-audit-r1/audit.json';audit=json.loads(audit_path.read_text())
    assert audit['native_executions']==52 and audit['unique_inputs']==26
    assert audit['native_modes']=={'master':26,'phd':26}
    assert all(r['both_diagnostic_families_match'] and r['all_run_states_match'] for r in audit['cases'])
    for name,digest in audit['sources'].items():assert sha(ROOT/name)==digest,name
    smoke=json.loads((base/'scale-mcp-r1/receipt.json').read_text())
    assert smoke['status']=='passed_actual_mcp_native_scale_smoke'
    assert smoke['server_version']=='0.2.20' and len(smoke['cases'])==20
    assert sha(ROOT.parent/smoke['private_raw_response'])==smoke['raw_response_sha256']
    rules=load_rule_registry();contexts=[]
    for rule in rules.values():
        for key in rule.get('verification_by_build',{}).get('232',{}):
            fmt,mode=key.split(':')
            assert context_evidence_valid(verification_context(rule,fmt,mode,232))
            contexts.append(rule['rule_id']+'/'+key)
    assert len(rules)==39 and len(contexts)==23
    repair_digest=sha(ROOT/'scripts/repair_build232.py')
    assert 'Skill is valid!' in (base/'skill-v0220-validation.log').read_text(encoding='utf-8-sig')
    assert repair_digest=='1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
    private=ROOT.parent/'private_trials/2026-10-15'
    trial=private/'cross_v0220_final';previous=private/'cross_v0219_final'
    summary_path=trial/'summary.private.json';summary=json.loads(summary_path.read_text())
    assert summary['processed_cases']==17 and summary['error_cases']==0 and not summary['errors']
    assert sha(private/'inventory.private.json')==summary['input_inventory_sha256']
    assert sha(previous/'summary.private.json')==summary['baseline_summary_sha256']['cross_v0219_final']
    for name,digest in summary['implementation_sha256'].items():assert sha(ROOT/name)==digest,name
    for name,digest in summary['native_capture_files_sha256'].items():assert sha(private/'native-build-232'/name)==digest
    inventory=json.loads((private/'inventory.private.json').read_text(encoding='utf-8-sig'))
    scale_rules=['Word.FontScaleTooSmall','Word.FontScaleTooLarge']
    current={rule:0 for rule in scale_rules};older=current.copy();changed=0
    for row in summary['cases']:
        inputs=[i for i in inventory if i.get('sha256')==row['source_sha256']]
        assert len(inputs)==1 and sha(Path(inputs[0]['path']))==row['source_sha256']
        local=trial/'cases'/(row['case']+'.local.json')
        assert sha(local)==row['local_report_sha256']
        assert sha(trial/'cases'/(row['case']+'.comparison.json'))==row['comparison_sha256']
        new_findings=json.loads(local.read_text())['findings']
        old_findings=json.loads((previous/'cases'/(row['case']+'.local.json')).read_text())['findings']
        new_counts={rule:sum(f['rule_id']==rule for f in new_findings) for rule in scale_rules}
        old_counts={rule:sum(f['rule_id']==rule for f in old_findings) for rule in scale_rules}
        changed+=new_counts!=old_counts
        for rule in scale_rules:current[rule]+=new_counts[rule];older[rule]+=old_counts[rule]
    out=base/'stage-v0220-final';out.mkdir(exist_ok=False)
    receipt={key:summary[key] for key in ['processed_cases','error_cases','native_totals',
        'paragraph_diagnostics_v0219_total','paragraph_diagnostics_v0220_total',
        'font_size_diagnostics_v0219_total','font_size_diagnostics_v0220_total','implementation_sha256']}
    receipt.update(private_summary_sha256=sha(summary_path),scale_diagnostics_current=current,
        scale_diagnostics_previous=older,scale_changed_cases=changed,
        additional_scale_dependency_sha256=sha(ROOT/'scripts/testvkr-service/checkers/native_scale_counts.py'),
        limits='Existing native captures reused; only local checker reran. Counts do not prove real-paper accuracy. Additional scale dependency is hashed at final freeze; runner records the existing ten-file dependency set. No private paths/text/EXE published.')
    (out/'private-case-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    chain=ROOT/'docs/RULE_CHAIN.zh.md'
    value=re.sub(r'当前注册表包含\d+个规则ID；build232有\d+个独立',
        f'当前注册表包含{len(rules)}个规则ID；build232有{len(contexts)}个独立',chain.read_text(encoding='utf-8'))
    chain.write_text(value,encoding='utf-8',newline='\n')
    (out/'REPORT.zh.md').write_text(f'''# v0.2.20 验收

52次原程序执行（硕士26/博士NKR26）、26个不同合成输入，三类缩放计数、两诊断族、分支及完整run属性/启用状态一致；20项真实MCP调用通过。完整回归一次运行{tests}项全通过，Skill结构验证另留日志。

17份真实案例复查0错误，原件未改；复用既有80项原程序诊断，未映射0项，不是重新执行原程序。段落{summary['paragraph_diagnostics_v0220_total']}对{summary['paragraph_diagnostics_v0219_total']}、字号{summary['font_size_diagnostics_v0220_total']}对{summary['font_size_diagnostics_v0219_total']}；缩放当前{sum(current.values())}对历史{sum(older.values())}，变化案例{changed}。这些数量不代表论文准确率。

注册表{len(rules)}规则、232独立验证上下文{len(contexts)}项，证据及实施哈希通过。新增普通DOCX字符缩放检查及XML位置，不新增任何副本修复；修复源SHA保持不变。

首行缩进生产者仍未恢复。进一步函数地图与ABI/调用者复核留在first-indent-static-r2/r3；未发现直接writer不证明不存在。原生包装器仍依赖原EXE，完整独立复刻目标未完成。
''',encoding='utf-8',newline='\n')
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    new=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    sources=sorted({p for p in tracked+new if p and not p.startswith('evidence/') and (ROOT/p).is_file()})
    evidence=[p for pattern in ['scale-*','first-indent-static-r2','first-indent-static-r3'] for d in base.glob(pattern)
              if d.is_dir() for p in d.rglob('*') if p.is_file()]
    evidence += [log,base/'skill-v0220-validation.log',out/'REPORT.zh.md',out/'private-case-receipt.json']
    manifest={'release':'0.2.20','tests_passed':tests,'native_scale_runs':52,'unique_inputs':26,
        'actual_mcp_cases':len(smoke['cases']),'registered_rule_ids':len(rules),'build232_contexts':contexts,
        'repair_permission_expanded':False,'repair_source_sha256':repair_digest,'full_goal_completed':False,
        'source_files':{p:sha(ROOT/p) for p in sources},
        'evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(evidence))}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ['source_files','evidence_files','build232_contexts']}))


if __name__=='__main__':
    main()

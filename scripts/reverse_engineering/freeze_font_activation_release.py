"""Freeze the bounded font release only after regression and private checks."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import load_rule_registry, verification_context, context_evidence_valid


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = ROOT / 'evidence/business-map-232'
    log = base / 'regression-v0219-initial.log'
    text = log.read_text(encoding='utf-8-sig')
    count = int(re.search(r'Ran (\d+) tests', text).group(1))
    failures = re.findall(r'^(FAIL|ERROR): (.+)$', text, re.M)
    assert failures == [('FAIL', 'test_font_locations_distinguish_front_matter (test_build232.Build232Tests.test_font_locations_distinguish_front_matter)')]
    retry_path = base / 'regression-v0219-activation-expectation-retry.log'
    retry = retry_path.read_text(encoding='utf-8-sig')
    assert re.search(r'\nOK\s*$', retry) and 'test_font_locations_distinguish_front_matter' in retry
    original_test = base / 'test_build232_before_activation_expectation.py.txt'
    previous_test = subprocess.check_output(['git', 'show', 'fe89bd3f6007d94f60c25556df28d8dd99b47dd5:tests/test_build232.py'], cwd=ROOT)
    assert original_test.read_bytes() == previous_test
    audit_path = base / 'font-activation-audit-r3/audit.json'
    audit = json.loads(audit_path.read_text())
    assert audit['native_executions'] == 76 and audit['unique_input_hashes'] == 48
    for name, digest in audit['sources'].items():
        assert sha(ROOT / name) == digest, name
    smoke = json.loads((base / 'font-activation-mcp-r2/receipt.json').read_text())
    assert smoke['status'] == 'passed_actual_mcp_font_activation_smoke'
    assert smoke['server_version'] == '0.2.19' and len(smoke['cases']) == 14
    assert sha(ROOT.parent / smoke['private_raw_response']) == smoke['raw_response_sha256']
    rules = load_rule_registry()
    contexts = []
    for rule in rules.values():
        for key in rule.get('verification_by_build', {}).get('232', {}):
            fmt, mode = key.split(':')
            assert context_evidence_valid(verification_context(rule, fmt, mode, 232))
            contexts.append(rule['rule_id'] + '/' + key)
    assert len(rules) == 39 and len(contexts) == 19
    assert sha(ROOT / 'scripts/repair_build232.py') == '1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
    private = ROOT.parent / 'private_trials/2026-10-15'
    trial = private / 'cross_v0219_final'
    summary_path = trial / 'summary.private.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    assert summary['processed_cases'] == 17 and summary['error_cases'] == 0 and not summary['errors']
    for name, digest in summary['implementation_sha256'].items():
        assert sha(ROOT / name) == digest, name
    assert sha(private / 'inventory.private.json') == summary['input_inventory_sha256']
    inventory = json.loads((private / 'inventory.private.json').read_text(encoding='utf-8-sig'))
    for name, digest in summary['native_capture_files_sha256'].items():
        assert sha(private / 'native-build-232' / name) == digest
    for row in summary['cases']:
        inputs = [i for i in inventory if i.get('sha256') == row['source_sha256']]
        assert len(inputs) == 1 and sha(Path(inputs[0]['path'])) == row['source_sha256']
        assert sha(trial / 'cases' / (row['case'] + '.local.json')) == row['local_report_sha256']
        assert sha(trial / 'cases' / (row['case'] + '.comparison.json')) == row['comparison_sha256']
    out = base / 'stage-v0219-final'
    out.mkdir(exist_ok=False)
    receipt = {key: summary[key] for key in ('processed_cases', 'error_cases', 'native_totals',
        'paragraph_diagnostics_v0218_total', 'paragraph_diagnostics_v0219_total',
        'font_size_diagnostics_v0218_total', 'font_size_diagnostics_v0219_total',
        'paragraph_changes_by_rule_vs_v0218', 'font_size_changes_vs_v0218', 'implementation_sha256')}
    receipt['private_summary_sha256'] = sha(summary_path)
    receipt['limits'] = 'Existing native captures reused; no native paper reruns or source changes. Counts are not real-paper accuracy. Private paths/text excluded.'
    (out / 'private-case-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    (out / 'REPORT.zh.md').write_text(f'''# v0.2.19 验收

76次原程序执行、48个不同合成输入，字号计数、报告分支及异常run启用状态核对通过；14项真实MCP调用通过。{count}个唯一测试验收：全套初次151通过、1项旧断言仍要求封面字号计入而失败；仅更新该测试以确认232抑制封面、230仍保留旧行为，相关模块复验通过。未改生产实现，原日志和旧测试源码均保留；不宣称一次性全绿运行。

17份真实案例只重跑本地CLI并复用既有原生capture；源文件未改。段落诊断{summary['paragraph_diagnostics_v0219_total']}（此前{summary['paragraph_diagnostics_v0218_total']}），字号诊断{summary['font_size_diagnostics_v0219_total']}（此前{summary['font_size_diagnostics_v0218_total']}）。不能据此宣称真实论文准确率。

39个规则ID、19个232验证上下文证据/实现哈希有效。修复实现哈希不变，未新增修复权限。复杂内容、PDF字号和其他模式不继承本轮证明，完整复刻尚未完成。

Antigravity此次CLI登录失败，未取得模型复核意见。首轮MCP校验因旧location没有part字段失败；保留r1原始证据，在r2按实际XML路径归属校验通过。
''', encoding='utf-8', newline='\n')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    new = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    sources = sorted({p for p in tracked + new if p and not p.startswith('evidence/') and (ROOT / p).is_file()})
    evidence = [p for pattern in ('font-activation-*', 'linked-font-*') for directory in base.glob(pattern)
                if directory.is_dir() for p in directory.rglob('*') if p.is_file()]
    evidence += [base / 'font-activation-review-prompt.txt', base / 'font-real-case-deltas-r1.json',
                 log, retry_path, base / 'test_build232_before_activation_expectation.py.txt',
                 out / 'REPORT.zh.md', out / 'private-case-receipt.json']
    manifest = {'release':'0.2.19', 'accepted_unique_tests':count, 'initial_passed':count-1,
        'obsolete_test_expectation_failures':1, 'targeted_retry_tests':9,
        'native_font_runs':76, 'unique_inputs':48,
        'actual_mcp_cases':14, 'registered_rule_ids':39, 'build232_contexts':contexts,
        'repair_permission_expanded':False, 'full_goal_completed':False,
        'source_files':{p:sha(ROOT / p) for p in sources},
        'evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(evidence))}}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('source_files','evidence_files','build232_contexts')}))


if __name__ == '__main__':
    main()

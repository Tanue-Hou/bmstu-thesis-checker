"""Freeze integrated paragraph release, private receipts and regression repair proof."""
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
    out = base / 'stage-v0218-final'
    regression = json.loads((base / 'regression-v0218-acceptance.json').read_text())
    assert regression['unique_tests_passed'] == 148 and regression['unresolved_failures'] == 0
    assert sha(base / 'regression-v0218-initial.log') == regression['initial_log_sha256']
    assert sha(base / 'regression-v0218-schema-retry.log') == regression['targeted_retry_log_sha256']
    registry_path = ROOT / 'scripts/testvkr-service/rules/rules_verified.json'
    assert sha(registry_path) == regression['current_registry_sha256']
    rules = load_rule_registry()
    contexts = []
    for rule in rules.values():
        for key in rule.get('verification_by_build', {}).get('232', {}):
            fmt, mode = key.split(':')
            assert context_evidence_valid(verification_context(rule, fmt, mode, 232))
            contexts.append(rule['rule_id'] + '/' + key)
    assert len(contexts) == 19 and len(rules) == 39
    assert sha(ROOT / 'scripts/repair_build232.py') == '1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
    audit = json.loads((base / 'paragraph-acceptance-r1/audit.json').read_text())
    assert len(audit['cases']) == 68 and all(c['three_families_agree'] for c in audit['cases'])
    for name, digest in audit['sources'].items():
        assert sha(ROOT / name) == digest, name
    smoke = json.loads((base / 'paragraph-mcp-final-r3/receipt.json').read_text())
    assert smoke['server_version'] == '0.2.18' and len(smoke['cases']) == 10
    assert all(c['three_families_match_native_capture'] for c in smoke['cases'])
    private = ROOT.parent / 'private_trials/2026-10-15'
    trial = private / 'cross_v0218_final'
    summary_path = trial / 'summary.private.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    assert summary['processed_cases'] == 17 and summary['error_cases'] == 0 and not summary['errors']
    for name, digest in summary['implementation_sha256'].items():
        assert sha(ROOT / name) == digest, name
    assert sha(private / 'inventory.private.json') == summary['input_inventory_sha256']
    inventory = json.loads((private / 'inventory.private.json').read_text(encoding='utf-8-sig'))
    baseline = json.loads((private / 'cross_v0217_final/summary.private.json').read_text(encoding='utf-8'))
    assert sha(private / 'cross_v0217_final/summary.private.json') == summary['baseline_summary_sha256']['cross_v0217_final']
    for name, digest in summary['native_capture_files_sha256'].items():
        assert sha(private / 'native-build-232' / name) == digest
    for case in summary['cases']:
        cid = case['case']
        assert case['source_sha256'] == next(c['source_sha256'] for c in baseline['cases'] if c['case'] == cid)
        entries = [i for i in inventory if i.get('sha256') == case['source_sha256']]
        assert len(entries) == 1 and sha(Path(entries[0]['path'])) == case['source_sha256']
        assert sha(trial / 'cases' / (cid + '.local.json')) == case['local_report_sha256']
        assert sha(trial / 'cases' / (cid + '.comparison.json')) == case['comparison_sha256']
        assert case['paragraph_rule_counts_v0218'] == case['paragraph_rule_counts_v0217']
        assert case['font_size_counts_v0218'] == case['font_size_counts_v0217']
    assert summary['native_totals'] == {'diagnostics': 80, 'unmapped': 0}
    out.mkdir(exist_ok=False)
    receipt = {'private_summary_sha256': sha(summary_path), 'processed_cases': summary['processed_cases'],
               'error_cases': summary['error_cases'], 'native_totals': summary['native_totals'],
               'paragraph_diagnostics_current': summary['paragraph_diagnostics_v0218_total'],
               'paragraph_diagnostics_baseline': summary['paragraph_diagnostics_v0217_total'],
               'font_diagnostics_current': summary['font_size_diagnostics_v0218_total'],
               'font_diagnostics_baseline': summary['font_size_diagnostics_v0217_total'],
               'per_case_changes': 0, 'implementation_sha256': summary['implementation_sha256'],
               'limits': 'Existing native captures reused. No native rerun, no paper/source modifications. Mapping and unchanged counts do not prove real-paper accuracy. Private filenames/content excluded.'}
    (out / 'private-case-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    chain = ROOT / 'docs/RULE_CHAIN.zh.md'
    value = re.sub(r'当前注册表包含\d+个规则ID；build232有\d+个独立',
                   f'当前注册表包含{len(rules)}个规则ID；build232有{len(contexts)}个独立', chain.read_text(encoding='utf-8'))
    chain.write_text(value, encoding='utf-8', newline='\n')
    (out / 'REPORT.zh.md').write_text(f'''# v0.2.18 验收

68次有效原程序运行、42个唯一合成输入（硕士47/NKR21），三个段落计数、诊断族及XML位置与正式CLI一致；{len(smoke['cases'])}个实际MCP调用通过。新增59/60后备启用边界、空段落、继承/覆盖、单格表格及1001段长输入。长输入普通属性采样触顶如实标记，末尾异常计数调用与最终报告仍有直接断点。

148个唯一测试验收通过：全套初次运行147通过、1个新增注册表缺空字段错误；仅补两个observed_message:null字段后，18项相关测试复验通过。删除这两个字段可重建初次注册表原SHA，全部已捕获核心实现SHA不变；原失败日志不覆盖，聚合收据不是伪造的一次性全绿运行。Skill按UTF8结构验证通过。

17份真实案例复查0错误，当前源/实施/报告/比较哈希一致；三类段落诊断44对44，字号16对16，逐例无变化；既有80条原生诊断全部映射。不能宣称真实案例误报率下降；公开仅脱敏收据，未上传论文或EXE。

当前{len(rules)}个规则ID、232独立验证上下文{len(contexts)}项，全部证据/实施哈希通过。仅受测普通DOCX硕士/NKR配置提升，复杂域/公式/编号/条件表格样式/布局及PDF不继承；首行生产者仍未恢复。学校建议独立运行，俄文文案不替代实际比较表达式。

修复实现SHA不变，自动修复权限不扩大。原生包装器仍依赖原程序，完整独立复刻目标未完成。
''', encoding='utf-8', newline='\n')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    new = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    sources = sorted({p for p in tracked + new if p and not p.startswith('evidence/') and (ROOT / p).is_file()})
    evidence = [p for directory in base.glob('paragraph*') if directory.is_dir() for p in directory.rglob('*') if p.is_file()]
    evidence += [p for p in base.glob('paragraph*') if p.is_file()]
    evidence += list((base / 'first-indent-static-r1').rglob('*'))
    evidence += [base / 'regression-v0218-initial.log', base / 'regression-v0218-schema-retry.log', base / 'regression-v0218-acceptance.json',
                 out / 'REPORT.zh.md', out / 'private-case-receipt.json']
    manifest = {'release': '0.2.18', 'accepted_unique_tests': 148, 'targeted_schema_retry_tests': 18,
                'native_valid_paragraph_runs': 68, 'unique_native_inputs': 42, 'actual_mcp_cases': 10,
                'private_cases_rechecked': 17, 'registered_rule_ids': len(rules),
                'build232_verified_contexts': contexts, 'repair_implementation_unchanged': True,
                'source_files': {p: sha(ROOT / p) for p in sources},
                'evidence_files': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(evidence)) if p.is_file()},
                'full_goal_completed': False}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ['source_files', 'evidence_files', 'build232_verified_contexts']}))


if __name__ == '__main__':
    main()

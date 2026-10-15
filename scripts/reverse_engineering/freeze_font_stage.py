"""Freeze font evidence and publish only a sanitized private-case receipt."""
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
    out = base / 'stage-v0217-final'
    log = base / 'regression-v0217-final.log'
    text = log.read_text(encoding='utf-8')
    assert '\nOK\n' in text
    tests = int(re.search(r'Ran (\d+) tests', text)[1])
    rules = load_rule_registry()
    contexts = []
    for rule in rules.values():
        for key in rule.get('verification_by_build', {}).get('232', {}):
            fmt, mode = key.split(':')
            assert context_evidence_valid(verification_context(rule, fmt, mode, 232))
            contexts.append(rule['rule_id'] + '/' + key)
    assert sha(ROOT / 'scripts/repair_build232.py') == '1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
    audit = json.loads((base / 'font-audit-r1/audit.json').read_text())
    assert audit['status'] == 'passed_native232_font_counter_role_and_inheritance_audit'
    assert len(audit['cases']) == 29 and all(c['both_font_families_agree'] for c in audit['cases'])
    for p, digest in audit['sources'].items():
        assert sha(ROOT / p) == digest, p
    modes = {mode: sum(c['work_type'] == mode for c in audit['cases']) for mode in ['master', 'phd']}
    assert modes == {'master': 21, 'phd': 8}
    smoke = json.loads((base / 'font-mcp-final/receipt.json').read_text())
    assert smoke['server_version'] == '0.2.17' and len(smoke['cases']) == 5
    assert all(c['two_families_and_three_counters_agree'] for c in smoke['cases'])
    private = ROOT.parent / 'private_trials/2026-10-15'
    trial = private / 'cross_v0217_final'
    summary_path = trial / 'summary.private.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    assert summary['processed_cases'] == 17 and summary['error_cases'] == 0 and not summary['errors']
    for p, digest in summary['implementation_sha256'].items():
        assert sha(ROOT / p) == digest, p
    baseline = json.loads((private / 'cross_v0215/summary.private.json').read_text(encoding='utf-8-sig'))
    inventory = json.loads((private / 'inventory.private.json').read_text(encoding='utf-8-sig'))
    for c in summary['cases']:
        cid = c['case']
        assert c['source_sha256'] == next(b['source_sha256'] for b in baseline['cases'] if b['case'] == cid)
        item = [i for i in inventory if i.get('sha256') == c['source_sha256']]
        assert len(item) == 1 and sha(Path(item[0]['path'])) == c['source_sha256']
        assert sha(trial / 'cases' / (cid + '.local.json')) == c['local_report_sha256']
        assert sha(trial / 'cases' / (cid + '.comparison.json')) == c['comparison_sha256']
        assert c['font_size_counts_v0215'] == c['font_size_counts_v0217']
    assert summary['native_totals'] == {'diagnostics': 80, 'unmapped': 0}
    assert summary['font_size_diagnostics_v0217_total'] == summary['font_size_diagnostics_v0215_total'] == 16
    chain = ROOT / 'docs/RULE_CHAIN.zh.md'
    value = re.sub(r'当前注册表包含\d+个规则ID；build232有\d+个独立',
                   f'当前注册表包含{len(rules)}个规则ID；build232有{len(contexts)}个独立', chain.read_text(encoding='utf-8'))
    chain.write_text(value, encoding='utf-8', newline='\n')
    out.mkdir(exist_ok=False)
    receipt = {
        'private_summary_sha256': sha(summary_path),
        'processed_cases': summary['processed_cases'], 'error_cases': summary['error_cases'],
        'native_totals': summary['native_totals'],
        'font_size_diagnostics_current': summary['font_size_diagnostics_v0217_total'],
        'font_size_diagnostics_baseline': summary['font_size_diagnostics_v0215_total'],
        'source_identity_mismatches': 0, 'per_case_font_count_changes': 0,
        'implementation_sha256': summary['implementation_sha256'],
        'limits': 'Retained native captures reused; no native rerun. Mapping and unchanged counts do not establish accuracy. Private source paths, content and diagnostics excluded.'}
    (out / 'private-case-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    (out / 'REPORT.zh.md').write_text(f'''# v0.2.17 验收

{tests}项回归通过，Skill结构验证通过；{len(audit['cases'])}次原程序字号运行（硕士{modes['master']}、博士NKR {modes['phd']}）核对实际计数分支、最终字号诊断和定位；{len(smoke['cases'])}个实际MCP调用与保留的同输入原程序记录一致。当前注册{len(rules)}个规则ID，232精确验证上下文{len(contexts)}项，源码/证据哈希均通过。

字号按UTF16代码单元计数并包含空格；普通小字为4<pt<8，tiny为0<pt<=4并单独计数，大字为pt>18且受角色状态门限制；普通小字/大字计数严格>10才报告。简单文本框大字取此前已处理字符数>100，不能用最终总字符数替代。修正空格/表情漏计、tiny误并入普通小字及外层run重复拥有文本框文字；保留段落和字符样式继承对照。

17份真实案例重新执行本地检查，源哈希与旧基线一致、0错误；字号诊断16对16且逐例不变，原生80条诊断全部映射。此处复用已有原生记录，映射成功和数量不变不能证明准确率，也不把案例作为学校标准。公开仅脱敏收据，论文和逐例报告留在私有目录。

仅开放受限DOCX硕士/博士NKR字号检测上下文。复杂公式、域、修订、额外故事、一般表格/绘图/PDF等仍待独立验证。原生AC/c8标志完整语义尚未确定，不宣称上标或表格普遍豁免。伪源码是带地址的分析重建，不是作者原始源代码。

自动修复权限不扩大，修复实现哈希保持不变；原论文/EXE未修改。原生后台包装器仍依赖原EXE，完整独立复刻目标未完成。
''', encoding='utf-8', newline='\n')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    new = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    sources = sorted({p for p in tracked + new if p and not p.startswith('evidence/') and (ROOT / p).is_file()})
    evidence = [p for d in base.glob('font*') if d.is_dir() for p in d.rglob('*') if p.is_file()]
    evidence += [base / 'regression-v0217-r1.log', log, out / 'REPORT.zh.md', out / 'private-case-receipt.json']
    manifest = {'release': '0.2.17', 'regression_tests_passed': tests,
                'native_valid_new_cases': len(audit['cases']), 'native_modes': modes,
                'actual_mcp_cases': len(smoke['cases']), 'private_cases_rechecked': summary['processed_cases'],
                'registered_rule_ids': len(rules), 'build232_verified_contexts': contexts,
                'source_files': {p: sha(ROOT / p) for p in sources},
                'evidence_files': {p.relative_to(ROOT).as_posix(): sha(p) for p in evidence},
                'repair_implementation_unchanged': True, 'full_goal_completed': False}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ['source_files', 'evidence_files', 'build232_verified_contexts']}))


if __name__ == '__main__':
    main()

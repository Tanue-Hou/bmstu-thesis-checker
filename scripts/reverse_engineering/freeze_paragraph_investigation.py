"""Freeze the validated investigation without claiming a production rule release."""
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
    out = base / 'paragraph-stage-r1'
    audit = json.loads((base / 'paragraph-audit-r1/audit.json').read_text())
    assert audit['status'] == 'passed_bounded_independent_paragraph_model_native_comparison'
    assert audit['native_executions'] == len(audit['cases']) == 45
    for name, digest in {**audit['sources'], **audit['implementation_sha256']}.items():
        assert sha(ROOT / name) == digest, name
    assert len({row['sha256'] for row in audit['cases']}) == 29
    assert all(row['three_families_agree'] for row in audit['cases'])
    contexts = []
    for rule in load_rule_registry().values():
        for key in rule.get('verification_by_build', {}).get('232', {}):
            fmt, mode = key.split(':')
            assert context_evidence_valid(verification_context(rule, fmt, mode, 232))
            contexts.append(rule['rule_id'] + '/' + key)
    assert len(contexts) == 13
    assert sha(ROOT / 'scripts/repair_build232.py') == '1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
    tests = {}
    for name in ['paragraph-model-tests-r1.log', 'paragraph-harness-tests-r1.log']:
        text = (base / name).read_text(encoding='utf-8')
        assert '\nOK\n' in text
        tests[name] = int(re.search(r'Ran (\d+) tests', text)[1])
    assert sum(tests.values()) == 16
    review = json.loads((base / 'paragraph-antigravity-review-r1/receipt.json').read_text())
    response = json.loads((base / 'paragraph-antigravity-review-r1/response.json').read_text(encoding='utf-8'))
    assert review['exit_code'] == 0 and response['status'] == 'SUCCESS'
    out.mkdir(exist_ok=False)
    (out / 'REPORT.zh.md').write_text('''# 段落逆向调查阶段验收

45次有效原程序执行，29个唯一输入；三个独立段落计数与原生计数、实际报告分支及原文诊断一致。此前新增探针的一次空字符串读取失败已排除，原始失败仍留存；成功记录不覆盖旧记录。

16项相关测试通过，Skill结构验证通过。原有13个232检测上下文的源码/证据哈希仍有效，修复实现哈希不变。本次不是新的生产规则版本，MCP/插件版本仍0.2.17，首行缩进、长文档与复杂内容未完成。

47个生产检查器诊断族差异实例（43本地独有、4原生独有）来自重复合成基线和角色/边界扰动，不代表真实论文误报率。独立实验CLI及Skill路径供进一步验证；生产整合需扩大状态/样式覆盖并重验真实案例与MCP。

公开内容均为合成文档和技术证据；未上传原程序或论文。Antigravity早期技术复核中的错误换算猜测已明确更正，最终结论以原始指令和断点观察为准。完整独立复刻目标未完成。
''', encoding='utf-8', newline='\n')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    new = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    sources = sorted({p for p in tracked + new if p and not p.startswith('evidence/') and (ROOT / p).is_file()})
    evidence = sorted(p for p in base.rglob('paragraph*') if p.is_file())
    evidence += [p for directory in base.glob('paragraph*') if directory.is_dir() and directory != out for p in directory.rglob('*') if p.is_file()]
    evidence += [out / 'REPORT.zh.md']
    manifest = {'stage': 'paragraph-investigation-r1', 'native_executions': 45, 'unique_input_hashes': 29,
                'targeted_tests_passed': tests, 'production_version': '0.2.17',
                'production_rule_promotion': False, 'repair_permission_expanded': False,
                'existing_verified_contexts_still_valid': contexts,
                'source_files': {p: sha(ROOT / p) for p in sources},
                'evidence_files': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(evidence))},
                'full_goal_completed': False}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'native_executions': 45, 'unique_inputs': 29, 'targeted_tests': sum(tests.values()),
                      'source_files': len(sources), 'evidence_files': len(manifest['evidence_files']),
                      'production_rule_promotion': False, 'full_goal_completed': False}))


if __name__ == '__main__':
    main()

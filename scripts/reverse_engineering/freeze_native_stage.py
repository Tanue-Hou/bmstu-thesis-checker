"""Hash this native-reference stage without including original binaries/private inputs."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    base=ROOT/'evidence/business-map-232';out=base/'stage-v029-final';out.mkdir(exist_ok=False)
    evidence=[p for p in base.rglob('*') if p.is_file() and out not in p.parents and p.suffix.lower()!='.exe']
    evidence.extend(p for p in (ROOT/'evidence/locale-loader-il-20261015').rglob('*') if p.is_file() and p.suffix.lower()!='.exe')
    paths=[ROOT/p for p in ['README.md','.gitignore','.codex-plugin/plugin.json','mcp/server.py','scripts/native_reference_cli.py','scripts/repair_build232.py','skills/bmstu-thesis-checker/SKILL.md','docs/NATIVE_REFERENCE_CLI.zh.md','docs/AGENT_CLI.zh.md','docs/RULE_CHAIN.zh.md','docs/VERSION_HISTORY.zh.md','releases/v0.2.9.md','tests/test_native_reference.py','tests/test_regression.py']]
    paths.extend(p for p in (ROOT/'scripts/reverse_engineering').iterdir() if p.is_file() and p.suffix in ['.py','.java','.cs'])
    regression=(base/'regression-v029-final.log').read_text(encoding='utf-8');assert regression.rstrip().endswith('OK');count=int(re.findall(r'Ran (\d+) tests',regression)[-1])
    smoke=json.loads((base/'native-mcp-smoke-final/receipt.json').read_text())
    proof=json.loads((base/'native-business-verification-r2/verification.json').read_text())
    final_doc=base/'STAGE_v029_FINAL.zh.md'
    final_doc.write_text(f'''# v0.2.9 最终验收

回归 {count} 项通过；Skill quick validation 通过。MCP 现有 {smoke['tool_count']} 个工具，实际原生调用返回复杂匿名 DOCX 的 {smoke['diagnostic_count']} 条诊断。源 DOCX 与 EXE 哈希保持不变。

四组硕士篇幅边界的最新记录在 `native-volume-*-r3/`，有实际选择阈值、计数、分母、最终候选和不足分支。复杂案例最新记录在 `native-direct-complex-reference-r3/`；原生 {proof['complex_reference']['numbered_diagnostics']} 条诊断与旧俄语环境证据完整匹配，原截图哈希也已核对。独立核查见 `native-business-verification-r2/verification.json`。

最终复核增加报告完整性防护：`WM_GETTEXT` 返回字符数、字符串长度、读取前后长度必须一致，CLI 还核对原文 UTF-16 长度和长度回执。空白、不完整、编号断裂、缺少完成返回或发生访问异常都拒绝报成功。保留原始 CRLF，避免 Unicode 计数失真。

受控主线程入口现在只用零载荷消息触发，转入共享检查函数前不会消费拖放句柄；不传递跨进程全局内存。只追踪本次创建的进程。CLI 的 DOCX、EXE 和辅助程序副本均在私有目录，不上传 Git。

`stage-v029-final/manifest.json` 是最终源码及证据哈希入口；`stage-v029/` 是上述报告防护复核前的历史快照，不应作为当前源码验收。历史原始记录与失败尝试均保留。

本轮没有扩大自动修复动作。原生包装器仍依赖 TestVkr232，仅开放64位 Windows、64位 Python、硕士 DOCX。博士/PDF、更多真实案例和独立复刻的完整等价尚未完成，总目标继续保留。
''',encoding='utf-8')
    evidence.append(final_doc)
    acceptance=json.loads((ROOT/'evidence/v028/complex-repair/acceptance.json').read_text());assert sha(ROOT/'scripts/repair_build232.py')==acceptance['implementation_sha256']
    report={'release':'0.2.9','evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(evidence))},'source_files':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths))},'regression_tests_passed':count,'native_mcp_tools':json.loads((base/'native-mcp-smoke-final/receipt.json').read_text())['tool_count'],'repair_implementation_unchanged':True,'limits':'Final source/evidence receipt supersedes pre-review stage-v029. Does not certify complete native equivalence. Private inputs and original executables excluded.'}
    (out/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'evidence_files':len(report['evidence_files']),'source_files':len(report['source_files']),'regression_tests_passed':count,'repair_implementation_unchanged':True}))
if __name__=='__main__':main()

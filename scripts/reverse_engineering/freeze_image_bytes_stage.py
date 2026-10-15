"""Freeze measured byte-size predicates and retain the full-goal gap boundary."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from check_document import load_rule_registry,verification_context,context_evidence_valid
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'evidence/business-map-232';out=base/'stage-v0212-final';out.mkdir(exist_ok=False)
 log=base/'regression-v0212-final.log';s=log.read_text(encoding='utf-8');assert '\nOK\n' in s;count=int(re.search(r'Ran (\d+) tests',s)[1]);rules=load_rule_registry()
 for rule,kind in [('Pic.FileSizeTooLarge','docx'),('Pic.PixelSizeTooLarge','docx'),('Pic.PixelSizeTooLarge','pdf')]:assert context_evidence_valid(verification_context(rules[rule],kind,'phd',232))
 repair=ROOT/'scripts/repair_build232.py';assert sha(repair)=='1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
 audit=json.loads((base/'image-bytes-audit-r1/audit.json').read_text(encoding='utf-8'));smoke=json.loads((base/'image-bytes-mcp-r1/receipt.json').read_text(encoding='utf-8'));assert smoke['server_version']=='0.2.12'
 (out/'REPORT.zh.md').write_text(f'''# v0.2.12 验收

回归{count}项通过，Skill验证通过。{len(audit['cases'])}个原生合成案例记录逐图ZIP本地头、无符号比较、触发分支与报告计数；同输入实际MCP原生/独立引擎各返回1条图片大小诊断。源码与证据哈希均冻结，原论文、原EXE未修改，私有报告不上传。

严格阈值30,000,000字节，文字独立写40Mb；29,999,999和30,000,000不触发，30,000,001触发。2×22,000,000聚合不触发；flags8/本地0/中央30,000,001也不触发。ZIP CRC验证通过，没有伪造本地头大小。有效PNG在IEND后填充以隔离像素数与字节数。

纠正旧累计40MiB本地模型的一个误报反例和一个漏报反例；不是实际论文准确率统计，也不证明原生230与232相同。232DOCX本地模型使用逐引用条目字段，旧230/PDF本地模型保持历史待验证状态。结构化阈值与源位置区分真实比较、原生文字和实际资源大小，去除未经证实的防查重关联。

新增验证仅232/docx:phd普通RGB8 PNG配置，限1–2图、压缩方法8、flags0/8，排除ZIP64、重复条目和异常头；独立版本上下文不提升其他规则或模式。像素规则的源码绑定同步刷新并经回归核对，修复实现及权限不变。

业务地图补齐4个分析名称与ZIP读取/计数/报告链。简单静态复核由Luna协助，核心动态执行、实现和验收由主任务完成。分析伪代码不等于原作者源码。

完整目标仍未完成：形状过滤及错误哨兵、ZIP64/异常头、其他模式、其余Word/PDF/结构判据尚需继续恢复并动态验证。原生后台仍依赖原EXE，不能称完整独立复刻。字节观察点最多128次，既有跟踪通用64次限制描述针对像素点；有限案例均未触及上限。
''',encoding='utf-8')
 evidence=[]
 for folder in ['image-bytes-boundaries-r1','image-bytes-audit-r1','image-bytes-function-map-r1','image-bytes-mcp-r1']:
  evidence.extend(p for p in (base/folder).rglob('*') if p.is_file())
 evidence.extend([log,base/'regression-v0212-r1.log',out/'REPORT.zh.md'])
 sources=['README.md','CHANGELOG.md','.codex-plugin/plugin.json','mcp/server.py','scripts/check_document.py','scripts/issue_locations.py','scripts/native_reference_cli.py','scripts/repair_build232.py','scripts/testvkr-service/checkers/pictures.py','scripts/testvkr-service/parsers/docx_parser.py','scripts/testvkr-service/rules/rules_verified.json','scripts/testvkr-service/rules/rule_guidance_zh.json','skills/bmstu-thesis-checker/SKILL.md','docs/NATIVE_IMAGE_RULE_232.zh.md','docs/NATIVE_IMAGE_BYTES_232.zh.md','docs/RULE_CHAIN.zh.md','docs/VERSION_HISTORY.zh.md','releases/v0.2.12.md','tests/test_native_image_bytes.py']
 sources.extend('scripts/reverse_engineering/'+n for n in ['trace_startup_windows.py','verify_native_image_bytes.py','audit_native_image_bytes.py','register_native_image_bytes.py','register_native_pixel_context.py','map_image_bytes_business.py','smoke_image_bytes_mcp.py','freeze_image_bytes_stage.py'])
 manifest={'release':'0.2.12','regression_tests_passed':count,'source_files':{p:sha(ROOT/p) for p in sources},'evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in evidence},'new_verified_context':'Pic.FileSizeTooLarge/232/docx:phd','repair_implementation_unchanged':True,'full_goal_completed':False,'limits':'Finite native detection/branch evidence; no complete replica, other-mode proof or new repair permission.'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps({'tests':count,'source_files':len(sources),'evidence_files':len(evidence),'goal_complete':False}))
if __name__=='__main__':main()

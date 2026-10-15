"""Freeze final pixel-family sources, evidence, checks and remaining gap ledger."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from check_document import load_rule_registry,verification_context,context_evidence_valid
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'evidence/business-map-232';out=base/'stage-v0211-final';out.mkdir(exist_ok=False)
 log=base/'regression-v0211-final.log';text=log.read_text(encoding='utf-8');assert '\nOK\n' in text;count=int(re.search(r'Ran (\d+) tests',text)[1])
 rule=load_rule_registry()['Pic.PixelSizeTooLarge'];assert all(context_evidence_valid(verification_context(rule,kind,'phd',232)) for kind in ['docx','pdf'])
 assert verification_context(rule,'docx','master',232) is None
 repair=ROOT/'scripts/repair_build232.py';assert sha(repair)=='1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
 smoke=json.loads((base/'pixel-mcp-default-r1/receipt.json').read_text(encoding='utf-8'));assert smoke['status']=='actual_native_and_independent_pixel_mcp_pass' and smoke['server_version']=='0.2.11'
 (out/'REPORT.zh.md').write_text(f'''# v0.2.11 验收与目标进度

回归{count}项通过，Skill校验通过；同输入实际MCP原生参考返回{smoke['native_diagnostics']}条诊断，本地图片计数{smoke['local_pixel_count']}，其232验证范围绑定到博士单页RGB PNG PDF。自动修图资格为false。原论文和原EXE未改动，私有报告未上传。

业务地图包含9个分析名称，部分仍为静态候选；没有声称全部函数已恢复语义。图片像素判据已追到getter值、signed32乘积、严格比较、输出标志、汇总计数和报告文字。6个DOCX/PDF正反边界与3个最终标志/计数案例均保留。最新源代码的实际MCP跟踪在pixel-mcp-default-r1/native。

像素单位控制/处理只改变匹配字面量的代码页936→1251，输出单位恢复俄语。早期控制组宽高标签顺序有误，getter寄存器和乘积未错；后续边界与最终记录明确+0x24为高度、+0x30为宽度。早期记录中的“只有词库代码页干预”通用说明未涵盖新增字面量，具体干预字段及本报告为准。

PDF资源别名按页面/XObject去重，真实bboxes保留。验证配置排除遮罩、透明PNG、组内多blip、损坏PNG、重复摆放、矢量以及溢出输入。232未验证规则不再显示旧230验证范围；旧230仍按原证据工作。

原生包装器仍依赖原EXE，独立引擎仅新增一个图片判据的两个232上下文。总目标继续进行，尚未完成全业务重建和任意论文等价。副本修复实现及权限未扩大。

下一项最明确差异是图片文件大小分支：静态读ZIP本地头未压缩大小并比较30,000,000，而报告写40Mb，本地则累计图片字节。需要动态确认边界、条目过滤、聚合方式与错误哨兵；当前不改变此规则或宣称已验证。
''',encoding='utf-8')
 evidence=[]
 for folder in ['pixel-boundaries-r1','pixel-audit-r1','pixel-audit-r2','pixel-final-r1','pixel-function-map-r1','pixel-mcp-default-r1']:
  evidence.extend(p for p in (base/folder).rglob('*') if p.is_file())
 evidence.extend([base/'regression-v0211-r1.log',log,out/'REPORT.zh.md'])
 sources=['README.md','CHANGELOG.md','.codex-plugin/plugin.json','mcp/server.py','scripts/native_reference_cli.py','scripts/check_document.py','scripts/repair_build232.py','scripts/testvkr-service/checkers/pictures.py','scripts/testvkr-service/parsers/docx_parser.py','scripts/testvkr-service/parsers/pdf_parser.py','scripts/testvkr-service/rules/rules_verified.json','skills/bmstu-thesis-checker/SKILL.md','docs/NATIVE_REFERENCE_CLI.zh.md','docs/NATIVE_IMAGE_RULE_232.zh.md','docs/RULE_CHAIN.zh.md','docs/VERSION_HISTORY.zh.md','releases/v0.2.11.md','tests/test_native_pixels.py','tests/test_graduate_structure.py']
 sources.extend('scripts/reverse_engineering/'+name for name in ['trace_startup_windows.py','verify_native_pixels.py','audit_native_pixels.py','register_native_pixel_context.py','map_pixel_business.py','publish_pixel_final.py','smoke_pixel_mcp.py','freeze_pixel_stage.py'])
 manifest={'release':'0.2.11','regression_tests_passed':count,'source_files':{p:sha(ROOT/p) for p in sources},'evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in evidence},'new_verified_build232_contexts':['Pic.PixelSizeTooLarge/docx:phd','Pic.PixelSizeTooLarge/pdf:phd'],'repair_implementation_unchanged':True,'full_goal_completed':False,'limits':'Bounded image predicate/encoding proof; no full replica, all-input equality or new repair permission.'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps({'tests':count,'source_files':len(sources),'evidence_files':len(evidence),'goal_complete':False}))
if __name__=='__main__':main()

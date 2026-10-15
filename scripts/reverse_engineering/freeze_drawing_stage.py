"""Freeze drawing release only after regression, MCP and evidence gates pass."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import load_rule_registry,verification_context,context_evidence_valid
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'evidence/business-map-232';out=base/'stage-v0213-final'
 log=base/'regression-v0213-final.log';text=log.read_text(encoding='utf-8');assert '\nOK\n' in text;count=int(re.search(r'Ran (\d+) tests',text)[1])
 rules=load_rule_registry();contexts=[]
 for rule in rules.values():
  for key,ctx in rule.get('verification_by_build',{}).get('232',{}).items():
   fmt,mode=key.split(':');assert context_evidence_valid(verification_context(rule,fmt,mode,232));contexts.append(rule['rule_id']+'/'+key)
 repair=ROOT/'scripts/repair_build232.py';assert sha(repair)=='1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
 smoke=json.loads((base/'drawing-mcp-final/receipt.json').read_text(encoding='utf-8'));assert smoke['server_version']=='0.2.13' and len(smoke['cases'])==3
 audit=json.loads((base/'drawing-audit-r1/audit.json').read_text(encoding='utf-8'));assert len(audit['cases'])==15
 chain=ROOT/'docs/RULE_CHAIN.zh.md';s=chain.read_text(encoding='utf-8');s=re.sub(r'当前注册表包含.*?此统计不代表每项规则适用于所有格式、所有论文或所有内容结构。',f'当前注册表包含{len(rules)}个规则ID；build232有{len(contexts)}个独立格式/论文类型验证上下文，均受数据配置和哈希校验约束。数量由发布冻结脚本读取注册表计算。此统计不代表每项规则适用于所有格式、所有论文或所有内容结构。',s);chain.write_text(s,encoding='utf-8',newline='\n')
 out.mkdir(exist_ok=False)
 (out/'REPORT.zh.md').write_text(f'''# v0.2.13 验收

{count}项回归通过，Skill结构验证通过；{len(audit['cases'])}个原程序实际合成DOCX输入完成四条绘图诊断对照，{len(smoke['cases'])}个实际MCP调用按相同输入哈希核对保留原生结果。当前注册{len(rules)}个规则ID，232上下文{len(contexts)}项，均检查证据及实现哈希。

本轮确认wrapNone面积float32累加、wrapSquare计数但面积0、500等值不报；小文本框宽或高小于2mm且数量超过10才报，普通7pt正文不属于此诊断。浮动图形与浮动文字独立保留。分析伪代码及旧槽命名纠正在drawing-audit-r1和文档中；不冒充原作者源码。

首次完整回归发现新规则缺少历史注册表要求的observed_message字段，已补齐并保留失败日志；最终全量重跑通过。绘图配置之外保持pending或unassessed；未知环绕不因测量不足而报面积异常。

自动修复实现哈希保持不变，所有绘图修复关闭。原论文/EXE未改，公开仅合成样本及受限技术证据；实际MCP原始响应保留本地并公开摘要哈希。后台原生包装器仍依赖原EXE；没有完成所有图形、Word/PDF和结构分支的独立复刻，不宣称学校合规或总体准确率。
''',encoding='utf-8',newline='\n')
 sources=['README.md','CHANGELOG.md','.codex-plugin/plugin.json','mcp/server.py','scripts/check_document.py','scripts/issue_locations.py','scripts/native_reference_cli.py','scripts/repair_build232.py','scripts/testvkr-service/checkers/pictures.py','scripts/testvkr-service/parsers/docx_parser.py','scripts/testvkr-service/parsers/drawing_geometry.py','scripts/testvkr-service/rules/rules_verified.json','scripts/testvkr-service/rules/rule_guidance_zh.json','skills/bmstu-thesis-checker/SKILL.md','docs/NATIVE_DRAWINGS_232.zh.md','docs/RULE_CHAIN.zh.md','docs/VERSION_HISTORY.zh.md','releases/v0.2.13.md','tests/test_native_drawings.py']
 sources+=['scripts/reverse_engineering/'+name+'.py' for name in ['trace_startup_windows','generate_drawing_probes','verify_native_drawings','audit_native_drawings','register_native_drawings','verify_drawing_mcp','freeze_drawing_stage']]
 evidence=[p for d in base.glob('drawing*') if d.is_dir() for p in d.rglob('*') if p.is_file()]+[log,base/'regression-v0213-r1.log',out/'REPORT.zh.md']
 manifest={'release':'0.2.13','regression_tests_passed':count,'registered_rule_ids':len(rules),'build232_verified_contexts':contexts,'source_files':{p:sha(ROOT/p) for p in sources},'evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in evidence},'repair_implementation_unchanged':True,'full_goal_completed':False}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'tests':count,'rule_ids':len(rules),'contexts232':len(contexts),'source_files':len(sources),'evidence_files':len(evidence)}))
if __name__=='__main__':main()

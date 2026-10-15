"""Freeze bounds evidence and a sanitized receipt of private-case cross-checks."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import load_rule_registry,verification_context,context_evidence_valid
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'evidence/business-map-232';out=base/'stage-v0215-final';log=base/'regression-v0215-r1.log';text=log.read_text(encoding='utf-8');assert '\nOK\n' in text;tests=int(re.search(r'Ran (\d+) tests',text)[1]);rules=load_rule_registry();contexts=[]
 for rule in rules.values():
  for key in rule.get('verification_by_build',{}).get('232',{}):
   fmt,mode=key.split(':');assert context_evidence_valid(verification_context(rule,fmt,mode,232));contexts.append(rule['rule_id']+'/'+key)
 assert sha(ROOT/'scripts/repair_build232.py')=='1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
 audit=json.loads((base/'textbox-bounds-audit-r1/audit.json').read_text());assert len(audit['cases'])==13 and all(r['four_families_agree'] for r in audit['cases'])
 smoke=json.loads((base/'textbox-bounds-mcp-final/receipt.json').read_text());assert smoke['server_version']=='0.2.15' and len(smoke['cases'])==5
 private=ROOT.parent/'private_trials/2026-10-15/cross_v0215';summary=private/'summary.private.json';s=json.loads(summary.read_text(encoding='utf-8'));assert s['processed_cases']==s['expected_cases']==17 and s['error_cases']==0
 for p,d in s['implementation_sha256'].items():assert sha(ROOT/p)==d,p
 files={sha(p):p for p in (private/'cases').glob('*.json')}
 for row in s['cases']:
  local=json.loads(files[row['local_report_sha256']].read_text(encoding='utf-8'));assert local['source_sha256']==row['source_sha256'];assert row['comparison_sha256'] in files
 native_count=sum(r['native_diagnostics'] for r in s['cases']);unmapped=sum(r['native_unmapped'] for r in s['cases']);drawing=sum(r['native_drawing_diagnostics'] for r in s['cases'])
 out.mkdir(exist_ok=False)
 receipt={'status':'same_input_private_cross_check_completed','cases':len(s['cases']),'errors':s['error_cases'],'native_diagnostics':native_count,'native_unmapped':unmapped,'native_drawing_diagnostics':drawing,'summary_sha256':sha(summary),'implementation_sha256':s['implementation_sha256'],'limits':'Retained build232 native captures, not new native executions. Family mapping is not semantic equivalence, school compliance, accuracy or recall. No private filenames/content published.'}
 (out/'private-cross-check-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
 chain=ROOT/'docs/RULE_CHAIN.zh.md';v=chain.read_text(encoding='utf-8');v=re.sub(r'当前注册表包含\d+个规则ID；build232有\d+个独立',f'当前注册表包含{len(rules)}个规则ID；build232有{len(contexts)}个独立',v);chain.write_text(v,encoding='utf-8',newline='\n')
 (out/'REPORT.zh.md').write_text(f'''# v0.2.15 验收

{tests}项回归、Skill结构验证通过；{len(audit['cases'])}个原程序输入的尺寸阈值/实际分支/计数/报告完成四类同输入核对；{len(smoke['cases'])}个实际MCP调用与相同输入保留原生结果一致。注册{len(rules)}个规则ID、232精确验证上下文{len(contexts)}项，所有相关证据及实现哈希通过。

新增文本框尺寸越界：纵向宽177/高254等值不触发，紧邻上界触发；横向基础交换实际观测。尺寸越界绕过小框分支，修正长窄框误报。位置越界是另一条路径，不合并成尺寸诊断。一般图形越界、横向完整邻界和复杂布局尚未恢复。

Luna复查{len(s['cases'])}份真实案例，{s['error_cases']}错误，{native_count}条保留原生诊断中未映射{unmapped}条、绘图诊断{drawing}条。主任务独立核对实现哈希与逐例本地/对照文件哈希。此组没有原生绘图诊断，不能作为新绘图规则的真实论文准确率证明。私人报告仅本地，公开摘要不含文件名或论文内容。

原论文/EXE不变；绘图自动修复关闭，修复实现哈希不变。后台对照仍依赖原EXE，完整独立复刻目标仍未完成。
''',encoding='utf-8',newline='\n')
 tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');new=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0');sources=sorted({p for p in tracked+new if p and not p.startswith('evidence/') and (ROOT/p).is_file()})
 evidence=[p for d in base.glob('textbox-bounds*') if d.is_dir() for p in d.rglob('*') if p.is_file()]+[log,out/'REPORT.zh.md',out/'private-cross-check-receipt.json']
 manifest={'release':'0.2.15','regression_tests_passed':tests,'native_new_cases':len(audit['cases']),'actual_mcp_cases':len(smoke['cases']),'registered_rule_ids':len(rules),'build232_verified_contexts':contexts,'source_files':{p:sha(ROOT/p) for p in sources},'evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in evidence},'repair_implementation_unchanged':True,'full_goal_completed':False}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'tests':tests,'private_cases':len(s['cases']),'private_native_diagnostics':native_count,'source_files':len(sources),'evidence_files':len(evidence)}))
if __name__=='__main__':main()

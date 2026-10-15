"""Freeze shape-bounds evidence, retaining invalid experiments outside proof."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import load_rule_registry,verification_context,context_evidence_valid
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'evidence/business-map-232';out=base/'stage-v0216-final';log=base/'regression-v0216-r1.log';text=log.read_text(encoding='utf-8');assert '\nOK\n' in text;tests=int(re.search(r'Ran (\d+) tests',text)[1]);rules=load_rule_registry();contexts=[]
 for rule in rules.values():
  for key in rule.get('verification_by_build',{}).get('232',{}):
   fmt,mode=key.split(':');assert context_evidence_valid(verification_context(rule,fmt,mode,232));contexts.append(rule['rule_id']+'/'+key)
 assert sha(ROOT/'scripts/repair_build232.py')=='1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
 proof=base/'shape-bounds-audit-r2/audit.json';audit=json.loads(proof.read_text());assert len(audit['cases'])==20 and all(r['shape_family_agrees'] for r in audit['cases'])
 assert not any('shape-landscape-native-r1/' in p or 'shape-bounds-inputs-r3/landscape' in p for p in audit['sources'])
 smoke=json.loads((base/'shape-mcp-final/receipt.json').read_text());assert smoke['server_version']=='0.2.16' and len(smoke['cases'])==4 and all(r['all_compared_families_agree'] for r in smoke['cases'])
 chain=ROOT/'docs/RULE_CHAIN.zh.md';s=chain.read_text(encoding='utf-8');s=re.sub(r'当前注册表包含\d+个规则ID；build232有\d+个独立',f'当前注册表包含{len(rules)}个规则ID；build232有{len(contexts)}个独立',s);chain.write_text(s,encoding='utf-8',newline='\n')
 out.mkdir(exist_ok=False)
 (out/'REPORT.zh.md').write_text(f'''# v0.2.16 验收

{tests}项回归通过，Skill结构验证通过；{len(audit['cases'])}个有效原程序输入完成原始/所选宽高、旋转、比较界限、实际分支、计数和诊断核对；{len(smoke['cases'])}个实际MCP调用按相同输入哈希对照通过。当前注册{len(rules)}个规则ID，232精确验证上下文{len(contexts)}项，全部证据/实现哈希通过。

新增图形越界：纵向177/253、横向264/166包含等值；未越界严格门的否定必须保留，不能混成文本框的严格177/254、264/167阈值。44/45/46和90/180/270输入确认原生分箱选择尺寸，不等于渲染包围框。图形与文本框规则、原生计数槽和XML定位分开。

一批六个横向输入被生成器变量冲突污染，已标为无效边界实验并排除于所有本项验证引用；纠正后六个完整邻界重新执行。失败输入/原输出保留，新增意图尺寸断言及生成器回归检查，不改写旧哈希。

Luna协助静态初阅，主任务以原始指令控制流与动态等值分支复核包含等值的结论。四个调整字段的inset别名尚未确证，偏移和值为准；一般VML/DrawingML、组合、未知角度/调整、PDF图形及其他模式仍未完成。

全部绘图自动修复关闭，修复实现哈希保持不变；原论文/EXE未修改，公开只有合成样本与技术证据。原生后台包装器依赖原EXE，完整独立复刻目标仍未完成。
''',encoding='utf-8',newline='\n')
 tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');new=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0');sources=sorted({p for p in tracked+new if p and not p.startswith('evidence/') and (ROOT/p).is_file()})
 evidence=[p for d in base.glob('shape*') if d.is_dir() for p in d.rglob('*') if p.is_file()]+[log,out/'REPORT.zh.md']
 manifest={'release':'0.2.16','regression_tests_passed':tests,'native_valid_new_cases':len(audit['cases']),'invalid_boundary_cases_retained_not_verified':6,'actual_mcp_cases':len(smoke['cases']),'registered_rule_ids':len(rules),'build232_verified_contexts':contexts,'source_files':{p:sha(ROOT/p) for p in sources},'evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in evidence},'repair_implementation_unchanged':True,'full_goal_completed':False}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'tests':tests,'source_files':len(sources),'evidence_files':len(evidence),'full_goal_complete':False}))
if __name__=='__main__':main()

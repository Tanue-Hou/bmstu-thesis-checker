"""Freeze exact textbox release source/evidence after measured checks."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import load_rule_registry,verification_context,context_evidence_valid
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'evidence/business-map-232';out=base/'stage-v0214-final';log=base/'regression-v0214-r1.log';text=log.read_text(encoding='utf-8');assert '\nOK\n' in text;tests=int(re.search(r'Ran (\d+) tests',text)[1]);rules=load_rule_registry();contexts=[]
 for rule in rules.values():
  for key in rule.get('verification_by_build',{}).get('232',{}):
   fmt,mode=key.split(':');assert context_evidence_valid(verification_context(rule,fmt,mode,232));contexts.append(rule['rule_id']+'/'+key)
 assert sha(ROOT/'scripts/repair_build232.py')=='1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
 audit=json.loads((base/'textbox-audit-r1/audit.json').read_text());assert len(audit['cases'])==32 and all(r['all_three_families_agree'] for r in audit['cases'])
 smoke=json.loads((base/'textbox-mcp-final/receipt.json').read_text());assert smoke['server_version']=='0.2.14' and len(smoke['cases'])==5
 out.mkdir(exist_ok=False)
 (out/'REPORT.zh.md').write_text(f'''# v0.2.14 验收

{tests}项回归通过；{len(audit['cases'])}个新增原程序DOCX/NKR输入逐项尺寸、宽高分支、计数和三类诊断一致；{len(smoke['cases'])}个实际MCP调用按同输入哈希与保留原生结果核对通过。Skill结构验证通过。

恢复单位换算函数0041a204及float32常数，补厘米/磅/英寸/无单位的2mm正例、等值和反例；形状层自适应启用会把有效高度设10mm，宽度小于2mm仍计入。同样textbox层值在本轮输入未设置标志。空文本、长文本、有限inset与较大矩形单因素对照保留。

px原生换算已复现，但没有负例/等值测试；pc只有静态证据，二者不提升验证。越界分支静态找到但本轮未触发，fc排除标志语义、组合/旋转、DrawingML/PDF图形和更多模式仍需恢复。验证配置之外保持pending或unassessed，不宣称完整复刻、总体准确率或学校合规。

三项分析函数命名有静态/动态对应；Luna协助只读初步梳理，主任务核对二进制指令、常数、实际分支并完成验收。分析伪代码不是原作者手写源码。原论文与EXE未改，修复实现哈希不变，绘图修复关闭。
''',encoding='utf-8',newline='\n')
 tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');new=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
 sources=sorted({p for p in tracked+new if p and not p.startswith('evidence/') and (ROOT/p).is_file()})
 evidence=[p for d in base.glob('textbox*') if d.is_dir() for p in d.rglob('*') if p.is_file()]+[log,out/'REPORT.zh.md']
 manifest={'release':'0.2.14','regression_tests_passed':tests,'native_new_cases':len(audit['cases']),'actual_mcp_cases':len(smoke['cases']),'registered_rule_ids':len(rules),'build232_verified_contexts':contexts,'source_files':{p:sha(ROOT/p) for p in sources},'evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in evidence},'repair_implementation_unchanged':True,'full_goal_completed':False}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'tests':tests,'source_files':len(sources),'evidence_files':len(evidence),'full_goal_complete':False}))
if __name__=='__main__':main()

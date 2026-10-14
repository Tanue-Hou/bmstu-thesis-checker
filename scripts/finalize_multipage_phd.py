"""Final source/evidence audit, independent native counts and retained acceptance report."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/multipage-phd-repair'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    matrix=read(OUT/'comparison.json');repair=read(OUT/'repair-comparison.json');validation=read(ROOT/'evidence/2026-10-14/validation.json');assert validation['test_exit_code']==0
    for name,digest in validation['source_hashes'].items():assert sha(ROOT/name)==digest,name
    for name,c in matrix['cases'].items():
        assert sha(OUT/(name+'.'+c['format']))==c['input_sha256'];assert sha(OUT/(name+'.original.json'))==c['capture_sha256'];assert list(OUT.glob(name+'.original-*.png'))
    assert all(c['pass'] for c in matrix['checks'].values())
    registry=read(ROOT/'scripts/testvkr-service/rules/rules_verified.json');contexts=0
    for rule in registry['rules']:
        for context in rule.get('verification_by_context',{}).values():
            refs=context['evidence_refs'];assert sha(ROOT/refs[0])==context['verification_evidence_sha256']
            for ref in refs:assert sha(ROOT/ref)==context.get('evidence_hashes',{}).get(ref,context['verification_evidence_sha256']),ref
            if context.get('repair_evidence_ref'):assert sha(ROOT/context['repair_evidence_ref'])==context['repair_evidence_sha256']
            contexts+=1
    for name,c in repair['native_before_after'].items():assert sha(OUT/(name+'.original.json'))==c['sha256']
    assert repair['source_unchanged'] and repair['all_xml_changes_reversible_from_log']
    execution=read(OUT/'repair-execution.json');assert sha(Path(execution['input_file']))==repair['source_sha256'];assert sha(Path(execution['output_file']))==repair['output_sha256'];assert sha(OUT/'phd_combined_after.docx')==repair['output_sha256']
    smoke=read(OUT/'mcp-smoke.json');assert smoke['exit_code']==0 and smoke['mcp_copy_identical_to_native_checked_copy'];smokecopy=smoke['responses'][3]['result']['structuredContent'];assert sha(Path(smokecopy['output_file']))==repair['output_sha256']
    log=(ROOT/'evidence/2026-10-14/regression-test.log').read_text(encoding='utf-8');assert log.rstrip().endswith('OK');tests=int(re.search(r'Ran (\d+) tests',log)[1])
    counts={name:matrix['cases'][name]['native_diagnostics'] for name in ['structure_clean','structure_no_abstract','structure_wrong_toc']}
    before=repair['native_before_after']['phd_combined']['diagnostics'];after=repair['native_before_after']['phd_combined_after']['diagnostics']
    result={'native_input_cases':len(matrix['cases'])+1,'native_pdf_cases':sum(c['format']=='pdf' for c in matrix['cases'].values()),'native_docx_cases_including_repair':sum(c['format']=='docx' for c in matrix['cases'].values())+1,'rule_context_pairs':sum(len([k for k in c if k!='pass']) for c in matrix['checks'].values()),'local_tests_passed':tests,'source_files_hashed':len(validation['source_hashes']),'all_registry_context_hashes_checked':contexts,'pdf_upper_probes':matrix['pdf_upper_font_probes'],'pdf_structure_native_diagnostic_counts':counts,'doctoral_repair_native_before_after':[before,after],'doctoral_copy_property_changes':repair['changes'],'all_xml_changes_reversible_from_log':True,'source_unchanged':True,'mcp_version':'0.2.4','mcp_copy_identical_to_native_checked_copy':True,'git_push_performed':False}
    (OUT/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=f'''# 多页图表PDF与博士DOCX副本修复验收

现有Skill与MCP项目已更新至0.2.4。本轮{result['native_input_cases']}个原程序输入（PDF {result['native_pdf_cases']}、DOCX含修复副本{result['native_docx_cases_including_repair']}），{result['rule_context_pairs']}组规则/格式/论文类型配对通过；{tests}项本地测试通过。{result['source_files_hashed']}个源文件及{contexts}个注册表上下文的证据哈希已复核。未推送GitHub；MCP以本地stdio实际调用验证，不声称桌面已安装插件自动刷新。

## 原程序多页格式对照

3页PDF每页含普通表格和PNG图表。第2页7磅表格文字、超16000000像素图片，第3页红字、非A4纸张均触发原程序对应诊断。本地检查已返回相应页码，并将可靠范围限定为已测嵌入Times New Roman+ToUnicode、无旋转、1–3页、每页最多一张PNG。其他配置仍可做本地检查，但不提升原程序验证状态。

## 大字号上限的差异

多页PDF的18.5、19、24、36、72磅探针均有超过10个大字号字符，原程序都没有输出大字号提示；博士DOCX的18.5磅正文则明确触发超过18磅提示。恢复的PDF文字函数00477f50检查下限DAT_006ee118，但没有引用DOCX上限DAT_006ee11c。原程序共用输出分支存在大字号警告，并不证明PDF解析器会累计该类字符。不能把DOCX的18磅直接套用PDF，也不能据此断言所有PDF路径都没有上限。学校正文格式应按独立模板要求判断。

## 结构检查差异

| 分页PDF输入 | 原程序全部诊断数 | 本轮确认的结构问题 |
|---|---:|---|
| 完整标题基准（14页） | {counts['structure_clean']} | 未出现摘要/目录标题缺失；原程序仍报告页边文字、上边距与页码位置 |
| 删除摘要标题（13页） | {counts['structure_no_abstract']} | 摘要标题缺失 |
| 博士目录改为СОДЕРЖАНИЕ（14页） | {counts['structure_wrong_toc']} | ОГЛАВЛЕНИЕ缺失，另有目录解析连带诊断 |

修复本地PDF结构漏检：增加博士摘要、ОГЛАВЛЕНИЕ的独立标题识别，并规范化PDF提取的NBSP空白，消除完整参考文献标题的旧误报。保留的prechange.local.json记录三种输入原先均被误判缺少bibliography；完整标题基准修正后不再报此项。只有摘要和博士目录标题缺失有正反原程序证据；其他结构谓词继续人工复核。

剩余差异已分类保留：本地尚未实现PDF几何边距/文字落入页边、页码和页眉页脚定位、目录页码与正文标题对应、封面与参考文献完整性。native_comparison_limits与Markdown报告明确列出这些缺口。14页结构样本不扩大图表格式谓词到任意页数，本地零诊断不代表原程序通过。

## 博士副本自动修复

原程序组合样本{before}条诊断，经{repair['changes']}项有记录的属性修改后降为{after}条，原程序显示“Замечаний нет.”。CLI和MCP现在允许博士模式的A4、异常正文大小和非黑文字副本修复，限一个纵向节；不自动修博士边距、行距、缩进、结构或PDF。

原文件未变，正文文字、表格、图表、边距、其他ZIP成员均保持一致，只改word/document.xml。按changes.json逆转全部记录后，规范XML与原文档一致，未发现日志外的修改。字号目标取显式14磅，未来文档取用户指定或已知Normal样式，不能凭异常下限猜测。特殊内容、表格文字和图像不自动修改，跳过原因保留。

博士修复额外要求完整的原程序修复前后证据哈希；多节/横向输入拒绝该操作。MCP实际initialize、tools/list、预览、创建副本四次请求均成功，MCP副本与原程序已复查副本哈希一致。范围是合成图表样本，不能承诺任意论文都通过。

## 可复查入口

- comparison.json：19个修复前原程序输入、9组规则上下文配对、大字号探针。
- *.original.json / *.original-*.png：原程序实际文本与截图，含修复副本。
- inputs.json、pdf-extraction.json与生成脚本：输入参数、逐页文本/字体/图片属性及来源哈希。
- static/provenance.json及恢复函数：原程序SHA256、伪代码来源与推断边界；不是原始源代码。
- repair-comparison.json、repair-execution.json、repair_outputs/*.changes.json：原程序4→0、5项修改、源完整性及XML可逆性。
- mcp-smoke.json：实际MCP请求/响应；acceptance.json：机器计算验收数量和检查结果。
- ../2026-10-14/validation.json与regression-test.log：测试结果和源文件哈希；../manifest.json：全证据哈希。

复查顺序：verify_multipage_phd.py、verify_phd_repair.py、run_revision_validation.py、finalize_multipage_phd.py、finalize_dynamic_evidence.py。冻结的原程序对照不可由本地测试代替；所有修改都在现有项目，历史证据保留。
'''
    (OUT/'REPORT.zh.md').write_text(report,encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()

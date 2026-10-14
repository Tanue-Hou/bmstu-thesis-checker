"""Audit frozen inputs, reproducibility, captures and current validation; write a review report."""
import hashlib,json,re,zipfile
from lxml import etree
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/graduate-structure'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    matrix=json.loads((OUT/'comparison.json').read_text(encoding='utf-8'))
    capture_count=0
    for mode,cases in matrix['cases'].items():
        for name,case in cases.items():
            assert sha(ROOT/case['input'])==case['input_sha256']
            assert sha(ROOT/case['original_capture'])==case['capture_sha256']
            capture_count+=1
    reproduced=[]
    for candidate in sorted((OUT/'reproduced-v2').glob('g_*.docx')):
        original=OUT/candidate.name
        with zipfile.ZipFile(original) as a,zipfile.ZipFile(candidate) as b:
            assert a.namelist()==b.namelist()
            assert all(a.read(n)==b.read(n) for n in a.namelist()),candidate.name
        reproduced.append({'case':candidate.stem,'all_zip_member_contents_equal':True,'original_sha256':sha(original),'reproduction_sha256':sha(candidate),'note':'ZIP timestamps may differ; byte identity is asserted for every uncompressed member.'})
    (OUT/'reproduction.json').write_text(json.dumps(reproduced,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(OUT/'g_phd_correct_heading.docx') as a,zipfile.ZipFile(OUT/'g_phd_left25.docx') as b:
        changed=[name for name in a.namelist() if a.read(name)!=b.read(name)]
        assert changed==['word/document.xml']
        x,y=etree.fromstring(a.read(changed[0])),etree.fromstring(b.read(changed[0]))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};left='{'+ns['w']+'}left'
        xa,ya=x.xpath('//w:pgMar',namespaces=ns),y.xpath('//w:pgMar',namespaces=ns)
        assert len(xa)==len(ya)==1
        actual_before,actual_after=xa[0].get(left),ya[0].get(left)
        ya[0].set(left,actual_before)
        assert etree.tostring(x)==etree.tostring(y),'Left-margin probe changed other XML'
    (OUT/'phd-margin-delta.json').write_text(json.dumps({'modified_zip_parts':changed,'only_xml_attribute_changed':'w:pgMar/@w:left','before_twips':actual_before,'after_twips':actual_after,'before_sha256':sha(OUT/'g_phd_correct_heading.docx'),'after_sha256':sha(OUT/'g_phd_left25.docx')},indent=2)+'\n',encoding='utf-8')
    validation=json.loads((ROOT/'evidence/2026-10-14/validation.json').read_text(encoding='utf-8'))
    assert validation['test_exit_code']==0
    log=(ROOT/'evidence/2026-10-14/regression-test.log').read_text(encoding='utf-8')
    tests=int(re.search(r'Ran (\d+) tests',log)[1])
    summary=json.loads((OUT/'summary.json').read_text(encoding='utf-8'))
    verified={mode:sum(mode in proof and proof[mode]['pass'] for proof in matrix['checks'].values()) for mode in matrix['cases']}
    receipt={'native_cases_including_reused_baseline':capture_count,'native_cases_by_mode':summary['native_cases_by_mode'],'promoted_rule_ids':list(matrix['checks']),'verified_predicates_by_mode':verified,'reproduced_extended_inputs':len(reproduced),'tests_passed':tests,'test_exit_code':0,'matrix_sha256':sha(OUT/'comparison.json'),'static_provenance_sha256':sha(OUT/'static/provenance.json')}
    (OUT/'acceptance.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    progress=summary['master_diagnostic_progression']
    report=f'''# TestVkr 硕士／博士模式验证报告

本轮证据包括硕士 {summary['native_cases_by_mode']['master']} 个对照结果（含复用的已冻结基准）和博士 {summary['native_cases_by_mode']['phd']} 个原程序结果。新增 {len(matrix['checks'])} 项诊断判据；硕士适用 {verified['master']} 项，博士适用 {verified['phd']} 项。{tests} 项本地回归测试通过，MCP 已实际调用检查硕士和博士文件。原程序为 build 230；可复查输入、截图、输出、SHA-256 与逐项比较见 comparison.json、static/provenance.json 和 acceptance.json。

## 硕士剩余六条诊断

|原诊断|原因与对照结果|
|---|---|
|封面校名错误|原样例只有简称，不足以匹配内置 TITUL 校名模板。完整真实模板信息的合成封面对照消除了该提示。|
|封面多处不符|原样例缺少多项机构、院系、题目与人员信息。补全合成封面后消失；不能自动编造实际论文信息。|
|附录A标题缺失|加入 ПРИЛОЖЕНИЕ А 正文标题与匹配目录后消失。只证明此样例判据，不代表所有论文都应添加附录。|
|目录被判空|原样例只有4条带页码条目。实测5条转为过短，10条仍过短，11条不再过短。必须更新真实目录。|
|摘要过短|原样例只有一个非空段落；三个内容段落的对照消除了提示。俄语字符数350边界目前是静态推断，未做独立精确动态边界。|
|篇幅不足|硕士48折算页，900字符每页；各段去首尾空白，按UTF-16单位计数，从摘要标题至附录标题前。43199字符缺1页，43200字符不报警；正文足量时附录A目录页码47缺1页，48不报警。修改Word缓存页数47／48未改变结果。|

原程序诊断数依次为：基准 {progress['baseline']} → 完整封面 {progress['cover_corrected']} → 补全结构 {progress['structure_corrected']} → 满足篇幅判据 {progress['volume_corrected']}。两个边界合成样例显示“Проверка закончена. Замечаний нет.”。这是合成样例通过，不能据此认证真实论文，不能用修改目录数字代替实际分页或正文写作。

## 博士科研资格论文

界面模式为 НКР аспиранта。工作名称使用 НАУЧНО-КВАЛИФИКАЦИОННАЯ РАБОТА，目录标题必须为 ОГЛАВЛЕНИЕ。使用硕士的 СОДЕРЖАНИЕ 会造成目录缺失、无法定位正文起点和目录一致性等连带提示。改正博士封面及目录的样例只剩原程序页边距警告；只将左边距从30毫米改为25毫米后，原程序显示“无意见”。博士诊断数为 {' → '.join(str(x) for x in summary['phd']['diagnostic_progression'])}。phd-margin-delta.json 确认全DOCX仅有左边距XML属性变化。

恢复的数字篇幅分支只给工作代码0／1／2选择40／48／56；博士代码5未选择数字下限。{summary['native_cases_by_mode']['phd']}个博士样例都未触发篇幅警告。已移除博士DOCX的10万字符本地猜测，但这不等于现实博士论文没有篇幅要求。博士左边距仅验证25毫米通过／30毫米报警；右／上／下保持10／20／20毫米。没有测定边距容差，也不认证任意博士文档。

## 已整合的行为与边界

现有 check_thesis_document／check_thesis_folder 使用 work_type=master 或 phd 即可获得新诊断、中文解释和当前模式的证据引用。硕士与博士的验证状态独立；表格、图片、域、文本框、内容控件、修订及PDF不继承这批普通正文结构规则的高置信验证。

封面、真实篇幅和目录内容只提供人工修订建议。已有副本自动修复仍限已验证的本科／硕士A4、普通文字颜色及异常字号；保留原文件和逐项修改记录。博士自动格式修复未开放。

已复现 {len(reproduced)} 个自适应边界输入，每个DOCX的全部解压成员内容与冻结样例一致；完整源码不可从本轮证明恢复，静态材料为反编译伪代码和内置资源。
'''
    (OUT/'REPORT.zh.md').write_text(report,encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()

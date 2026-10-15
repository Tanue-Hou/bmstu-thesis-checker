"""Conservative action eligibility, separate from native anomaly detection.

No candidate is deleted and no native absence is interpreted as ground truth.
"""
from collections import Counter

def assess(finding, report):
    rule = finding['rule_id']
    locations = finding.get('precise_locations', {}).get('occurrences', [])
    if report.get('document_kind') == 'dissertation' and not rule.startswith('Template.'):
        return 'scope_not_applicable', '学位论文与NKR模式不同；该检测不能作为学位论文违规依据。'
    if rule.startswith('Template.'):
        return 'reference_applicability_unconfirmed', '参考配置的院系、年份适用性未确认。'
    if rule == 'Graduate.UniversityNameInvalid':
        return 'template_name_requires_review', '只确认封面与原程序词串模板不匹配；旧式机构性质词串不能代替当前学校名称要求，不自动改校名。'
    if rule in {'Word.TableRowHeightTooSmall', 'Word.TableSuspiciousHeightRule'}:
        return 'layout_property_advisory', 'XML指定行高不等于实际渲染行高；固定行高也不等于已发生裁切，先查看表格/公式页面。'
    if rule.startswith(('Dict.', 'Pic.')) or rule == 'Struct.ContainsLatex':
        return 'advisory_only', '混合字符、浮动图或技术标记本身不证明格式违规；保留上下文供复核。'
    if (rule in {'Word.FontSizeTooLarge', 'Word.FontSizeTooSmall', 'Word.TextColorNotBlack'}
            and locations and not finding.get('precise_locations', {}).get('truncated')
            and all(l.get('content_role') == 'front_matter_candidate_manual_review' for l in locations)):
        return 'special_role_requires_review', '所定位异常全部在前置页；不能按正文标准直接改写。'
    if (rule in {'Word.AlignmentNotJustified','Word.FirstLineIndentInvalid','Word.LeftIndentInvalid',
                 'Word.RightIndentInvalid','Word.LeadingWhitespace','Word.LineSpacingInvalid'}
            and locations and not finding.get('precise_locations', {}).get('truncated')
            and all(l.get('content_role') in {'front_matter_candidate_manual_review','heading_or_caption_candidate_manual_review','table_row_manual_review'}
                    or l.get('special_content') for l in locations)):
        return 'special_role_requires_review', '候选全部是前置页、标题/图题、表格或含公式/域等特殊内容；按长度推断正文不足以支持统一格式修复。'
    return 'evidence_required', '属性异常或原程序同类提示不等于学校违规；需要适用条款及页面/语义复核。'

def annotate(report):
    for finding in report['findings']:
        disposition, reason = assess(finding, report)
        finding['action_eligibility'] = {'status': disposition, 'reason_zh': reason,
                                         'automatic_repair_allowed': False}
    report['action_summary'] = dict(Counter(f['action_eligibility']['status'] for f in report['findings']))
    from repair_build232 import capability
    report['repair_capability']=capability()
    report['action_contract'] = 'Candidates retained; whole-group eligibility is not a truth verdict. Independently accepted build232 partial-run font plans are exposed separately; special roles are preserved.'
    return report

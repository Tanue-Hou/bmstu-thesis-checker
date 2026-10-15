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
    if rule.startswith(('Dict.', 'Pic.')) or rule == 'Struct.ContainsLatex':
        return 'advisory_only', '混合字符、浮动图或技术标记本身不证明格式违规；保留上下文供复核。'
    if (rule in {'Word.FontSizeTooLarge', 'Word.FontSizeTooSmall', 'Word.TextColorNotBlack'}
            and locations and not finding.get('precise_locations', {}).get('truncated')
            and all(l.get('content_role') == 'front_matter_candidate_manual_review' for l in locations)):
        return 'special_role_requires_review', '所定位异常全部在前置页；不能按正文标准直接改写。'
    return 'evidence_required', '属性异常或原程序同类提示不等于学校违规；需要适用条款及页面/语义复核。'

def annotate(report):
    for finding in report['findings']:
        disposition, reason = assess(finding, report)
        finding['action_eligibility'] = {'status': disposition, 'reason_zh': reason,
                                         'automatic_repair_allowed': False}
    report['action_summary'] = dict(Counter(f['action_eligibility']['status'] for f in report['findings']))
    report['action_contract'] = 'Candidates retained; action eligibility is not a truth verdict. Build232 repair remains closed.'
    return report

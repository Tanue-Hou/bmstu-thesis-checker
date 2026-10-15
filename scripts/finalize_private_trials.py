"""Keep private review artifacts outside Git; publish only non-identifying trial totals."""
import argparse,csv,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('private_results');a=p.parse_args();private=Path(a.private_results).resolve()
    if private.is_relative_to(ROOT):raise ValueError('Private input must remain outside repository')
    summary=json.loads((private/'summary.private.json').read_text(encoding='utf-8'))
    review=[];pdf_locations=0;pdf_in_bounds=0
    for row in summary:
        report=json.loads((private/(row['id']+'.report.private.json')).read_text(encoding='utf-8'))
        native={'status':'pending','input_sha256':report['source_sha256'],'work_type':report['work_type'],'build':230,'reason':'Computer Use failed to activate file-selection window; actual result not captured'}
        capture_path=private/(row['id']+'.native-capture.private.json')
        if not capture_path.exists():capture_path.write_text(json.dumps(native,ensure_ascii=False,indent=2),encoding='utf-8')
        if report['file_type']=='pdf':
            import fitz
            with fitz.open(report['file']) as doc:
                for f in report['findings']:
                    for loc in f['precise_locations']['occurrences']:
                        if 'bbox' in loc:
                            pdf_locations+=1;pdf_in_bounds+=int(doc[loc['page']-1].rect.contains(fitz.Rect(loc['bbox'])))
        for f in report['findings']:
            review.append({'case':row['id'],'rule':f['rule_id'],'native_status':'pending_native_capture','local_status':f['verification_status'],'locations':f['precise_locations']['occurrence_count'],'school_clause':'','source_property_review':'','page_review':'','verdict':'pending','reason':'','reviewer':'','repair_scope':''})
    if not (private/'adjudication.private.csv').exists():
        with (private/'adjudication.private.csv').open('x',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(review[0]));w.writeheader();w.writerows(review)
    aggregate={'schema_version':1,'case_count':len(summary),'pdf_cases':sum(r['source_path'].lower().endswith('.pdf') for r in summary),'docx_cases':sum(r['source_path'].lower().endswith('.docx') for r in summary),'checked':sum(r['status']=='checked' for r in summary),'source_unchanged':all(r.get('source_unchanged') for r in summary),'candidate_rule_groups':sum(r['findings'] for r in summary),'template_candidate_groups':sum(r['template_findings'] for r in summary),'groups_with_location_or_scope':sum(r['located_findings'] for r in summary),'repair_preview_changes':sum(r['repair_planned_changes'] for r in summary),'mode_review_required':sum(r['mode_needs_review'] for r in summary),'native_corpus_captures_completed':0,'adjudicated_groups':0,'pdf_sample_bboxes_checked':pdf_locations,'pdf_sample_bboxes_inside_page':pdf_in_bounds,'limits':['Cases are not ground truth; no accuracy/recall claim','No original-program pass for this corpus','Page bounds are geometry sanity only, not semantic confirmation','Private sources, names, excerpts, paths and source hashes excluded','Real documents remain unchanged; repair previews only']}
    assert aggregate['checked']==aggregate['case_count'] and aggregate['source_unchanged']
    out=ROOT/'evidence/2026-10-15';out.mkdir(parents=True,exist_ok=True);(out/'private-trial-aggregate.json').write_text(json.dumps(aggregate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (private/'CROSS_CHECK.private.md').write_text('# 案例交叉检测台账\n\n这些案例不是标准答案，所有判定仍为pending。原程序已通过俄语兼容环境启动，但文件选择窗口控制失败：failed to activate captured window。本批原诊断尚未采集，不宣称对照完成。\n\n人工判定表：adjudication.private.csv。每篇 native-capture.private.json 明确pending，取得真实输出后按公开流程录入并校验哈希。\n\n公式小字号、混合字母及结构缺失首先核对页面。封面保护后本批自动修复预览没有改动项，模板行距/缩进/边距仍需确认后处理。\n',encoding='utf-8')
    print(json.dumps(aggregate))
if __name__=='__main__':main()

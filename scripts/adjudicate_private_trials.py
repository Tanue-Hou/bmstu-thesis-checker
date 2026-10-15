"""Evidence dispositions for every retained review row; no fabricated ground truth."""
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path
from review_policy import assess
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def adjudicate(previous, reports, out):
    previous,reports,out=map(Path,(previous,reports,out))
    out=out.resolve()
    if out.is_relative_to(ROOT):raise ValueError('Private review must remain outside publishable repository')
    out.mkdir(parents=True,exist_ok=False)
    with (previous/'review.private.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    decisions=[]
    for row in rows:
        case=row['case'];report_path=reports/(case+'.report.private.json')
        report=json.loads(report_path.read_text(encoding='utf-8'))
        comparison_path=previous/(case+'.comparison.private.json')
        comparison=json.loads(comparison_path.read_text(encoding='utf-8'))
        if sha(report['file'])!=report['source_sha256']:raise ValueError('Source changed: '+case)
        evidence={'report_sha256':sha(report_path),'comparison_sha256':sha(comparison_path),'source_sha256':report['source_sha256']}
        if row['side']=='native':
            item=next(d for d in comparison['native_diagnostics'] if d['number']==int(row['index']))
            status='scope_not_applicable' if comparison['document_kind_mismatch'] else 'evidence_required'
            reason='学位论文/NKR模式不适配，原程序提示不能作为该论文违规结论。' if comparison['document_kind_mismatch'] else '原程序确实提示此项；尚需学校条款、源属性与页面语义，不能把原程序当作标准答案。'
            details={'native_message':item['message'],'page_candidates':item.get('page_candidates',[])}
        else:
            item=report['findings'][int(row['index'])]
            if item['rule_id']!=row['rule_id']:raise ValueError('Finding index drift')
            status,reason=assess(item,report)
            # A specific source normalization defect, established from the cover text.
            if item['rule_id']=='Graduate.WorkNameInvalid':
                from check_document import parse_document
                import re
                _,data=parse_document(Path(report['file']))
                records=data.get('structure_paragraphs',[])
                matches=[r for r in records[:60] if re.search(r'\bвыпускной\s+квалификационной\s+работе\b',r['text'],re.I)]
                if matches:
                    status='confirmed_local_recognition_defect'
                    reason='原文封面有“К ВЫПУСКНОЙ КВАЛИФИКАЦИОННОЙ РАБОТЕ”；本地只接受主格导致名称识别误报。只修检查器，不改论文；不证明封面整体符合学校要求。'
                    evidence['matched_cover_locations']=[{'xml_path':r['xml_path'],'text':r['text']} for r in matches]
            details={'threshold':item.get('threshold'),'precise_locations':item.get('precise_locations')}
        decisions.append({**row,'disposition':status,'decision_reason':reason,'truth_verdict':'false_positive_of_local_name_recognition' if status=='confirmed_local_recognition_defect' else 'unresolved_school_compliance',
                          'automatic_repair_allowed':False,'evidence':evidence,'details':details})
    (out/'decisions.private.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2),encoding='utf-8')
    fields=['case','side','index','rule_id','disposition','truth_verdict','decision_reason','automatic_repair_allowed']
    with (out/'decisions.private.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(decisions)
    summary={'rows':len(decisions),'dispositions':dict(Counter(d['disposition'] for d in decisions)),
             'fully_adjudicated_school_compliance':False,'accuracy':None,'repair232_open':False,
             'previous_review_sha256':sha(previous/'review.private.csv')}
    (out/'summary.private.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('previous');p.add_argument('reports');p.add_argument('--out',required=True);a=p.parse_args()
    print(json.dumps(adjudicate(a.previous,a.reports,a.out)))

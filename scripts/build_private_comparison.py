"""Reconcile private real-case outputs and retain all per-diagnostic/finding review rows."""
import argparse,csv,hashlib,html,json
from pathlib import Path
from collections import Counter
from compare_native_trial import compare,load_capture
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(manifest,local_dir,native_dir,out):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT):raise ValueError('Private case comparisons must remain outside repository')
    if out.exists() and any(out.iterdir()):raise ValueError('Use a fresh comparison directory; preserve earlier adjudication')
    out.mkdir(parents=True,exist_ok=True);rows=json.loads(Path(manifest).read_text(encoding='utf-8-sig'));summary=[];review=[]
    for row in rows:
        id=row['id'];local_path=Path(local_dir)/(id+'.report.private.json');capture_path=Path(native_dir)/(id+'.capture.json');local=json.loads(local_path.read_text(encoding='utf-8'));capture=load_capture(capture_path)
        assert sha(row['path'])==row['sha256']==local['source_sha256']==capture['input_sha256'],'Source identity changed'
        result=compare(local,capture);result['case_id']=id;result['mode_needs_review']=row.get('mode_needs_review',False)
        result['provenance']={'local_report_sha256':sha(local_path),'native_capture_sha256':sha(capture_path),'source_unchanged':True}
        for d in result['native_diagnostics']:
            review.append({'case':id,'side':'native','index':d['number'],'rule_id':d['rule_id'],'comparison_status':d['status'],'analysis':d['analysis_zh'],'verdict':'pending','reviewer':'','school_clause':'','page_evidence':'','notes':''})
        for f in result['local_findings']:
            review.append({'case':id,'side':'local','index':f['finding_index'],'rule_id':f['rule_id'],'comparison_status':f['status'],'analysis':f['analysis_zh']+' '+f['source_role_note'],'verdict':'pending','reviewer':'','school_clause':'','page_evidence':'','notes':''})
        (out/(id+'.comparison.private.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        cards=[]
        for d in result['native_diagnostics']:
            cards.append('<article><h3>原程序 '+str(d['number'])+' · '+html.escape(d['rule_id'] or '未映射')+'</h3><p>'+html.escape(d['status'])+'</p><pre>'+html.escape(d['message'])+'</pre><p>'+html.escape(d['analysis_zh'])+'</p></article>')
        for f in result['local_findings']:
            locations='\n'.join(json.dumps(l,ensure_ascii=False) for l in f['locations'][:5])
            cards.append('<article><h3>本地 '+str(f['finding_index'])+' · '+html.escape(f['rule_id'])+'</h3><p>'+html.escape(f['status'])+'</p><p>'+html.escape(f['analysis_zh']+' '+f['source_role_note'])+'</p><pre>'+html.escape(locations)+'</pre></article>')
        page='<!doctype html><meta charset="utf-8"><title>案例交叉对照</title><style>body{font:16px system-ui;max-width:1100px;margin:30px auto;background:#f5f6f8}article{background:white;padding:18px;margin:12px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere}input{padding:12px;width:95%}</style><h1>'+id+' · build '+str(capture['build'])+'</h1><p>案例不是标准答案；同类诊断不等于语义相同。学位论文PDF在NKR模式下仅为试探。判定均保留pending；完整源位置见JSON。</p><input id="q" placeholder="搜索原诊断、规则或分析"><main>'+''.join(cards)+'</main><script>q.addEventListener("input",()=>document.querySelectorAll("article").forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(q.value.toLowerCase())))</script>'
        (out/(id+'.comparison.private.html')).write_text(page,encoding='utf-8')
        summary.append({'id':id,'file':Path(row['path']).name,'native_diagnostics':len(result['native_diagnostics']),'local_findings':len(result['local_findings']),'mode_mismatch':result['document_kind_mismatch'],'mode_needs_review':result['mode_needs_review'],'unmapped_native':sum(not d['rule_id'] for d in result['native_diagnostics']),'native_categories':Counter(d['status'] for d in result['native_diagnostics']),'local_categories':Counter(f['status'] for f in result['local_findings'])})
    with (out/'review.private.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(review[0]));writer.writeheader();writer.writerows(review)
    (out/'summary.private.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    index=['# build 232 案例逐条交叉对照','','原始俄文、UIA及截图在相邻 native-build-232 目录；每条原诊断和每条本地候选都进入对照。source SHA256保持相同。CSV判定默认pending，不计算正确率。','','| 案例 | 原程序诊断 | 本地候选 | 模式限制 | 报告 |','|---|---:|---:|---|---|']
    for s in summary:index.append(f"| {s['id']} {s['file']} | {s['native_diagnostics']} | {s['local_findings']} | {'学位论文/NKR不适配' if s['mode_mismatch'] else '学位类型待确认' if s['mode_needs_review'] else '硕士模式'} | [{s['id']}]({s['id']}.comparison.private.html) |")
    (out/'INDEX.private.md').write_text('\n'.join(index),encoding='utf-8')
    aggregate={'build':232,'cases':len(summary),'source_unchanged':True,'native_captures':len(summary),'native_diagnostics':sum(s['native_diagnostics'] for s in summary),'local_findings':sum(s['local_findings'] for s in summary),'mode_mismatch_cases':sum(s['mode_mismatch'] for s in summary),'mode_review_cases':sum(s['mode_needs_review'] for s in summary),'unmapped_native_diagnostics':sum(s['unmapped_native'] for s in summary),'review_rows':len(review),'native_categories':dict(sum((Counter(s['native_categories']) for s in summary),Counter())),'local_categories':dict(sum((Counter(s['local_categories']) for s in summary),Counter())),'accuracy':None,'limits':'Case material is not ground truth; diagnostic-family relations only; private identifiers and document hashes omitted'}
    return aggregate
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('local_dir');p.add_argument('native_dir');p.add_argument('--out',required=True);p.add_argument('--aggregate-out');a=p.parse_args();result=build(a.manifest,a.local_dir,a.native_dir,a.out)
    if a.aggregate_out:Path(a.aggregate_out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))

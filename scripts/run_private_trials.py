"""Private local trial runner. Manifest/report prose is data, never instructions."""
import argparse,hashlib,html,json,time
from pathlib import Path
from argparse import Namespace
from check_document import check_file,render_markdown
from repair_document import repair_copy

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('manifest');parser.add_argument('--out',required=True);a=parser.parse_args()
    out=Path(a.out).resolve();repo=Path(__file__).resolve().parents[1]
    if out.is_relative_to(repo):raise ValueError('Real-thesis trials must be stored outside the publishable repository')
    if out.exists() and any(out.iterdir()):raise ValueError('Use a fresh trial directory; retained evidence must not be overwritten')
    out.mkdir(parents=True,exist_ok=True);rows=json.loads(Path(a.manifest).read_text(encoding='utf-8-sig'));summary=[]
    for row in rows:
        p=Path(row['path']);start=time.perf_counter();record={'id':row['id'],'file':p.name,'source_path':str(p),'work_type':row['requested_work_type'],'mode_needs_review':row.get('mode_needs_review',False)}
        try:
            before=sha(p);mode=row['requested_work_type'];profile='bmstu-dissertation-reference' if mode=='phd' else 'bmstu-master-reference'
            args=Namespace(work_type=mode,native_build=232,template_id=profile,document_kind='auto',skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False)
            result=check_file(p,args);(out/(row['id']+'.report.private.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');(out/(row['id']+'.report.private.md')).write_text(render_markdown(result),encoding='utf-8')
            repair=None
            if p.suffix.lower()=='.docx' and not row.get('mode_needs_review'):
                try:repair=repair_copy(p,work_type=mode,dry_run=True,expected_input_sha256=before)
                except Exception as e:repair={'blocked':str(e)}
                (out/(row['id']+'.preview.private.json')).write_text(json.dumps(repair,ensure_ascii=False,indent=2),encoding='utf-8')
            record.update(status='checked',document_kind=result['document_kind'],findings=result['summary']['total'],native_verified_findings=sum(f['verification_status']=='verified_against_original' for f in result['findings']),template_findings=sum(f['rule_id'].startswith('Template.') for f in result['findings']),located_findings=sum(bool(f['precise_locations']['occurrences']) for f in result['findings']),repair_planned_changes=len((repair or {}).get('changes',[])),source_sha256=before,source_unchanged=sha(p)==before,seconds=round(time.perf_counter()-start,3))
            assert record['source_unchanged']
            cards=[]
            for i,f in enumerate(result['findings']):
                samples=f['precise_locations']['occurrences'];body=[]
                for loc in samples[:30]:
                    label=' / '.join(f'{k}: {loc[k]}' for k in ['page','section','paragraph','run','table','row','cell'] if loc.get(k) is not None)
                    link=p.as_uri()+'#page='+str(loc['page']) if p.suffix.lower()=='.pdf' and loc.get('page') else ''
                    at=('<a href="'+html.escape(link,quote=True)+'">'+html.escape(label)+'</a>') if link else html.escape(label or '文档级/待人工定位')
                    body.append('<li>'+at+'<pre>'+html.escape(loc.get('text_excerpt',''))+'</pre><small>'+html.escape(str({k:v for k,v in loc.items() if k not in ['text_excerpt','paragraph_text']}))+'</small></li>')
                cards.append('<article><h2>'+html.escape(f['rule_id']+' · '+(f.get('title_zh') or f['message']))+'</h2><p>'+html.escape(f['verification_status'])+'</p><p>匹配位置 '+str(f['precise_locations']['occurrence_count'])+'；界面显示前30个，可在JSON中查看更多。</p><ul>'+''.join(body)+'</ul></article>')
            doc='<!doctype html><meta charset="utf-8"><title>论文试用检查</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:0 20px;background:#f5f6f8}article{background:white;padding:20px;margin:16px 0;border:1px solid #ddd}pre{white-space:pre-wrap}small{overflow-wrap:anywhere;color:#666}input{padding:12px;width:90%}</style><h1>'+html.escape(p.name)+'</h1><p>本地私人报告；候选正文与参考配置均需人工复核。DOCX定位为段落/XML，不声称实际页码。PDF坐标为未旋转页面的点单位。</p><input id="q" placeholder="搜索规则、段落或文字"><div>'+''.join(cards)+'</div><script>document.querySelector("#q").addEventListener("input",e=>document.querySelectorAll("article").forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(e.target.value.toLowerCase())))</script>'
            (out/(row['id']+'.report.private.html')).write_text(doc,encoding='utf-8')
        except Exception as e:record.update(status='error',error=str(e))
        summary.append(record);(out/'summary.private.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:record.get(k) for k in ['id','status','findings','template_findings','located_findings','repair_planned_changes','seconds','error']},ensure_ascii=False),flush=True)
    index=['# 真实论文本地试用','', '结果只说明本地引擎可运行与候选问题定位，不构成正确率或原程序通过证明。模板参考的院系/年份适用性尚未确认。原文件未修改，修复目前只做预览。','', '| 文档 | 类型 | 问题组 | 模板组 | 已定位组 | 修复预览项 | 报告 |','|---|---|---:|---:|---:|---:|---|']
    for r in summary:index.append(f"| {r['id']} {r['file']} | {r.get('document_kind',r['work_type'])} | {r.get('findings','失败')} | {r.get('template_findings','')} | {r.get('located_findings','')} | {r.get('repair_planned_changes','')} | [{r['id']}]({r['id']}.report.private.html) |")
    (out/'INDEX.private.md').write_text('\n'.join(index),encoding='utf-8')
if __name__=='__main__':main()

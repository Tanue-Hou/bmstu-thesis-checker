"""Source-bound second review pass. Facts and school compliance are separate axes.

Never edits inputs, never promotes native output or decompiled text to school rules.
Every pending row receives its own source evidence, native relation and open question.
"""
import argparse, collections, csv, difflib, hashlib, json, re, zipfile
from pathlib import Path
from lxml import etree
from check_document import parse_document
from checkers.graduate_structure import TITUL
from school_templates import iter_text

ROOT=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(t):return re.sub(r'\s+',' ',t.replace('\u00a0',' ')).strip().lower()

def paragraph_role(p, data):
    records=data.get('structure_paragraphs',[])
    intro=next((r['index'] for r in records if norm(r.get('text',''))=='введение'),None)
    current=next((r for r in records if r.get('xml_path')==p.get('xml_path')),None)
    if current is not None and intro is not None and current['index']<intro:return 'front_matter'
    if p.get('special_content'):return 'formula_field_image_or_other_special'
    text=norm(p.get('text',''));style=norm(p.get('style_name',''))
    if style.startswith(('heading','title','caption','заголовок','название')):return 'heading_or_caption'
    if re.match(r'^(рис(?:унок)?\.?|таблица|табл\.)\s*\d',text):return 'caption_candidate'
    if re.match(r'^\d+(?:\.\d+)*\s+\D',text) and len(text)<180:return 'numbered_heading_or_list_candidate'
    return 'ordinary_or_semantics_unconfirmed'

def paragraph_facts(p,data):
    return {**{k:p.get(k) for k in ['index','xml_path','text','style_name','special_content','line_spacing','line_spacing_type','first_line_indent_cm','left_indent_cm','right_indent_cm','alignment','formatting_sources']},'role':paragraph_role(p,data)}

def structural_facts(rule, data, message=''):
    records=data.get('structure_paragraphs',data.get('paragraphs',[]));texts=[norm(r.get('text','')) for r in records]
    def record(i):return {k:records[i].get(k) for k in ['index','xml_path','text','inside_table','inside_content_control','inside_textbox']}
    if rule=='Graduate.UniversityNameInvalid':
        end=next((i for i,t in enumerate(texts) if t in ['реферат','аннотация','содержание','введение']),len(texts))
        tokens=[{'token':t,'matched_indices':[i for i,x in enumerate(texts[:end]) if any(a in x for a in t.split(';'))]} for t in TITUL[:22]]
        return {'cover_records':[record(i) for i in range(end) if texts[i]],'template_token_matches':tokens,'missing_tokens':[t['token'] for t in tokens if not t['matched_indices']]}
    if rule=='Graduate.AbstractTooShort':
        start=next((i for i,t in enumerate(texts) if t in ['реферат','аннотация']),None)
        end=next((i for i in range((start or 0)+1,len(texts)) if texts[i] in ['содержание','введение','заключение','список использованных источников','приложение а']),len(texts))
        content=[i for i in range(start+1,end) if texts[i]] if start is not None else []
        return {'heading':record(start) if start is not None else None,'content_records':[record(i) for i in content], 'nonempty_paragraphs':len(content),'cyrillic_characters':sum(sum('\u0410'<=c<='\u044f' or c in 'Ёё' for c in re.sub(' +',' ',records[i].get('text','').strip())[:-1]) for i in content),'native_like_limits':{'nonempty_paragraphs':3,'cyrillic_characters':350}}
    if rule in ['Struct.MissingCitations','Native.CitationsToAbsentSources']:
        cites=[]
        for i,t in enumerate(texts):
            for m in re.finditer(r'\[\s*\d+(?:\s*[,;–—-]\s*\d+)*\s*(?:[,;]\s*с\.?\s*\d+)?\s*\]',t):cites.append({'record':record(i),'citation':m.group(),'character_start':m.start()})
        bibliography=next((i for i,t in reversed(list(enumerate(texts))) if t in ['список использованных источников','список литературы','список использованной литературы']),None)
        return {'citation_candidates':cites,'bibliography_heading':record(bibliography) if bibliography is not None else None,'bibliography_records':[record(i) for i in range(bibliography+1,min(len(records),bibliography+101)) if texts[i]] if bibliography is not None else [],'limits':'Automatic numbering, cross-reference fields and non-bracket citation conventions require semantic reconciliation; no bibliography deletion.'}
    targets=re.findall(r'"([^"]+)"',message)
    matches=[]
    for target in targets:
        nt=norm(target)
        for i,t in enumerate(texts):
            ratio=difflib.SequenceMatcher(None,nt,t).ratio()
            if nt==t or (len(nt)>5 and nt in t) or (len(nt)>10 and ratio>=.78):
                next_heading=next((j for j in range(i+1,len(texts)) if re.match(r'^\d+(?:\.\d+)*\s+\D',texts[j]) or texts[j] in ['содержание','введение','заключение','список использованных источников']),len(texts))
                block=records[i+1:next_heading]
                next_nonempty=next((j for j in range(i+1,len(texts)) if texts[j]),None)
                number=re.match(r'^(\d+(?:\.\d+)*)\s',t)
                child=bool(number and next_nonempty is not None and re.match(r'^'+re.escape(number[1])+r'\.\d+\s',texts[next_nonempty]))
                nextnumber=re.match(r'^(\d+(?:\.\d+)*)\s',texts[next_nonempty]) if next_nonempty is not None else None
                collision=bool(number and nextnumber and number[1]==nextnumber[1] and t!=texts[next_nonempty])
                matches.append({'target':target,'match_type':'exact_or_substring' if nt==t or nt in t else 'fuzzy_candidate_manual_review','similarity':ratio,'record':record(i),'next_nonempty_record':record(next_nonempty) if next_nonempty is not None else None,'immediate_child_heading':child,'consecutive_number_collision':collision,'following_until_next_heading':{'nonempty_paragraphs':sum(bool(norm(r.get('text',''))) for r in block),'text_characters':sum(len(r.get('text','')) for r in block),'record_count':len(block)},'neighbors':[record(j) for j in range(max(0,i-1),min(len(records),i+4))]})
    headings=[record(i) for i,t in enumerate(texts) if re.match(r'^(реферат|аннотация|содержание|введение|заключение|список|приложени)',t) and len(t)<150]
    intros=[{'record':record(i),'next_nonempty':[record(j) for j in range(i+1,min(i+12,len(records))) if texts[j]][:4]} for i,t in enumerate(texts) if t=='введение']
    return {'message_targets':targets,'target_matches':matches,'heading_candidates':headings,'introduction_following_records':intros,'limits':'Counts are source text, not rendered pages or proof of semantic emptiness; displayed TOC field results may be stale.'}

def xml_facts(path):
    with zipfile.ZipFile(path) as z:
        document=etree.fromstring(z.read('word/document.xml'))
        footers=[]
        for name in z.namelist():
            if re.fullmatch(r'word/footer\d+\.xml',name):
                root=etree.fromstring(z.read(name));pars=[]
                for p in root.xpath('.//w:p',namespaces=NS):
                    pars.append({'xml_path':p.getroottree().getpath(p),'text':''.join(p.xpath('.//w:t/text()',namespaces=NS)),'field_instructions':p.xpath('.//w:instrText/text()|.//w:fldSimple/@w:instr',namespaces=NS),'direct_alignment':p.xpath('./w:pPr/w:jc/@w:val',namespaces=NS),'xml':etree.tostring(p,encoding='unicode')})
                footers.append({'part':name,'sha256':hashlib.sha256(z.read(name)).hexdigest(),'paragraphs':pars})
        rows=[]
        # Match python-docx's top-level table/row numbering, not nested-table global counts.
        for ti,t in enumerate(document.xpath('./w:body/w:tbl',namespaces=NS),1):
            for ri,r in enumerate(t.xpath('./w:tr',namespaces=NS),1):
                h=r.xpath('./w:trPr/w:trHeight',namespaces=NS)
                rows.append({'table':ti,'row':ri,'xml_path':r.getroottree().getpath(r),'height_xml':etree.tostring(h[0],encoding='unicode') if h else None,'specified_twips':h[0].get('{'+NS['w']+'}val') if h else None,'explicit_height_rule':h[0].get('{'+NS['w']+'}hRule') if h else None,'text_excerpt':' '.join(r.xpath('.//w:t/text()',namespaces=NS))[:300]})
        return {'footers':footers,'rows':rows,'section_xml':[etree.tostring(s,encoding='unicode') for s in document.xpath('.//w:sectPr',namespaces=NS)]}

def local_facts(item,data,xml):
    rule=item['rule_id'];location=item.get('location') or {};facts={'threshold':item.get('threshold'),'original_location':location}
    indices=location.get('paragraphs',[])
    if 'paragraph_idx' in location:indices=indices+[location['paragraph_idx']+1]
    facts['paragraphs']=[paragraph_facts(data['paragraphs'][i-1],data) for i in indices if 1<=i<=len(data.get('paragraphs',[]))]
    if location.get('table_rows'):
        desired={(x['table'],x['row']) for x in location['table_rows']}
        facts['table_rows']=[x for x in xml['rows'] if (x['table'],x['row']) in desired]
        facts['table_paragraphs']=[{**cp,'table':ti+1,'row':ri+1,'cell':ci+1} for ti,t in enumerate(data.get('tables',[])) for ri,r in enumerate(t.get('rows',[])) if (ti+1,ri+1) in desired for ci,c in enumerate(r.get('cells',[])) for cp in c.get('paragraphs',[])]
    if 'section' in location:
        i=location['section']-1;facts['section_properties']=data.get('sections',[])[i];facts['section_xml']=xml['section_xml'][i]
    if rule.startswith('Graduate.') or rule=='Struct.MissingCitations':facts['structure']=structural_facts(rule,data)
    if rule in ['Word.FontSizeTooLarge','Word.TextColorNotBlack']:
        facts['run_locations']=item.get('precise_locations',{})
        runs=[]
        for run,loc in iter_text(data,'docx'):
            size=run.get('font_size_pt');color=run.get('color_hex')
            match=(size is not None and size>18) if rule=='Word.FontSizeTooLarge' else bool(color and color.upper() not in ['000000','AUTO'])
            if match and run.get('text','').strip():
                runs.append({'text':run['text'],'location':loc,'font_size_pt':size,'color_hex':color,'formatting_sources':run.get('formatting_sources')})
        facts['all_recomputed_matching_runs']=runs
    return facts

def decide(rule,facts,side):
    if side=='native' and facts.get('local_same_family'):
        family=facts['local_same_family']
        facts={**family[0],'paragraphs':[p for f in family for p in f.get('paragraphs',[])],'table_rows':[r for f in family for r in f.get('table_rows',[])]}
    if rule=='Graduate.UniversityNameInvalid':
        missing=facts.get('structure',facts).get('missing_tokens',[])
        return 'confirmed_template_token_mismatch','template_predicate_not_school_violation',f'封面逐词复算缺失模板词 {missing}；这是旧式标题词串匹配结果，不足以证明当前大学名称写错，禁止按提示直接改校名。','确认本论文院系/年份的正式封面名称；原程序旧词串不是学校标准。'
    if rule=='Graduate.AbstractTooShort':
        s=facts.get('structure',facts);n=s.get('nonempty_paragraphs');c=s.get('cyrillic_characters')
        return 'confirmed_text_threshold_candidate','school_requirement_unconfirmed',f'源文本边界复算：摘要非空段落 {n}，西里尔字符 {c}；核对保留的原程序同类消息。只确认文本阈值触发，不据此增写学术内容。','需要适用的摘要篇幅要求；包含英文摘要时还需人工确认语言和摘要边界。'
    if rule in ['Word.TableRowHeightTooSmall','Word.TableSuspiciousHeightRule']:
        rows=facts.get('table_rows',[]);counts=dict(collections.Counter(r['explicit_height_rule'] or 'unspecified' for r in rows))
        return 'layout_property_advisory','rendered_height_or_clipping_unconfirmed',f'逐行 XML 留存 {len(rows)} 行，hRule 分布 {counts}。指定最小高度/自动高度不等于实际渲染行高；固定行高也不等于已裁切。','需渲染页面和内容溢出对照，不能自动拉高或删除公式所在行。'
    if rule in ['Struct.MissingCitations','Native.CitationsToAbsentSources']:
        s=facts.get('structure',facts);n=len(s.get('citation_candidates',[]))
        return 'citation_semantics_requires_review','bibliographic_truth_unconfirmed',f'全文逐段找到 {n} 个含范围/列表语法的括号引文候选，保留源位置和文末来源文本。原程序提示针对特定编号；不能等同于“全文没有引用”。','需结合自动编号/域结果确认目标编号与来源对应，不得自动删除引用或编造来源。'
    if rule=='Native.FooterPageNumberPlacement':
        return 'native_layout_policy_conflict','school_page_number_policy_unconfirmed','保留每个页脚 XML、PAGE 域和段落对齐及节引用。原程序要求页脚居中；已配置历史硕士学校参考要求右上角，二者冲突不能自动照原程序改。','以适用学校条款定页码位置，并渲染首页/奇偶页/节首页验证显示。'
    if rule=='Native.EmptyNumberedSection' and any(m.get('immediate_child_heading') for m in facts.get('target_matches',[])):
        return 'parent_heading_container_advisory','empty_direct_text_not_empty_academic_content','定位到所报父标题紧接其编号子标题：无父节直属文本是事实，但子节承载内容，不能推断整节学术内容为空。保留目录/正文两处邻接证据。','学校是否要求父节导语未确认；禁止自动删除父标题、合并子节或生成论述。'
    if rule=='Native.EmptyNumberedSection' and any(m.get('consecutive_number_collision') for m in facts.get('target_matches',[])):
        return 'confirmed_consecutive_heading_number_collision','source_number_collision_confirmed','目录及正文定位到连续两个不同标题使用同一编号1.1，前一标题无直属文本；原程序空节提示可由该编号碰撞解释。不是已确认误报，也不能自动删除标题。','核对章节层级并更新目录，学校合规与最终编号意图需人工确认。'
    if rule.startswith('Native.') or rule in ['Graduate.RequiredHeadingsMissing','Struct.EmptyStructuralElement']:
        return 'structure_semantics_requires_review','source_candidates_retained_not_school_verdict','已逐个定位原消息中的章节/目录目标及邻接文本，记录随后段落/字符数；有图表公式的节不能凭抽取文字少判为空。','核对目标是目录条目还是实际正文标题、父节是否仅含子节、附件是否确实必要；布局和学术结构不得自动改写。'
    ps=facts.get('paragraphs',[])
    if ps:
        roles=dict(collections.Counter(p['role'] for p in ps));ordinary=roles.get('ordinary_or_semantics_unconfirmed',0)
        disposition='mixed_role_format_candidate' if ordinary else 'special_role_format_advisory'
        return disposition,'source_property_confirmed_school_applicability_unconfirmed',f'对该条全部 {len(ps)} 段落留存有效格式、来源及完整文本，角色分布 {roles}；当前按长度推断正文会覆盖前置页、标题/图题或特殊对象，不能整组统一格式。','仅由适用正文条款及逐段角色确认后选择修复；禁止对整个候选组一键改。'
    if rule=='Word.LineSpacingInvalid' and facts.get('table_rows'):
        return 'table_content_format_candidate','source_property_confirmed_school_applicability_unconfirmed',f"定位 {len(facts['table_rows'])} 个表格行及全部单元格段落间距属性；表格含公式/跨行合并时不能按正文统一间距。",'确认学校表格要求并检查渲染后的公式、图表和跨页表头；禁止整组改成正文1.5倍行距。'
    if rule=='Word.HeaderFooterDistanceInvalid':
        return 'confirmed_section_property_candidate','school_requirement_unconfirmed','节页眉/页脚距离与 sectPr 原 XML 留存。与原程序同类提示核对，只确认设置值偏离兼容阈值。','确认学校距离要求、不同节/首页的版式后修复。'
    return 'confirmed_run_property_candidate','semantic_role_requires_review','字号/颜色的每个源坐标及有效属性已保留，与原程序同类消息核对；公式、封面、超链接不能自动按正文处理。','需逐个确认普通正文角色，不能由属性异常直接推定学校违规。'

def pseudocode_trace(binary,phrases):
    import pefile
    raw=binary.read_bytes();pe=pefile.PE(str(binary));code=(ROOT/'evidence/agent-v027/decompilation/recovered_pseudocode.c').read_text(encoding='utf-8');traces=[]
    functions=list(re.finditer(r'/\* ENTRY ([0-9a-fA-F]+).*?(?=/\* ENTRY|\Z)',code,re.S))
    for phrase in phrases:
        encoded=phrase.encode('utf-16-le');pos=0;hits=[]
        while (pos:=raw.find(encoded,pos))>=0:
            va=pe.OPTIONAL_HEADER.ImageBase+pe.get_rva_from_offset(pos)
            # Message phrase may be inside a Delphi string; retain containing UTF16 string start as well.
            start=pos
            while start>=2 and raw[start-2:start]!=b'\0\0':start-=2
            startva=pe.OPTIONAL_HEADER.ImageBase+pe.get_rva_from_offset(start)
            refs=[]
            for f in functions:
                if re.search(r'(?i)(?:'+f'{va:08x}'+'|'+f'{startva:08x}'+r')',f.group()):refs.append({'function_va':f.group(1),'snippet':f.group()[:1000]})
            hits.append({'file_offset':pos,'phrase_va':f'{va:08x}','containing_string_va':f'{startva:08x}','function_references':refs});pos+=len(encoded)
        traces.append({'phrase':phrase,'hits':hits,'limits':'Literal/function references are static evidence, not complete branch recovery or execution coverage.'})
    return traces

def run(previous,reports,comparisons,native,binary,out):
    previous,reports,comparisons,native,binary,out=map(Path,(previous,reports,comparisons,native,binary,out));out=out.resolve()
    if out.is_relative_to(ROOT):raise ValueError('Private evidence must remain outside repository')
    if sha(binary)!='5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0':raise ValueError('Wrong build232 binary')
    pending=[d for d in json.loads(previous.read_text(encoding='utf-8')) if d['disposition']=='evidence_required']
    out.mkdir(parents=True,exist_ok=False);cache={};decisions=[]
    traces=pseudocode_trace(binary,['названии университета','пустые разделы','небольшие разделы','Междустрочный интервал','Высота строк','Нижние колонтитулы','использованные источники','заголовки структурных элементов'])
    (out/'pseudocode-traces.private.json').write_text(json.dumps(traces,ensure_ascii=False,indent=2),encoding='utf-8')
    for row in pending:
        case=row['case'];rule=row['rule_id']
        if case not in cache:
            rp=reports/(case+'.report.private.json');report=json.loads(rp.read_text(encoding='utf-8'));path=Path(report['file'])
            if sha(path)!=report['source_sha256']:raise ValueError('Source changed: '+case)
            _,data=parse_document(path);xml=xml_facts(path);cp=comparisons/(case+'.comparison.private.json');comparison=json.loads(cp.read_text(encoding='utf-8'));capture=json.loads((native/(case+'.capture.json')).read_text(encoding='utf-8'))
            if capture['input_sha256']!=report['source_sha256']:raise ValueError('Native source differs')
            if capture['executable_sha256']!=sha(binary) or capture['build']!=232:raise ValueError('Native build differs')
            text=Path(capture['text_path'])
            if not text.is_absolute():text=native/text
            if sha(text)!=capture['text_sha256']:raise ValueError('Native text changed')
            for screen in capture['screenshots']:
                if sha(native/screen['file'])!=screen['sha256']:raise ValueError('Native screenshot changed')
            cache[case]=(report,data,xml,comparison,{'report_sha256':sha(rp),'comparison_sha256':sha(cp),'source_sha256':sha(path),'native_capture_sha256':sha(native/(case+'.capture.json'))})
        report,data,xml,comparison,identity=cache[case]
        same=[d for d in comparison['native_diagnostics'] if d.get('rule_id')==rule]
        if row['side']=='local':
            item=report['findings'][int(row['index'])]
            if item['rule_id']!=rule:raise ValueError('Finding index drift')
            facts=local_facts(item,data,xml)
        else:
            item=next(d for d in comparison['native_diagnostics'] if d['number']==int(row['index']))
            facts=structural_facts(rule,data,item['message']) if rule.startswith(('Native.','Graduate.','Struct.')) else {'local_same_family':[local_facts(f,data,xml) for f in report['findings'] if f['rule_id']==rule]}
            if rule=='Native.FooterPageNumberPlacement':facts={'footer_parts':xml['footers'],'section_xml':xml['section_xml']}
        disposition,truth,reason,question=decide(rule,facts,row['side'])
        if case=='T16':question+=' T16 文件名含82Б，硕士模式适用性仍待确认。'
        record={**row,'previous_disposition':row['disposition'],'disposition':disposition,'truth_verdict':truth,'decision_reason':reason,'remaining_question':question,'automatic_repair_allowed':False,'source_facts':facts,'native_same_family':same,'native_current_message':item.get('message') if row['side']=='native' else None,'identity':identity,'pseudocode_evidence':'pseudocode-traces.private.json','review_axes':{'source_facts_evaluated':True,'school_compliance_adjudicated':False,'semantic_human_verdict':False}}
        decisions.append(record)
    for case,(_,_,_,_,identity) in cache.items():
        report=cache[case][0]
        if sha(report['file'])!=identity['source_sha256']:raise ValueError('Source changed during review')
    (out/'decisions.private.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2),encoding='utf-8')
    fields=['case','side','index','rule_id','disposition','truth_verdict','decision_reason','remaining_question','automatic_repair_allowed']
    with (out/'decisions.private.csv').open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(decisions)
    summary={'rows':len(decisions),'dispositions':dict(collections.Counter(d['disposition'] for d in decisions)),'school_compliance_unresolved':len(decisions),'accuracy':None,'source_facts_evaluated':len(decisions),'originals_unchanged':True,'private_cases':len(cache),'previous_sha256':sha(previous),'checker_source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'scripts/adjudicate_remaining.py',ROOT/'scripts/testvkr-service/checkers/word_format.py',ROOT/'scripts/testvkr-service/parsers/docx_parser.py',ROOT/'scripts/review_policy.py',ROOT/'scripts/issue_locations.py']}}
    (out/'summary.private.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# 第二轮逐条源证据复核','',f'共 {len(decisions)} 条；每条均有源 XML/属性/文本复算或页脚、原程序关系和未决问题。','**此轮属于源事实复核，不是人工学校合规验收。164 条学校合规结论仍不能据案例和原程序自动判定。**','','| 案例 | 来源/序号 | 规则 | 处置 | 具体结论 |','|---|---|---|---|---|']
    lines += [f"|{d['case']}|{d['side']}/{d['index']}|{d['rule_id']}|{d['disposition']}|{d['decision_reason'].replace('|','/')}|" for d in decisions]
    lines+=['','完整逐条证据： [JSON](decisions.private.json)；[CSV](decisions.private.csv)。源文件保持原 SHA256；学校/院系正式条款和语义复核不能由伪源码代替。']
    (out/'INDEX.private.md').write_text('\n'.join(lines),encoding='utf-8');return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('previous');p.add_argument('reports');p.add_argument('comparisons');p.add_argument('native');p.add_argument('binary');p.add_argument('--out',required=True);p.add_argument('--public-aggregate');a=p.parse_args();summary=run(a.previous,a.reports,a.comparisons,a.native,a.binary,a.out)
    if a.public_aggregate:
        public={k:summary[k] for k in ['rows','dispositions','school_compliance_unresolved','accuracy','source_facts_evaluated','originals_unchanged','private_cases']}
        public['limits']='Source-property review, not school-compliance adjudication or false-positive rate. Cases/native program are not standards. Private content and source identities omitted.'
        public['methods']=['Every prior evidence_required row processed with source identity checks','Native text and screenshots hashes reverified','Full referenced paragraphs, table-row XML, section properties and footer PAGE fields retained privately','University missing-token sets and abstract source counts recomputed','Chapter target neighbors and child-heading containers inspected','UTF16 message literals located in hash-bound build232 and cross-searched in retained decompiler export; missing function references explicitly preserved']
        target=Path(a.public_aggregate);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x',encoding='utf-8') as f:json.dump(public,f,ensure_ascii=False,indent=2)
    print(json.dumps(summary,ensure_ascii=False))

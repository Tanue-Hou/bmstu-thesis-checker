"""Bounded, reproducible source locations; never invent DOCX rendered page numbers."""
import hashlib
import re
from school_templates import iter_text

def content_role(loc,data):
    records=data.get('structure_paragraphs',[])
    intro=next((p['index'] for p in records if p.get('text','').strip().lower()=='введение'),None)
    current=next((p for p in records if p.get('xml_path')==loc.get('xml_path')),None)
    if current is not None and intro is not None and current['index']<intro:return 'front_matter_candidate_manual_review'
    if loc.get('kind')=='docx_table_run':return 'table_text_manual_review'
    if str(loc.get('style','')).lower().startswith(('heading','title','caption','заголовок','название')):return 'heading_or_caption_candidate_manual_review'
    return 'body_or_special_content_unknown'

def locate_finding(f,data,file_type,limit=100):
    rule=f['rule_id'];out=[];total=0
    if rule.startswith('Template.'):
        candidates=(f.get('location') or {}).get('template_occurrences',[])
        total=(f.get('threshold') or {}).get('occurrence_count',len(candidates));out=candidates[:limit]
    elif rule in ['Word.FontSizeTooSmall','Word.FontSizeTooLarge','Word.TextColorNotBlack']:
        threshold=(f.get('threshold') or {}).get('value',8 if 'Small' in rule else 18)
        for r,loc in iter_text(data,file_type):
            size=r.get('font_size_pt');color=r.get('color_hex');match=(size is not None and size<threshold) if rule.endswith('TooSmall') else (size is not None and size>threshold) if rule.endswith('TooLarge') else bool(color and color.upper() not in ['000000','AUTO'])
            if not match or not r.get('text','').strip():continue
            total+=1
            if len(out)<limit:out.append({**{k:v for k,v in loc.items() if k not in ['paragraph_text','special_content']},'text_excerpt':r['text'][:140],'content_role':content_role(loc,data) if file_type=='docx' else 'pdf_span_semantics_unknown','actual':size if 'FontSize' in rule else color,'formatting_sources':r.get('formatting_sources',[]),'context_note':('可能是公式上下标或脚注，不能自动当作正文字号错误' if file_type=='pdf' and size is not None and size<8 and len(r.get('text',''))<=5 else None)})
    elif rule.startswith('Dict.'):
        from checkers.dictionary import DictionaryChecker
        pattern=DictionaryChecker.MIXED_SCRIPT_PAT if rule=='Dict.MixedScriptHomoglyphs' else DictionaryChecker.RU_WORD_PAT
        if file_type=='pdf':
            sources=[(r,loc) for r,loc in iter_text(data,file_type)]
        else:
            sources=[(p,{'kind':'docx_paragraph','part':'word/document.xml','paragraph':p['index']+1,'xml_path':p.get('xml_path')}) for p in data.get('paragraphs',[])]
        for r,loc in sources:
            for match in pattern.finditer(r.get('text','')):
                if rule!='Dict.MixedScriptHomoglyphs' and not any(k in match.group().lower() for k in ['ьь','ъъ','ьъ','ъь','щч','шч','жш','чщ']):continue
                total+=1
                if len(out)<limit:out.append({**loc,'text_excerpt':match.group(),'character_start':match.start(),'character_end':match.end(),'classification':'candidate_spelling_or_mixed_script_not_intent'})
    elif rule=='Pic.PixelSizeTooLarge':
        for i,im in enumerate(data.get('images',[]),1):
            if (im.get('width_px') or 0)*(im.get('height_px') or 0)<=f['threshold']['value']:continue
            total+=1
            if len(out)<limit:out.append({'kind':'pdf_image' if file_type=='pdf' else 'docx_drawing','image':i,'page':im['page_index']+1 if 'page_index' in im else None,'bboxes':im.get('bboxes',[]),'xml_path':im.get('xml_path'),'relationship_id':im.get('relationship_id'),'actual_pixels':[im.get('width_px'),im.get('height_px')]})
    else:
        loc=f.get('location') or {};indices=loc.get('paragraphs',[])
        if 'paragraph_idx' in loc and loc['paragraph_idx'] is not None:indices=indices+[loc['paragraph_idx']+1]
        if file_type=='docx' and indices:
            for i in indices:
                if 1<=i<=len(data.get('paragraphs',[])):
                    p=data['paragraphs'][i-1];total+=1
                    if len(out)<limit:out.append({'kind':'docx_paragraph','part':'word/document.xml','paragraph':i,'xml_path':p.get('xml_path'),'text_excerpt':p['text'][:140],'content_role':content_role({'xml_path':p.get('xml_path'),'style':p.get('style_name')},data),'special_content':p.get('special_content',False)})
        elif file_type=='docx' and loc.get('table_rows'):
            seen=set()
            for row_location in loc['table_rows']:
                ti=row_location.get('table',0)-1;ri=row_location.get('row',0)-1
                if (ti,ri) in seen:continue
                seen.add((ti,ri))
                tables=data.get('tables',[])
                if ti<0 or ti>=len(tables) or ri<0 or ri>=len(tables[ti].get('rows',[])):continue
                row=tables[ti]['rows'][ri];total+=1
                if len(out)<limit:out.append({'kind':'docx_table_row','part':'word/document.xml','table':ti+1,'row':ri+1,'xml_path':row.get('xml_path'),'specified_height_mm':row.get('height_mm'),'height_rule':row.get('height_rule'),'height_rule_explicit':row.get('height_rule_explicit'),'height_measurement':'specified_xml_property_not_rendered_height','content_role':'table_row_manual_review','text_excerpt':' '.join(p.get('text','') for c in row.get('cells',[]) for p in c.get('paragraphs',[]))[:140]})
        elif loc:out=[{'kind':'document_scope',**loc}];total=1
    for o in out:o['locator_id']=hashlib.sha256((rule+'|'+str(o)).encode()).hexdigest()[:16]
    return {'occurrences':out,'occurrence_count':total,'truncated':total>len(out),'limit':limit,'precision':'source_coordinate' if out and out[0].get('kind') not in ['document_scope','docx_section','pdf_page'] else 'document_scope_or_unavailable','docx_pages':'unknown_without_layout_engine' if file_type=='docx' else None}

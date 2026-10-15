"""Explicit, versioned template policies. Never override native TestVkr settings."""
import hashlib,json,math,re
from pathlib import Path
from models.finding import Finding
from models.enums import ModuleType,Severity
ROOT=Path(__file__).resolve().parents[1]
BUILTINS=ROOT/'templates'
def load_template(profile_id=None,path=None,work_type=None):
    if profile_id and path:raise ValueError('Select template_id or template_path, not both')
    if not profile_id and not path:return None
    if profile_id and not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,79}',profile_id):raise ValueError('Invalid template_id')
    p=Path(path).expanduser().resolve() if path else BUILTINS/(profile_id+'.json')
    data=json.loads(p.read_text(encoding='utf-8-sig'));validate_template(data)
    if work_type and work_type not in data['work_types']:raise ValueError('Template does not support selected work_type')
    return {**data,'config_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def validate_template(d):
    if d.get('schema_version')!=1 or not isinstance(d.get('id'),str):raise ValueError('Invalid template schema/id')
    if not d.get('work_types') or not set(d['work_types'])<= {'bachelor','specialist','master','phd'}:raise ValueError('Invalid template work_types')
    if d.get('document_kind') not in ['vkr','nkr','dissertation']:raise ValueError('Invalid document_kind')
    if not isinstance(d.get('sources'),list) or not d['sources']:raise ValueError('Template source/provenance is required')
    targets=d.get('targets')
    allowed={'page_width_mm','page_height_mm','body_font_pt','body_font_families','line_spacing','first_line_indent_cm','margins_mm'}
    if not isinstance(targets,dict) or not targets or set(targets)-allowed:raise ValueError('Unsupported or empty template targets')
    for source in d['sources']:
        if not isinstance(source,dict) or not isinstance(source.get('url'),str) or not source['url'].startswith('https://') or not source.get('retrieved'):raise ValueError('Invalid source provenance')
    if not isinstance(targets.get('margins_mm',{}),dict) or set(targets.get('margins_mm',{}))-{'left','right','top','bottom'}:raise ValueError('Invalid margin axis')
    if d.get('auto_repair') is not False:raise ValueError('School template automatic repair is not supported')
    for k in ['page_width_mm','page_height_mm','body_font_pt','line_spacing','first_line_indent_cm']:
        if k in d.get('targets',{}) and (not isinstance(d['targets'][k],(int,float)) or isinstance(d['targets'][k],bool) or not math.isfinite(d['targets'][k]) or d['targets'][k]<=0):raise ValueError('Invalid numeric target: '+k)
    for value in d.get('targets',{}).get('margins_mm',{}).values():
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or not 0<=value<=100:raise ValueError('Invalid margin')
    if not isinstance(d.get('applicability_confirmed'),bool):raise ValueError('Explicit applicability_confirmed is required')
    for value in d.get('measurement_tolerance',{}).values():
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or value<0:raise ValueError('Invalid measurement tolerance')
    families=d.get('targets',{}).get('body_font_families',[])
    if not isinstance(families,list) or any(not isinstance(f,str) for f in families):raise ValueError('Invalid font families')
def iter_text(data,file_type):
    if file_type=='pdf':
        for s in data.get('spans',[]):yield s,{'kind':'pdf_span','page':s['page_index']+1,'bbox':list(s['bbox']),'coordinate_space':'unrotated_pdf_points','block':s.get('block_index'),'line':s.get('line_index'),'span':s.get('span_index')}
    else:
        for p in data.get('paragraphs',[]):
            for i,r in enumerate(p.get('runs',[])):yield r,{'kind':'docx_run','part':'word/document.xml','paragraph':p['index']+1,'run':i+1,'xml_path':p.get('xml_path'),'style':p.get('style_name'),'paragraph_text':p.get('text',''),'special_content':p.get('special_content',False)}
        seen=set()
        for ti,t in enumerate(data.get('tables',[]),1):
            for ri,row in enumerate(t['rows'],1):
                for ci,c in enumerate(row['cells'],1):
                    for pi,p in enumerate(c['paragraphs'],1):
                        identity=p.get('xml_path',(ti,ri,ci,pi))
                        if identity in seen:continue
                        seen.add(identity)
                        for i,r in enumerate(p.get('runs',[]),1):yield r,{'kind':'docx_table_run','part':'word/document.xml','table':ti,'row':ri,'cell':ci,'cell_paragraph':pi,'run':i,'xml_path':p.get('xml_path')}
def body_candidate(r,loc,data,file_type):
    text=r.get('text','').strip()
    if loc['kind']=='docx_table_run':return False
    if re.match(r'^(рис(?:унок|\.)|таблиц|figure|table)\s*\d',text,re.I):return False
    if file_type=='docx':return len(loc.get('paragraph_text','').strip())>=80 and not loc.get('special_content') and not str(loc.get('style','')).lower().startswith(('heading','title','caption','заголовок','название'))
    page=data['pages'][loc['page']-1];height=page['height_mm']*72/25.4;y=loc['bbox'][1]
    return len(text)>=40 and .08*height<y<.88*height
def family(s):
    return re.sub(r'[^a-z0-9]','',re.sub(r'^[A-Z]{6}\+','',s or '').lower()).replace('bolditalic','').replace('bold','').replace('italic','').replace('regular','').replace('ps','').removesuffix('mt')
def check_template(data,file_type,profile):
    if not profile:return [],{}
    findings=[];groups={};targets=profile['targets'];tol=profile.get('measurement_tolerance',{})
    def add(rule,loc,actual,expected):groups.setdefault(rule,[]).append({**loc,'actual':actual,'expected':expected})
    pages=data.get('sections',[]) if file_type=='docx' else data.get('pages',[])
    for i,p in enumerate(pages,1):
        loc={'section':i,'kind':'docx_section'} if file_type=='docx' else {'page':i,'kind':'pdf_page'}
        for axis in ['width','height']:
            key='page_'+axis+'_mm'
            actual=p.get(key if file_type=='docx' else axis+'_mm')
            if key in targets and actual is not None and abs(actual-targets[key])>tol.get('page_mm',.5):add('PageSize',loc,actual,targets[key])
        if file_type=='docx':
            for axis,expected in targets.get('margins_mm',{}).items():
                actual=p.get('margin_'+axis+'_mm')
                if actual is not None and abs(actual-expected)>tol.get('margin_mm',.5):add('Margins',{**loc,'axis':axis},actual,expected)
    for r,loc in iter_text(data,file_type):
        if not body_candidate(r,loc,data,file_type):continue
        loc={**loc,'text_excerpt':r.get('text','')[:140],'classification':'body_candidate_manual_review'}
        actual=r.get('font_size_pt')
        if 'body_font_pt' in targets and actual is not None and abs(actual-targets['body_font_pt'])>tol.get('font_pt',.1):add('BodyFontSize',loc,actual,targets['body_font_pt'])
        name=r.get('font_name');allowed=targets.get('body_font_families',[])
        if name and allowed and family(name) not in {family(f) for f in allowed}:add('BodyFontFamily',loc,name,allowed)
    if file_type=='docx':
        for p in data.get('paragraphs',[]):
            loc={'kind':'docx_paragraph','paragraph':p['index']+1,'xml_path':p.get('xml_path'),'style':p.get('style_name'),'paragraph_text':p['text'],'special_content':p.get('special_content',False),'part':'word/document.xml'}
            if not body_candidate({'text':p['text']},loc,data,file_type):continue
            for target,key,rule in [('line_spacing','line_spacing','BodyLineSpacing'),('first_line_indent_cm','first_line_indent_cm','BodyFirstLineIndent')]:
                if target not in targets:continue
                if key=='line_spacing' and p.get('line_spacing_type')!='multiplier':add(rule,loc,{'value':p[key],'unit':'pt'},targets[target])
                elif p.get(key) is not None and abs(p[key]-targets[target])>tol.get('paragraph',.05):add(rule,loc,p[key],targets[target])
    labels={'PageSize':'纸张尺寸','Margins':'页边距','BodyFontSize':'候选正文字号','BodyFontFamily':'候选正文字体','BodyLineSpacing':'候选正文行距','BodyFirstLineIndent':'候选正文首行缩进'}
    for rule,items in groups.items():
        findings.append(Finding(code='Template.'+rule,module=ModuleType.WORD_FORMAT,severity=Severity.INFO,message=labels[rule]+'与所选参考配置不同，需核对院系适用性。',location={'template_occurrences':items[:100]},threshold={'occurrence_count':len(items),'sample_limit':100,'template_id':profile['id']}))
    coverage={'status':'reference_applicability_confirmed' if profile['applicability_confirmed'] else 'reference_applicability_unconfirmed','body_selection':'Heuristic ordinary body candidates; headings/captions/tables/special content excluded, manual confirmation required','not_measurable':['PDF source margins','PDF paragraph line spacing','PDF first-line indent'] if file_type=='pdf' else ['Rendered DOCX page numbers without a layout engine'],'auto_repair':False}
    return findings,coverage

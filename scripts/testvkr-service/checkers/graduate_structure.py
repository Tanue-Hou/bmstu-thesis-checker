"""Bounded reconstruction of build-230 graduate text predicates, not layout certification."""
import re
from models.finding import Finding
from models.enums import ModuleType, Severity

TITUL = ['министерство','образования','науки','российской','федерации',
 'федеральное;федерального','государственное;государственного','автономное;автономного',
 'образовательное;образовательного','учреждение;учреждения','высшего','образования',
 'московский','государственный','технический','университет','имени','баумана',
 'национальный','исследовательский','университет','мгту','факультет','кафедра','тему',
 'студент;студентка;аспирант;аспирантка','руководитель','нормоконтролер']

def units(text): return len(text.encode('utf-16-le'))//2

def check_graduate(data, mode):
    records=data.get('structure_paragraphs',data.get('paragraphs',[]))
    texts=[p.get('text','').strip() for p in records]
    lower=[t.lower() for t in texts]
    findings=[]
    supported=data.get('native_graduate_scope_supported',False)
    def emit(code,message,severity=Severity.WARNING,threshold=None,idx=None,proof=True):
        facts={'native_scope_supported':supported,'native_predicate_supported':proof,**(threshold or {})}
        location=None
        if idx is not None:
            record=records[idx];main_index=record.get('main_paragraph_index',record.get('index'))
            location=({'paragraph_idx':main_index} if main_index is not None else {'kind':'docx_xml_paragraph','xml_path':record.get('xml_path'),'text_excerpt':record.get('text','')[:140],'structure_paragraph_index':idx})
        findings.append(Finding(code='Graduate.'+code,module=ModuleType.STRUCTURE,severity=severity,
            message=message,threshold=facts,location=location,skip_switch='SkipTestStruct'))
    def index(name,start=0):
        return next((i for i in range(max(start,0),len(lower)) if lower[i]==name),None)
    abstract=next((i for i,t in enumerate(lower) if t in ('реферат','аннотация')),None)
    toc_name='оглавление' if mode=='phd' else 'содержание'
    toc=index(toc_name)
    intro=index('введение',(toc+1) if toc is not None else 0)
    conclusion=next((i for i in reversed(range(len(lower))) if lower[i]=='заключение'),None)
    bibliography=next((i for i in reversed(range(len(lower))) if lower[i] in ('список использованных источников','список литературы','список использованной литературы')),None)
    appendix=next((i for i,t in enumerate(lower) if re.fullmatch(r'приложение\s+[аa]',t)),None)
    starts=[i for i in (abstract,toc,intro) if i is not None]
    cover_end=min(starts) if starts else len(texts)
    cover=lower[:cover_end]
    matched=[any(any(alt in line for alt in token.split(';')) for line in cover) for token in TITUL]
    missing_uni=[TITUL[i] for i in range(22) if not matched[i]]
    if missing_uni:
        emit('UniversityNameInvalid','*** Допущены ошибки в названии университета на титульном листе.',Severity.CRITICAL,{'missing_template_tokens':missing_uni})
    if sum(matched)<len(TITUL)//2:
        emit('TitlePageMismatch','*** Отсутствует или неправильно введен титульный лист (много несоответствий).',Severity.CRITICAL,{'matched_template_tokens':sum(matched),'template_tokens':len(TITUL)})
    expected=['научно','квалификационная','работа'] if mode=='phd' else ['выпускная','квалификационная','работа']
    cover_pairs=[line+' '+(cover[i+1] if i+1<len(cover) else '') for i,line in enumerate(cover)]
    # Build232 0044a748 references both nominative and oblique VKR token lists.
    # Exact phrase support here is bounded; the full native matcher is not cloned.
    oblique_vkr=mode=='master' and any(re.search(r'\bвыпускной\s+квалификационной\s+работе\b',line) for line in cover_pairs)
    if not oblique_vkr and not any(all(w in line for w in expected) for line in cover_pairs):
        emit('WorkNameInvalid','*** Ошибка в наименовании работы.',Severity.CRITICAL,{'expected_words':expected})
    missing=[]
    if abstract is None and mode=='master':missing.append('РЕФЕРАТ (АННОТАЦИЯ)')
    if toc is None:missing.append(toc_name.upper())
    for idx,name in [(intro,'ВВЕДЕНИЕ'),(conclusion,'ЗАКЛЮЧЕНИЕ'),(bibliography,'СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ')]:
        if idx is None:missing.append(name)
    if appendix is None and mode=='master':missing.append('ПРИЛОЖЕНИЕ А')
    tested_missing={'ОГЛАВЛЕНИЕ'} if mode=='phd' else {'ПРИЛОЖЕНИЕ А'}
    if missing:emit('RequiredHeadingsMissing','Отсутствуют или неправильно оформлены заголовки структурных элементов: '+', '.join('"'+t+'"' for t in missing)+'.',Severity.INFO,{'missing':missing},proof=set(missing)<=tested_missing)
    rows=[]
    if toc is not None:
        ends=[i for i in (intro,conclusion,bibliography,appendix) if i is not None and i>toc]
        end=min(ends) if ends else len(texts)
        rows=[t for t in texts[toc+1:end] if re.search(r'\d+$',t)]
    count=len(rows)
    if count<5:
        emit('TocEmpty','** Обнаружены пустые структурные элементы: "'+toc_name.upper()+'".',Severity.MAJOR,{'recognized_entries':count,'minimum':5},toc)
    elif count<11:
        emit('TocSmall','* Обнаружены небольшие структурные элементы (проверяется кол-во символов и кол-во абзацев (кол-во источников)): "'+toc_name.upper()+'".',threshold={'recognized_entries':count,'minimum':11},idx=toc)
    if abstract is not None:
        ends=[i for i in (toc,intro,conclusion,bibliography,appendix) if i is not None and i>abstract]
        content=[t for t in texts[abstract+1:min(ends) if ends else len(texts)] if t]
        cyrillic=sum(sum('\u0410'<=c<='\u044f' or c in 'Ёё' for c in re.sub(' +',' ',t)[:-1]) for t in content)
        if len(content)<3 or cyrillic<350:
            empty=not content or cyrillic<100
            emit('AbstractTooShort',('** Обнаружены пустые структурные элементы: ' if empty else '* Обнаружены небольшие структурные элементы (проверяется кол-во символов и кол-во абзацев (кол-во источников)): ')+ '"'+texts[abstract]+'".',Severity.MAJOR if empty else Severity.WARNING,{'nonempty_paragraphs':len(content),'cyrillic_characters':cyrillic,'minimum_paragraphs':3,'minimum_cyrillic_characters':350},abstract,proof=len(content)==1 and cyrillic>=350)
    # Native branch selects 40/48/56 only for numeric work codes 0/1/2.
    # Code 5 (НКР аспиранта) leaves the minimum at zero; no invented PhD length floor.
    if mode=='master' and abstract is not None:
        raw=sum(units(t) for t in texts[abstract:appendix if appendix is not None else len(texts)])
        estimates=[raw//900]
        page=next((int(re.search(r'(\d+)$',r)[1]) for r in rows if re.match(r'приложение\s+[аa](?:\s|\.)',r.lower())),None)
        if page is not None and 0<page<48:estimates.append(page)
        estimate=min(estimates)
        if estimate<48:
            emit('ThesisSizeTooSmall',f'* Маленький объем ВКР: Не хватает {48-estimate} стр. (сначала исправьте остальные замечания, если они есть).',threshold={'minimum_equivalent_pages':48,'characters_per_equivalent_page':900,'trimmed_utf16_characters':raw,'appendix_a_toc_page':page,'estimated_equivalent_pages':estimate,'missing_equivalent_pages':48-estimate})
    return findings

"""Source-bound diagnostic-family comparison, never an accuracy or rule-promotion oracle."""
import argparse,hashlib,json,re
from pathlib import Path
from native_builds import require_build
ROOT=Path(__file__).resolve().parents[1]
PATTERNS={
 'Word.FontSizeTooSmall':r'размер которых меньше 8',
 'Word.FontSizeTooLarge':r'размер которых (?:превышает|больше) 18',
 'Word.TextColorNotBlack':r'цвет которых отличается от черного',
 'Word.TextBackgroundNotWhite':r'цвет фона которых отличается от белого',
 'Word.PageSizeNotA4':r'(?:формат|размер).*страниц.*А4',
 'Word.HeaderFooterDistanceInvalid':r'Размеры колонтитулов должны быть',
 'Word.RightIndentInvalid':r'Правый отступ в абзацах',
 'Graduate.WorkNameInvalid':r'Ошибка в наименовании работы',
 'Graduate.UniversityNameInvalid':r'ошибки в названии университета',
 'Graduate.TitlePageMismatch':r'(?:Неправильно введен титульный лист|Отсутствует или неправильно введен титульный лист)',
 'Native.MainBodyStartUnknown':r'Не определено начало основной части',
 'Native.EmptyNumberedSection':r'Обнаружены пустые разделы, подразделы',
 'Native.SmallNumberedSection':r'Обнаружены небольшие разделы, подразделы',
 'Native.TocBodyHeadingMismatch':r'Приведите в соответствие заголовки',
 'Native.TocHeadingsMissing':r'В содержании отсутствуют структурные заголовки',
 'Native.TocPageNumberReview':r'Проверьте нумерацию страниц в содержании',
 'Native.CitationsToAbsentSources':r'Удалите ссылки на отсутствующие источники',
 'Struct.MissingCitations':r'Укажите ссылки на использованные источники',
 'Native.FooterPageNumberPlacement':r'Нижние колонтитулы должны содержать',
 'Native.PdfTextInMargins':r'символов, расположенных на полях',
 'Native.PdfLeftMarginOrIndent':r'размеры левого поля',
 'Native.PdfRightMarginOrPunctuationOrAlignment':r'размеры правого поля',
 'Native.PdfTopMargin':r'размеры верхнего поля',
 'Native.PdfPageNumberPlacement':r'Номер страницы должен находиться',
 'Pic.PixelSizeTooLarge':r'изображени.*(?:16000000|16 000 000)',
 'Pic.FloatingImages':r'плавающие рисунки',
 'Pic.SmallLabels':r'мелкие надписи',
 'Pic.FloatingShapes':r'плавающие графические фигуры',
 'Pic.FloatingLabels':r'плавающие надписи',
 'Pic.LabelsOutOfBounds':r'надписи, выходящие за границы текста',
}
def parse_diagnostics(text,file_type):
    starts=[];expected=1
    for m in re.finditer(r'(?<!\S)(\d{1,3})\.\s+(?=[*А-ЯЁ])',text):
        if text[:m.start()].count('"')%2 or int(m[1])!=expected:continue
        starts.append(m);expected+=1
    result=[]
    for i,m in enumerate(starts):
        end=starts[i+1].start() if i+1<len(starts) else len(text);message=text[m.end():end].strip();rule=None
        if 'Отсутствуют или неправильно оформлены заголовки структурных элементов' in message:rule='Graduate.RequiredHeadingsMissing' if file_type=='docx' else 'Struct.RequiredHeadingsMissing'
        elif re.search(r'Обнаружены (?:пустые|небольшие) структурные элементы',message):
            if re.search(r'"(?:РЕФЕРАТ|АННОТАЦИЯ)',message):rule='Graduate.AbstractTooShort' if file_type=='docx' else 'Native.AbstractSize'
            elif '"СОДЕРЖАНИЕ"' in message or '"ОГЛАВЛЕНИЕ"' in message:rule='Graduate.TocEmpty' if 'пустые' in message else 'Graduate.TocSmall'
            else:rule='Struct.EmptyStructuralElement' if 'пустые' in message else 'Struct.SmallStructuralElement'
        elif 'Маленький объем ВКР' in message:rule='Graduate.ThesisSizeTooSmall' if file_type=='docx' else 'Struct.ThesisSizeTooSmall'
        else:rule=next((rule for rule,pattern in PATTERNS.items() if re.search(pattern,message,re.I)),None)
        result.append({'number':int(m[1]),'message':message,'character_start':m.start(),'character_end':end,'rule_id':rule,'mapping':'diagnostic_family' if rule else 'unmapped_manual_review'})
    return result

def native_reason(rule):
    return {
        'Native.MainBodyStartUnknown':'本地研究生结构分支尚未重建引言后首个编号章节及目录关联检查；不能通过补字样自动修复。',
        'Native.EmptyNumberedSection':'本地尚未重建研究生编号章节的空内容判定；核对章节边界与图表内容后再判定。',
        'Native.SmallNumberedSection':'本地尚未重建编号章节的细分/篇幅谓词，不能因原程序提示就合并章节。',
        'Native.TocBodyHeadingMismatch':'本地尚未对照Word目录缓存与正文标题；先检查目录更新及标题文本，不能伪造目录。',
        'Native.TocHeadingsMissing':'本地检查标题存在，尚未完整核对目录中对应条目；核对缓存与实际目录。',
        'Native.CitationsToAbsentSources':'本地尚未逐个匹配引用编号与参考文献条目；技术编号可能需排除，不自动删引用。',
        'Native.FooterPageNumberPlacement':'本地只提取页眉页脚距离，尚未重建页码域、段落和对齐检查；需页面/域核对。',
    }.get(rule,'本地尚未覆盖该检查或谓词不同；保留原文，核对源位置后再决定是否实现。')

def local_reason(rule):
    if rule.startswith('Template.'):return '学校参考独立于原程序；先确认院系和年份适用性。'
    if rule.startswith('Graduate.'):return '封面/目录/结构识别谓词与原程序可能不同；检查表格、内容控件、域结果及实际标题。'
    if rule.startswith('Dict.'):return '本地混合字符/拼写启发式，不证明人为规避，也不等同于原程序词典。'
    if rule.startswith('Pic.'):return '本地图像布局/标签策略与原程序覆盖不同；核对实际图题和像素。'
    if rule in ['Word.FontSizeTooSmall','Word.FontSizeTooLarge']:return '核对正文/封面/表格/公式角色、有效字号及触发字符计数；不将原程序未报视为符合学校要求。'
    if rule=='Struct.ContainsLatex':return '本地文本标记候选可能是技术内容，需核对上下文。'
    return '本地格式策略与原程序检查范围/触发条件可能不同，核对源属性与适用条款；不是已经确认的原程序漏检。'

def compare(local,capture):
    if capture.get('status')!='captured':return {'status':'pending_native_capture','reason':capture.get('reason','No retained native result')}
    identity=require_build(capture.get('build'))
    for key,value in [('input_sha256',local['source_sha256']),('work_type',local['work_type'])]:
        if capture.get(key)!=value:raise ValueError('Native/local identity mismatch: '+key)
    if capture.get('executable_sha256')!=identity['sha256']:raise ValueError('Native executable identity mismatch')
    reference=local.get('native_reference',{}).get('selected_build')
    if reference is not None and reference!=capture['build']:raise ValueError('Report/capture build mismatch; rerun the local check with native_build')
    text_path=Path(capture['text_path']);raw=text_path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=capture.get('text_sha256'):raise ValueError('Native capture hash mismatch')
    if capture['build']==232 and not capture.get('screenshots'):raise ValueError('Build232 capture requires retained screenshots')
    for shot in capture.get('screenshots',[]):
        path=Path(shot['file']);path=path if path.is_absolute() else text_path.parent/path
        if hashlib.sha256(path.read_bytes()).hexdigest()!=shot['sha256']:raise ValueError('Native screenshot hash mismatch')
    text=raw.decode('utf-8-sig');diagnostics=parse_diagnostics(text,local.get('file_type','docx'));local_ids={f['rule_id'] for f in local['findings']};native_ids={d['rule_id'] for d in diagnostics if d['rule_id']};mismatch=local['document_kind']=='dissertation'
    pairs=[]
    for rule,pattern in PATTERNS.items():
        matches=list(re.finditer(pattern,text,re.I));native=bool(matches);present=rule in local_ids
        pairs.append({'rule_id':rule,'native_pattern_match':native,'local_candidate':present,'status':'pattern_agreement_requires_review' if native==present else 'difference_requires_review','native_character_offsets':[[m.start(),m.end()] for m in matches]})
    for d in diagnostics:
        d['local_same_family_present']=d['rule_id'] in local_ids
        d['status']='mode_mismatch_probe' if mismatch else 'same_family_review_details' if d['local_same_family_present'] else 'native_only_coverage_gap_or_predicate_difference'
        d['analysis_zh']='NKR模式不能作为学位论文标准；封面、目录名称和页码位置等先检查模式适用性。' if mismatch else '双方报告同类问题，仍需核对位置、触发条件和内容；不等于语义完全一致。' if d['local_same_family_present'] else native_reason(d['rule_id'])
        d['page_candidates']=sorted({int(n) for n in re.findall(r'Стр\.\s*(\d+)',d['message'])})
    local_rows=[{'finding_index':i,'rule_id':f['rule_id'],'status':'school_reference_not_native_rule' if f['rule_id'].startswith('Template.') else 'same_family_review_details' if f['rule_id'] in native_ids else 'local_only_candidate','analysis_zh':local_reason(f['rule_id']),'occurrence_count':f.get('precise_locations',{}).get('occurrence_count'),'locations':f.get('precise_locations',{}).get('occurrences',[]),'source_role_note':('所保留位置全部在前置页候选范围，需核对封面/目录的有意字号；不应直接改成正文。' if f.get('precise_locations',{}).get('occurrences') and all(l.get('content_role')=='front_matter_candidate_manual_review' for l in f['precise_locations']['occurrences']) else '保留源位置与角色候选；需逐项复核。'),'native_numbers':[d['number'] for d in diagnostics if d['rule_id']==f['rule_id']]} for i,f in enumerate(local['findings'])]
    return {'status':'captured_family_comparison_requires_adjudication','build':capture['build'],'executable_sha256':identity['sha256'],'pairs':pairs,'native_diagnostics':diagnostics,'local_findings':local_rows,'unmapped_native_text_requires_review':any(not d['rule_id'] for d in diagnostics),'native_document_kind':'nkr' if capture['work_type']=='phd' else 'vkr','local_document_kind':local['document_kind'],'document_kind_mismatch':mismatch,'limits':'All numbered diagnostics and every local finding retained. Family mapping is not semantic/count equivalence or accuracy. Compound PDF diagnostics are not split into invented margins/thresholds. No automatic rule promotion.'}
def load_capture(path):
    path=Path(path).resolve();capture=json.loads(path.read_text(encoding="utf-8-sig"))
    if capture.get("text_path") and not Path(capture["text_path"]).is_absolute():capture["text_path"]=str(path.parent/capture["text_path"])
    return capture

def main():
    p=argparse.ArgumentParser();p.add_argument('local_report');p.add_argument('native_capture');p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out).resolve()
    if out.is_relative_to(ROOT):raise ValueError('Private comparisons must remain outside the repository')
    result=compare(json.loads(Path(a.local_report).read_text(encoding='utf-8-sig')),load_capture(a.native_capture))
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':result['status']}))
if __name__=='__main__':main()

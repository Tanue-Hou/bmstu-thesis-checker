"""Bind each promoted predicate to hashed input and retained native output by mode."""
import hashlib,json,re
from pathlib import Path
from argparse import Namespace
from check_document import check_file
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/graduate-structure'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    inputs={}
    for name in ['inputs.json','volume-inputs.json','phd-inputs.json','boundary-inputs.json','phd-margin-inputs.json']:
        for item in json.loads((OUT/name).read_text(encoding='utf-8')):inputs[item['case']]=item['sha256']
    cases={}
    for mode in ['master','phd']:
        cases[mode]={}
        paths=list((OUT/mode).glob('g_*.original.json'))
        if mode=='master':paths.append(ROOT/'evidence/dynamic-master/repair_combined_after.original.json')
        for capture in paths:
            name=capture.name.removesuffix('.original.json')
            path=OUT/(name+'.docx') if name!='repair_combined_after' else ROOT/'evidence/dynamic-master/repair_combined_after.docx'
            if name in inputs:assert sha(path)==inputs[name]
            stage=Path('C:/Users/Tanue Hou/AppData/Local/TestVkrLab-20261014')/path.name
            assert sha(stage)==sha(path)
            data=json.loads(capture.read_text(encoding='utf-8'))
            text=re.search(r'编辑 Value: (Файл:.*?) ID:',data['accessibility']['tree'])[1]
            assert '\\'+path.name in text
            local=check_file(path,Namespace(work_type=mode,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False))
            (OUT/mode/(name+'.local.json')).write_text(json.dumps(local,ensure_ascii=False,indent=2),encoding='utf-8')
            cases[mode][name]={'input':str(path.relative_to(ROOT)),'input_sha256':sha(path),'original_capture':str(capture.relative_to(ROOT)),'capture_sha256':sha(capture),'original_text':text,'local_rules':[f['rule_id'] for f in local['findings']],'native_diagnostics':len(re.findall(r'(?:^| )\d+\. ',text))}
    specs={
      'UniversityNameInvalid':('ошибки в названии университета',{'master':(['repair_combined_after'],['g_cover','g_structure']),'phd':(['g_baseline'],['g_phd_correct_heading'])}),
      'TitlePageMismatch':('титульный лист (много несоответствий)',{'master':(['repair_combined_after'],['g_cover','g_structure']),'phd':(['g_baseline'],['g_phd_correct_heading'])}),
      'WorkNameInvalid':('Ошибка в наименовании работы',{'phd':(['g_baseline'],['g_phd_structure','g_phd_correct_heading'])}),
      'RequiredHeadingsMissing':('Отсутствуют или неправильно оформлены заголовки структурных элементов',{'master':(['g_cover'],['g_structure']),'phd':(['g_phd_structure'],['g_phd_correct_heading'])}),
      'TocEmpty':('пустые структурные элементы',{'master':(['g_cover'],['g_toc_entries5','g_structure']),'phd':(['g_phd_structure'],['g_phd_correct_heading'])}),
      'TocSmall':('небольшие структурные элементы',{'master':(['g_toc_entries5','g_toc_entries10'],['g_toc_entries11','g_structure'])}),
      'AbstractTooShort':('небольшие структурные элементы',{'master':(['g_cover'],['g_structure'])}),
      'ThesisSizeTooSmall':('Маленький объем ВКР',{'master':(['g_toc47','g_chars43199','g_pages47','g_pages48'],['g_toc48','g_chars43200'])})}
    checks={}
    for suffix,(needle,modes) in specs.items():
        rule='Graduate.'+suffix;checks[rule]={}
        for mode,(positive,negative) in modes.items():
            rows=[]
            for name in positive+negative:
                case=cases[mode][name];native=needle in case['original_text']
                if suffix=='TocSmall':native=native and '"СОДЕРЖАНИЕ"' in case['original_text'].split('небольшие структурные элементы')[1].split('ID:')[0].split(' 2. ')[0]
                rows.append({'case':name,'expected':name in positive,'original':native,'local':rule in case['local_rules']})
            checks[rule][mode]={'pass':all(r['expected']==r['original']==r['local'] for r in rows),'results':rows}
    margin_rows=[]
    for name,expected in [('g_phd_correct_heading',True),('g_phd_margin15',True),('g_phd_left25',False)]:
        case=cases['phd'][name]
        # The 15 mm right-margin variant is retained as a failed attempt, not used to promote the left-only predicate.
        if name=='g_phd_margin15':continue
        margin_rows.append({'case':name,'expected':expected,'original':'размеры полей' in case['original_text'],'local':'Word.LeftMarginInvalid' in case['local_rules']})
    checks['Word.LeftMarginInvalid']={'phd':{'pass':all(r['expected']==r['original']==r['local'] for r in margin_rows),'results':margin_rows}}
    assert all(c['pass'] for modes in checks.values() for c in modes.values()),checks
    assert 'Замечаний нет.' in cases['phd']['g_phd_left25']['original_text']
    # Exact deficit values and no-diagnostic successes are independently asserted.
    for name in ['g_toc47','g_chars43199']:assert 'Не хватает 1 стр.' in cases['master'][name]['original_text']
    for name in ['g_toc48','g_chars43200']:assert 'Замечаний нет.' in cases['master'][name]['original_text']
    assert all('Маленький объем ВКР' not in c['original_text'] for c in cases['phd'].values())
    matrix=OUT/'comparison.json'
    scope={'build':230,'format':'docx','limits':'Finite native fixture predicates, ordinary text paragraphs only. No full cover/layout or arbitrary DOCX equivalence. No physical-page guarantee.'}
    matrix_checks={rule:{**modes,'pass':all(c['pass'] for c in modes.values())} for rule,modes in checks.items()}
    matrix.write_text(json.dumps({'scope':scope,'cases':cases,'checks':matrix_checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rp=ROOT/'scripts/testvkr-service/rules/rules_verified.json';registry=json.loads(rp.read_text(encoding='utf-8'))
    existing={r['rule_id']:r for r in registry['rules']}
    for rule,modes in checks.items():
        entry=existing.get(rule)
        if entry is None:entry={'rule_id':rule};registry['rules'].append(entry)
        entry.update({'verification_status':'verified_against_original','confidence':'high','verified_formats':['docx'],'verified_work_types':list(modes),'verified_policy':{},'evidence_refs':['evidence/graduate-structure/comparison.json'],'verification_evidence_sha256':sha(matrix),'verification_scope':scope,'verification_by_work_type':{mode:{'evidence_refs':['evidence/graduate-structure/comparison.json'],'verification_evidence_sha256':sha(matrix),'scope':{**scope,'work_type':mode}} for mode in modes},'automatic_repair':False,'observed_message':specs[rule.removeprefix('Graduate.')][0] if rule.startswith('Graduate.') else 'Документ содержит страницы, размеры полей на которых не соответствуют требованиям.'})
        if rule=='Word.LeftMarginInvalid':
            entry['verified_policy']={'MARGIN_LEFT_PHD_MM':25.0,'MARGIN_TOLERANCE_MM':1.0}
            entry['threshold_by_work_type']={'phd':25.0}
            entry['verification_by_work_type']['phd']['scope']['limits']='Only paired 30 mm failure versus 25 mm pass, one ordinary-text DOCX section with right/top/bottom 10/20/20 mm. Native tolerance is unmeasured.'
    rp.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={'native_cases_by_mode':{k:len(v) for k,v in cases.items()},'promoted_predicates':checks,
       'master_diagnostic_progression':{'baseline':cases['master']['repair_combined_after']['native_diagnostics'],'cover_corrected':cases['master']['g_cover']['native_diagnostics'],'structure_corrected':cases['master']['g_structure']['native_diagnostics'],'volume_corrected':cases['master']['g_chars43200']['native_diagnostics']},
       'master_size':{'minimum_equivalent_pages':48,'characters_per_page':900,'exact_text_boundary':43200,'counting_range':'abstract heading inclusive to first appendix heading exclusive; each paragraph trimmed; UTF-16 units','cached_docx_page_count_used':False,'toc_appendix_a_page_checked':True},
       'phd':{'ui_mode':'НКР аспиранта','required_toc_heading':'ОГЛАВЛЕНИЕ','work_name':'НАУЧНО-КВАЛИФИКАЦИОННАЯ РАБОТА','characters_100000_floor_rejected_for_docx':True,'left_margin_mm_passed':25,'left_margin_mm_failed':30,'margin_tolerance':'unmeasured','diagnostic_progression':[cases['phd']['g_baseline']['native_diagnostics'],cases['phd']['g_phd_correct_heading']['native_diagnostics'],cases['phd']['g_phd_left25']['native_diagnostics']]},
       'limits':scope['limits'],'automatic_content_repair':False}
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cases':summary['native_cases_by_mode'],'predicates':len(checks),'master_progression':summary['master_diagnostic_progression']}))
if __name__=='__main__':main()

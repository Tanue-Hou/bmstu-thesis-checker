"""Native multipage/doctoral pairs; exact format:mode evidence, never cartesian scope."""
import hashlib,json,re,copy
from pathlib import Path
from argparse import Namespace
from check_document import check_file
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/multipage-phd-repair'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cases={};items=json.loads((OUT/'inputs.json').read_text(encoding='utf-8'));args=Namespace(work_type='phd',skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False)
    for item in items:
        name=item['case'];p=OUT/(name+'.'+item['format']);capture=OUT/(name+'.original.json');assert sha(p)==item['sha256'];assert sha(Path('C:/Users/Tanue Hou/AppData/Local/TestVkrLab-20261014')/p.name)==sha(p)
        data=json.loads(capture.read_text(encoding='utf-8'));text=re.search(r'编辑 Value: (Файл:.*?) ID:',data['accessibility']['tree'])[1];assert '\\'+p.name+' ' in text
        result=check_file(p,args);(OUT/(name+'.local.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        cases[name]={'format':item['format'],'work_type':'phd','input_sha256':sha(p),'capture_sha256':sha(capture),'original_text':text,'local_rules':[f['rule_id'] for f in result['findings']],'parameters':item['parameters'],'native_diagnostics':len(re.findall(r' \d+\. ',text))}
    specs={'pdf:phd':{
        'Word.FontSizeTooSmall':('размер которых меньше 8 пт',['mp_small'],['mp_clean']),
        'Word.TextColorNotBlack':('цвет которых отличается от черного',['mp_red'],['mp_clean']),
        'Word.PageSizeNotA4':('не соответствуют формату А4',['mp_letter'],['mp_clean']),
        'Pic.PixelSizeTooLarge':('больше 16000000 пикселей',['mp_image_above'],['mp_clean']),
        'Struct.RequiredHeadingsMissing':('Отсутствуют или неправильно оформлены заголовки структурных элементов',['structure_no_abstract','structure_wrong_toc','mp_clean'],['structure_clean'])},
      'docx:phd':{
        'Word.FontSizeTooSmall':('размер которых меньше 8 пт',['phd_small','phd_combined'],['phd_complex_control']),
        'Word.FontSizeTooLarge':('размер которых превышает 18 пт',['phd_large','phd_combined'],['phd_complex_control']),
        'Word.TextColorNotBlack':('цвет которых отличается от черного',['phd_red','phd_combined'],['phd_complex_control']),
        'Word.PageSizeNotA4':('не соответствуют формату А4',['phd_letter','phd_combined'],['phd_complex_control'])}}
    checks={}
    for ctx,rules in specs.items():
        for rule,(needle,pos,neg) in rules.items():
            rows=[{'case':name,'expected':name in pos,'original':needle in cases[name]['original_text'],'local':rule in cases[name]['local_rules']} for name in pos+neg]
            checks.setdefault(rule,{})[ctx]={'pass':all(r['expected']==r['original']==r['local'] for r in rows),'results':rows}
    assert all(c['pass'] for modes in checks.values() for c in modes.values()),checks
    upper=[]
    for name in ['mp_font18_5','mp_font19','mp_font24','mp_font36','mp_font72']:
        assert 'размер которых превышает' not in cases[name]['original_text'];assert 'Word.FontSizeTooLarge' not in cases[name]['local_rules']
        upper.append({'case':name,'font_pt':cases[name]['parameters']['probe_font_pt'],'native_upper_warning':False})
    assert 'Замечаний нет.' in cases['phd_complex_control']['original_text']
    matrix=OUT/'comparison.json';matrix.write_text(json.dumps({'cases':cases,'checks':{r:{**m,'pass':all(c['pass'] for c in m.values())} for r,m in checks.items()},'pdf_upper_font_probes':upper,'scope':'Finite native predicates only, not full PDF structural/layout equivalence.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    path=ROOT/'scripts/testvkr-service/rules/rules_verified.json';registry=json.loads(path.read_text(encoding='utf-8'));byid={r['rule_id']:r for r in registry['rules']}
    policies={'Word.FontSizeTooSmall':{'FONT_SIZE_MIN_PT':8.0,'FONT_VIOLATION_MIN_CHARS':10},'Word.FontSizeTooLarge':{'FONT_SIZE_MAX_PT':18.0,'FONT_VIOLATION_MIN_CHARS':10},'Word.PageSizeNotA4':{'PAGE_WIDTH_MM':210.0,'PAGE_HEIGHT_MM':297.0,'PAGE_SIZE_TOLERANCE_MM':2.0},'Word.TextColorNotBlack':{'FONT_VIOLATION_MIN_CHARS':10},'Pic.PixelSizeTooLarge':{'IMAGE_PIXEL_AREA_MAX':16000000},'Struct.RequiredHeadingsMissing':{}}
    for rule,modes in checks.items():
        entry=byid.get(rule)
        if entry is None:
            entry={'rule_id':rule};registry['rules'].append(entry);byid[rule]=entry
        ref='evidence/multipage-phd-repair/comparison.json';digest=sha(matrix)
        if entry.get('verification_status')!='verified_against_original' or entry.get('evidence_refs')==[ref]:
            entry.update(evidence_refs=[ref],verification_evidence_sha256=digest,verification_scope={'limits':'Finite PDF abstract/PhD TOC heading predicates only'},observed_message=specs[next(iter(modes))][rule][0],verified_policy=policies[rule])
        entry.update(verification_status='verified_against_original',confidence='high')
        contexts=entry.setdefault('verification_by_context',{})
        for ctx in modes:
            previous=contexts.get(ctx);refs=[ref];hashes={ref:digest}
            if previous:
                for old in previous.get('evidence_refs',[]):
                    if old!=ref:refs.append(old);hashes[old]=sha(ROOT/old)
            scope={'format':ctx.split(':')[0],'work_type':'phd','build':230,'limits':('PDF exact normalized abstract and ОГЛАВЛЕНИЕ heading predicates; 3/13/14-page probes, not cover/TOC correspondence/pagination.' if rule.startswith('Struct.') else 'PDF embedded Times New Roman+ToUnicode, unrotated 1–3 pages, ordinary table text and <=1 PNG per page; finite size/color/page/image predicates.' if ctx.startswith('pdf:') else 'Single portrait DOCX section, ordinary body text and tables/one inline PNG; formatting predicates only; special content preserved, no margin repair.')}
            contexts[ctx]={'evidence_refs':refs,'verification_evidence_sha256':digest,'evidence_hashes':hashes,'scope':scope,'verified_policy':policies[rule]}
        entry['verified_formats']=sorted({c.split(':')[0] for c in contexts});entry['verified_work_types']=sorted({c.split(':')[1] for c in contexts})
    path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'native_cases':len(cases),'rule_context_pairs':sum(len(m) for m in checks.values()),'upper_font_probes':upper},ensure_ascii=False))
if __name__=='__main__':main()

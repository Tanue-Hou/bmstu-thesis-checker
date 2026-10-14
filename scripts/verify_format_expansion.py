"""Verify each runtime pair and migrate proof binding to format:work_type contexts."""
import copy,hashlib,json,re,struct,zipfile
from pathlib import Path
from argparse import Namespace
from lxml import etree
from check_document import check_file
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/format-expansion'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    items=[]
    for name in ['inputs.json','adaptive-margin-1.json','adaptive-margin-2.json','adaptive-margin-right.json','adaptive-margin-top.json','adaptive-margin-bottom.json','complex-pdf-inputs.json']:
        items+=json.loads((OUT/name).read_text(encoding='utf-8'))
    cases={};deltas=[]
    for item in items:
        name=item['case'];p=OUT/(name+'.'+item['format']);capture=OUT/(name+'.original.json')
        assert sha(p)==item['sha256']
        assert sha(Path('C:/Users/Tanue Hou/AppData/Local/TestVkrLab-20261014')/p.name)==sha(p)
        data=json.loads(capture.read_text(encoding='utf-8'));text=re.search(r'编辑 Value: (Файл:.*?) ID:',data['accessibility']['tree'])[1];assert '\\'+p.name in text
        local=check_file(p,Namespace(work_type='phd',skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False))
        (OUT/(name+'.local.json')).write_text(json.dumps(local,ensure_ascii=False,indent=2),encoding='utf-8')
        cases[name]={'format':item['format'],'work_type':'phd','input_sha256':sha(p),'capture_sha256':sha(capture),'original_text':text,'local_rules':[f['rule_id'] for f in local['findings']],'parameters':item['parameters']}
        if name.startswith('margin_'):
            parent=ROOT/item['parent_input'];assert sha(parent)==item['parent_sha256']
            with zipfile.ZipFile(parent) as a,zipfile.ZipFile(p) as b:
                changed=[n for n in a.namelist() if a.read(n)!=b.read(n)];assert changed==['word/document.xml']
                x,y=etree.fromstring(a.read(changed[0])),etree.fromstring(b.read(changed[0]))
                ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};axis=item['parameters'].get('axis','left');key='{'+ns['w']+'}'+axis
                xa,ya=x.xpath('//w:pgMar',namespaces=ns),y.xpath('//w:pgMar',namespaces=ns);assert len(xa)==len(ya)==1
                old,new=xa[0].get(key),ya[0].get(key);ya[0].set(key,old);assert etree.tostring(x)==etree.tostring(y)
            deltas.append({'case':name,'parent_sha256':sha(parent),'output_sha256':sha(p),'only_xml_attribute_changed':'w:pgMar/@w:'+axis,'before_twips':old,'after_twips':new})
    specs={
      'docx:phd':{
       'Word.LeftMarginInvalid':('размеры полей',['margin_24','margin_26','margin_24_5','margin_25_5','margin_twips1405','margin_twips1429'],['margin_24_9','margin_25_1','margin_twips1406','margin_twips1428']),
       'Word.RightMarginInvalid':('размеры полей',['margin_right_10_3'],['margin_right_10_1']),
       'Word.TopMarginInvalid':('размеры полей',['margin_top_20_3'],['margin_top_20_1']),
       'Word.BottomMarginInvalid':('размеры полей',['margin_bottom_20_3'],['margin_bottom_20_1']),
       'Word.FontSizeTooSmall':('размер которых меньше 8 пт',['complex_table7'],['complex_clean']),
       'Pic.PixelSizeTooLarge':('больше 16000000 пикселей',['complex_image_above'],['complex_clean'])},
      'pdf:phd':{
       'Word.FontSizeTooSmall':('размер которых меньше 8 пт',['pdf_font7','pdf_complex_table7'],['pdf_font8','pdf_clean','pdf_complex_clean']),
       'Pic.PixelSizeTooLarge':('больше 16000000 пикселей',['pdf_complex_image_above'],['pdf_complex_clean']),
       'Word.PageSizeNotA4':('не соответствуют формату А4',['pdf_letter'],['pdf_clean']),
       'Word.TextColorNotBlack':('цвет которых отличается от черного',['pdf_red'],['pdf_clean'])}}
    checks={}
    for ctx,rules in specs.items():
        for rule,(needle,pos,neg) in rules.items():
            rows=[{'case':name,'expected':name in pos,'original':needle in cases[name]['original_text'],'local':rule in cases[name]['local_rules']} for name in pos+neg]
            checks.setdefault(rule,{})[ctx]={'pass':all(r['expected']==r['original']==r['local'] for r in rows),'results':rows}
    assert all(c['pass'] for modes in checks.values() for c in modes.values()),checks
    assert 'Замечаний нет.' in cases['complex_clean']['original_text']
    upper={'case':'pdf_font18_5','original_upper_font_warning':'размер которых превышает 18 пт' in cases['pdf_font18_5']['original_text'],'status':'not_promoted','reason':'DOCX upper font predicate did not transfer to this PDF'}
    assert upper['original_upper_font_warning'] is False
    matrix=OUT/'comparison.json'
    matrix.write_text(json.dumps({'cases':cases,'checks':{r:{**m,'pass':all(c['pass'] for c in m.values())} for r,m in checks.items()},'unresolved':[upper]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'margin-modification-records.json').write_text(json.dumps(deltas,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rp=ROOT/'scripts/testvkr-service/rules/rules_verified.json';registry=json.loads(rp.read_text(encoding='utf-8'));byid={r['rule_id']:r for r in registry['rules']}
    for entry in registry['rules']:
        if entry.get('verification_status')!='verified_against_original' or 'verification_by_context' in entry:continue
        entry['verification_by_context']={f+':'+w:copy.deepcopy(entry.get('verification_by_work_type',{}).get(w,{'evidence_refs':entry['evidence_refs'],'verification_evidence_sha256':entry['verification_evidence_sha256'],'scope':entry['verification_scope']})) for f in entry['verified_formats'] for w in entry['verified_work_types']}
    targets={'Word.LeftMarginInvalid':('MARGIN_LEFT_PHD_MM',25.0),'Word.RightMarginInvalid':('MARGIN_RIGHT_MM',10.0),'Word.TopMarginInvalid':('MARGIN_TOP_MM',20.0),'Word.BottomMarginInvalid':('MARGIN_BOTTOM_MM',20.0)}
    policies={r:{key:value,'MARGIN_TOLERANCE_PHD_MM':0.2} for r,(key,value) in targets.items()}
    policies.update({'Word.FontSizeTooSmall':{'FONT_SIZE_MIN_PT':8.0,'FONT_VIOLATION_MIN_CHARS':10},'Word.PageSizeNotA4':{'PAGE_WIDTH_MM':210.0,'PAGE_HEIGHT_MM':297.0,'PAGE_SIZE_TOLERANCE_MM':2.0},'Word.TextColorNotBlack':{'FONT_VIOLATION_MIN_CHARS':10},'Pic.PixelSizeTooLarge':{'IMAGE_PIXEL_AREA_MAX':16000000}})
    for rule,modes in checks.items():
        entry=byid.get(rule)
        if entry is None:entry={'rule_id':rule};registry['rules'].append(entry)
        previous=entry.get('verification_status')=='verified_against_original'
        if entry.get('evidence_refs')==['evidence/format-expansion/comparison.json']:entry['verification_evidence_sha256']=sha(matrix)
        if not previous:
            entry.update({'evidence_refs':['evidence/format-expansion/comparison.json'],'verification_evidence_sha256':sha(matrix),'verification_scope':{'limits':'Finite format-expansion fixtures, build 230'},'verified_policy':policies[rule],'observed_message':specs[next(iter(modes))][rule][0]})
        entry.update({'verification_status':'verified_against_original','confidence':'high'})
        contexts=entry.setdefault('verification_by_context',{})
        for ctx in modes:
            file_type,mode=ctx.split(':')
            scope={'format':file_type,'work_type':mode,'build':230,'limits':('Single ordinary-text DOCX section; four independent margin axes; left boundary at adjacent twips; no landscape/section/gutter equivalence.' if rule in targets else 'Embedded Times New Roman, one unrotated PDF page, ordinary table text and at most one inline PNG/chart; tested finite properties only; PDF structures and font upper limit unvalidated.' if file_type=='pdf' else 'Ordinary table cells and one inline PNG/chart; tested size predicates, not full complex-document structure or drawing support.')}
            contexts[ctx]={'evidence_refs':['evidence/format-expansion/comparison.json'],'verification_evidence_sha256':sha(matrix),'scope':scope,'verified_policy':policies[rule]}
        entry['verified_formats']=sorted({c.split(':')[0] for c in contexts});entry['verified_work_types']=sorted({c.split(':')[1] for c in contexts})
        if rule in targets:entry['threshold_by_work_type']={'phd':targets[rule][1]}
    registry['verification_status']='partially_verified_against_original';rp.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={'native_cases':len(cases),'formats':{fmt:sum(c['format']==fmt for c in cases.values()) for fmt in ['docx','pdf']},'verified_rule_context_pairs':sum(len(m) for m in checks.values()),'margin_targets_mm':{'left':25,'right':10,'top':20,'bottom':20},'margin_tolerance_mm':0.2,'left_margin_allowed_twips':[1406,1428],'single_attribute_modification_records':len(deltas),'pdf_upper_font_rule':upper,'complex_clean_native_pass':True,'pdf_is_not_a_full_thesis_fixture':True,'automatic_pdf_or_table_repair':False}
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()

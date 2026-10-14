"""Verify retained master-mode fixtures without borrowing bachelor runtime evidence."""
import hashlib
import json
import re
import zipfile
from argparse import Namespace
from pathlib import Path
from lxml import etree
from check_document import check_file

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/dynamic-master'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def original(name):
    p = OUT / (name + '.original.json')
    text = re.search(r'编辑 Value: (Файл:.*?) ID:', json.loads(p.read_text(encoding='utf-8'))['accessibility']['tree'])[1]
    assert '\\' + name + '.docx' in text
    assert sha(OUT/(name+'.docx')) == sha(Path('C:/Users/Tanue Hou/AppData/Local/TestVkrLab-20261014')/(name+'.docx'))
    return text

def main():
    names = ['baseline','font_7','font_8','font_18','font_18_5','page_letter','color_black']
    args = Namespace(work_type='master',skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False)
    frozen = {x['case']:x['sha256'] for x in json.loads((OUT/'inputs.json').read_text(encoding='utf-8'))}
    cases = {}
    for name in names:
        p = OUT/(name+'.docx')
        assert sha(p) == frozen[name]
        local = check_file(p,args)
        (OUT/(name+'.local.json')).write_text(json.dumps(local,ensure_ascii=False,indent=2),encoding='utf-8')
        cases[name] = {'input_sha256':sha(p),'capture_sha256':sha(OUT/(name+'.original.json')),'original_text':original(name),'local_rules':[f['rule_id'] for f in local['findings']]}
    specs = {
        'Word.FontSizeTooSmall':('размер которых меньше 8 пт',['font_7'],['font_8','baseline']),
        'Word.FontSizeTooLarge':('размер которых превышает 18 пт',['font_18_5'],['font_18','baseline']),
        'Word.PageSizeNotA4':('не соответствуют формату А4',['page_letter'],['baseline']),
        'Word.TextColorNotBlack':('цвет которых отличается от черного',['baseline'],['color_black'])}
    checks = {}
    for rule,(needle,pos,neg) in specs.items():
        results = [{'case':n,'expected':n in pos,'original':needle in cases[n]['original_text'],'local':rule in cases[n]['local_rules']} for n in pos+neg]
        checks[rule] = {'pass':all(r['expected']==r['original']==r['local'] for r in results),'results':results}
    assert all(c['pass'] for c in checks.values())
    scope = {'format':'docx','work_type':'master','build':230,'limits':'Formatting fixture predicates only; bachelor title text retained to isolate mode. No master structural or full-program equivalence.'}
    matrix = OUT/'comparison.json'
    matrix.write_text(json.dumps({'scope':scope,'cases':cases,'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    registry_path = ROOT/'scripts/testvkr-service/rules/rules_verified.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    for rule in registry['rules']:
        if rule['rule_id'] not in checks: continue
        contexts = rule.setdefault('verification_by_work_type',{})
        contexts.setdefault('bachelor',{'evidence_refs':rule['evidence_refs'],'verification_evidence_sha256':rule['verification_evidence_sha256'],'scope':rule['verification_scope']})
        contexts['master'] = {'evidence_refs':['evidence/dynamic-master/comparison.json'],'verification_evidence_sha256':sha(matrix),'scope':scope}
        rule['verified_work_types'] = sorted(set(rule['verified_work_types']+['master']))
    registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    before,after = original('repair_combined_before'),original('repair_combined_after')
    cleared = {r:needle in before and needle not in after for r,(needle,_,_) in specs.items() if r!='Word.FontSizeTooLarge'}
    assert all(cleared.values())
    a,b = OUT/'repair_combined_before.docx',OUT/'repair_combined_after.docx'
    with zipfile.ZipFile(a) as za, zipfile.ZipFile(b) as zb:
        assert za.namelist()==zb.namelist()
        changed = [n for n in za.namelist() if za.read(n)!=zb.read(n)]
        assert changed==['word/document.xml']
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        assert etree.fromstring(za.read(changed[0])).xpath('//w:t/text()',namespaces=ns)==etree.fromstring(zb.read(changed[0])).xpath('//w:t/text()',namespaces=ns)
    summary={'scope':scope,'controlled_cases':len(cases),'repair_recheck_cases':2,'verified_rules':list(checks),'repair_cleared':cleared,'diagnostics_before':len(re.findall(r'(?:^| )\d+\. ',before)),'diagnostics_after':len(re.findall(r'(?:^| )\d+\. ',after)),'repair_input_sha256':sha(a),'repair_output_sha256':sha(b),'text_unchanged':True,'modified_zip_parts':changed,'unvalidated':['Master title page and structure','Page-count threshold','Line spacing and indent','Image limits in master mode','PDF','PhD mode']}
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__': main()

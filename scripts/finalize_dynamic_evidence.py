"""Independently verify original before/after outputs, package preservation and hashes."""
import hashlib
import json
import re
import zipfile
from pathlib import Path
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/dynamic-pairs'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def original(name):
    capture=json.loads((OUT/(name+'.original.json')).read_text(encoding='utf-8'))
    return re.search(r'编辑 Value: (Файл:.*?) ID:',capture['accessibility']['tree'])[1]

if __name__=='__main__':
    before,after=original('repair_combined_before'),original('repair_combined_after')
    inputs=json.loads((OUT/'repair-inputs.json').read_text(encoding='utf-8'))
    execution=json.loads((OUT/'repair-execution.json').read_text(encoding='utf-8'))
    a=OUT/'repair_combined_before.docx';b=OUT/'repair_combined_after.docx'
    assert sha(a)==inputs['before_sha256']==execution['input_sha256']
    assert sha(b)==inputs['after_sha256']==execution['output_sha256']
    predicates={'font_size':'размер которых меньше 8 пт','text_color':'цвет которых отличается от черного','page_size':'не соответствуют формату А4'}
    cleared={key:needle in before and needle not in after for key,needle in predicates.items()}
    with zipfile.ZipFile(a) as za,zipfile.ZipFile(b) as zb:
        assert za.namelist()==zb.namelist()
        changed=[n for n in za.namelist() if za.read(n)!=zb.read(n)]
        assert changed==['word/document.xml']
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        texts_a=etree.fromstring(za.read('word/document.xml')).xpath('//w:t/text()',namespaces=ns)
        texts_b=etree.fromstring(zb.read('word/document.xml')).xpath('//w:t/text()',namespaces=ns)
        assert texts_a==texts_b
    matrix=json.loads((OUT/'comparison.json').read_text(encoding='utf-8'))
    registry=json.loads((ROOT/'scripts/testvkr-service/rules/rules_verified.json').read_text(encoding='utf-8'))
    verified=[r for r in registry['rules'] if r.get('verification_status')=='verified_against_original' and 'bachelor' in r.get('verified_work_types',[])]
    assert all(r['verification_evidence_sha256']==sha(OUT/'comparison.json') for r in verified)
    summary={'original_controlled_cases':len(matrix['cases']),'original_repair_recheck_cases':2,
             'rules_verified_in_tested_scope':len(verified),'scope':'TestVkr build 230, DOCX, bachelor mode; tested predicates and fixtures only',
             'repair_original_diagnostics_cleared':cleared,'repair_original_diagnostics_count_before':len(re.findall(r'(?:^| )\d+\. ',before)),
             'repair_original_diagnostics_count_after':len(re.findall(r'(?:^| )\d+\. ',after)),
             'repair_changes':len(execution['changes']),'source_unchanged':True,'main_document_text_unchanged':True,
             'modified_zip_parts':changed,'other_zip_parts_unchanged':True,
             'unresolved':matrix['unresolved_differences'],
             'repair_log':str(Path(execution['change_log']).relative_to(ROOT)),
             'limits':['No full-program equivalence claim','PDF and other work types are not dynamically validated',
                       'Images, table text, headers/footers, fields, hyperlinks and special typography are not automatically repaired']}
    assert all(cleared.values())
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    legacy=ROOT/'evidence/2026-10-14'
    legacy_manifest={str(p.relative_to(legacy)):{'sha256':sha(p),'bytes':p.stat().st_size}
                     for p in sorted(legacy.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    (legacy/'manifest.json').write_text(json.dumps(legacy_manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest={str(p.relative_to(ROOT/'evidence')):{'sha256':sha(p),'bytes':p.stat().st_size}
              for p in sorted((ROOT/'evidence').rglob('*')) if p.is_file() and p != ROOT/'evidence/manifest.json'}
    (ROOT/'evidence/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))

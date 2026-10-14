"""Promote only rules with retained, hashed positive and negative original outputs."""
import hashlib
import json
import re
import sys
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import check_file

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    out = ROOT / 'evidence' / 'dynamic-pairs'
    inputs = json.loads((out / 'inputs.json').read_text(encoding='utf-8'))
    cases = {}
    args = Namespace(work_type='bachelor',skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False)
    for item in inputs:
        name = item['case']
        path = out / (name + '.docx')
        if sha(path) != item['sha256']:
            raise ValueError('Input changed: ' + name)
        capture = out / (name + '.original.json')
        data = json.loads(capture.read_text(encoding='utf-8'))
        text = re.search(r'编辑 Value: (Файл:.*?) ID:', data['accessibility']['tree'])[1]
        if ('\\' + name + '.docx') not in text:
            raise ValueError('Wrong original document result: ' + name)
        staged = Path('C:/Users/Tanue Hou/AppData/Local/TestVkrLab-20261014') / path.name
        if sha(staged) != sha(path):
            raise ValueError('Staged original input differs')
        local = check_file(path,args)
        (out / (name + '.local.json')).write_text(json.dumps(local,ensure_ascii=False,indent=2),encoding='utf-8')
        cases[name] = {'input_sha256':sha(path),'capture_sha256':sha(capture),'original_text':text,
                       'local_rules':[f['rule_id'] for f in local['findings']]}
    specs = {
        'Word.FontSizeTooSmall': ('размер которых меньше 8 пт', ['font_7','font_7_5'], ['font_8','baseline']),
        'Word.FontSizeTooLarge': ('размер которых превышает 18 пт', ['font_18_5'], ['font_18','baseline']),
        'Word.PageSizeNotA4': ('не соответствуют формату А4', ['page_letter'], ['baseline']),
        'Word.TextColorNotBlack': ('цвет которых отличается от черного', ['baseline'], ['color_black']),
        'Pic.PixelSizeTooLarge': ('больше 16000000 пикселей', ['image_above_16m'], ['image_16m']),
    }
    checks = {}
    for rule,(needle,positive,negative) in specs.items():
        results = []
        for name in positive + negative:
            expected = name in positive
            original = needle in cases[name]['original_text']
            local = rule in cases[name]['local_rules']
            results.append({'case':name,'expected':expected,'original':original,'local':local,
                            'pass':original==expected and local==expected})
        checks[rule]={'pass':all(r['pass'] for r in results),'results':results,
                      'scope':{'format':'docx','work_type':'bachelor','build':230,
                               'limits':'Validated fixture predicates and tested boundaries; not full document-role/counting equivalence.'}}
    mismatches = []
    for rule,name,needle in [('Word.LineSpacingInvalid','spacing_1','Междустрочный интервал'),
                              ('Word.FirstLineIndentInvalid','indent_0','Отступ первой строки')]:
        mismatches.append({'rule_id':rule,'case':name,'original':needle in cases[name]['original_text'],
                           'local':rule in cases[name]['local_rules'],'status':'not_promoted'})
    matrix={'cases':cases,'checks':checks,'unresolved_differences':mismatches}
    matrix_path=out/'comparison.json'
    matrix_path.write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    registry_path=ROOT/'scripts/testvkr-service/rules/rules_verified.json'
    registry=json.loads(registry_path.read_text(encoding='utf-8'))
    by_id={r['rule_id']:r for r in registry['rules']}
    policy={'Word.FontSizeTooSmall':{'FONT_SIZE_MIN_PT':8.0,'FONT_VIOLATION_MIN_CHARS':10},
            'Word.FontSizeTooLarge':{'FONT_SIZE_MAX_PT':18.0,'FONT_VIOLATION_MIN_CHARS':10},
            'Word.PageSizeNotA4':{'PAGE_WIDTH_MM':210.0,'PAGE_HEIGHT_MM':297.0,'PAGE_SIZE_TOLERANCE_MM':2.0},
            'Word.TextColorNotBlack':{'FONT_VIOLATION_MIN_CHARS':10},
            'Pic.PixelSizeTooLarge':{'IMAGE_PIXEL_AREA_MAX':16000000}}
    promoted=[]
    for rule,check in checks.items():
        if not check['pass']:
            continue
        entry=by_id.get(rule)
        if entry is None:
            entry={'rule_id':rule};registry['rules'].append(entry)
        entry.update({'verification_status':'verified_against_original','confidence':'high',
                      'evidence_refs':['evidence/dynamic-pairs/comparison.json'],
                      'verification_evidence_sha256':sha(matrix_path),'verified_formats':['docx'],
                      'verified_work_types':['bachelor'],'verified_policy':policy[rule],
                      'verification_scope':check['scope'], 'observed_message':specs[rule][0]})
        promoted.append(rule)
    registry['verification_status']='partially_verified_against_original'
    registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'original_cases':len(cases),'promoted':promoted,'unresolved':mismatches}))

if __name__=='__main__':
    main()

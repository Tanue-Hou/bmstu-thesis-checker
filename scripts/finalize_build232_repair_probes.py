"""Validate finite font repair probes without promoting the public repair gate."""
import hashlib,json,zipfile
from argparse import Namespace
from pathlib import Path
from lxml import etree
from check_document import check_file
from compare_native_trial import compare,load_capture,parse_diagnostics
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'evidence/agent-v027/repair-probes';controls=ROOT/'evidence/build-232/controls'
    results=[]
    for row in json.loads((out/'inputs.json').read_text(encoding='utf-8')):
        id=row['id'];source=controls/(row['source_control']+'.docx');copy=out/(id+'.docx')
        assert sha(source)==row['source_sha256'] and sha(copy)==row['copy_sha256']
        args=Namespace(work_type='master',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False)
        report=check_file(copy,args);capture=load_capture(out/(id+'.capture.json'))
        result=compare(report,capture)
        before_capture=load_capture(controls/(row['source_control']+'.capture.json'))
        compare(json.loads((controls/(row['source_control']+'.local.json')).read_text(encoding='utf-8')),before_capture)
        before=parse_diagnostics(Path(before_capture['text_path']).read_text(encoding='utf-8'),'docx')
        target='Word.FontSizeTooSmall' if id=='R01' else 'Word.FontSizeTooLarge'
        assert any(d['rule_id']==target for d in before)
        assert not any(d['rule_id']==target for d in result['native_diagnostics'])
        assert not any(f['rule_id']==target for f in report['findings'])
        assert [d['message'] for d in before if d['rule_id']!=target]==[d['message'] for d in result['native_diagnostics']]
        with zipfile.ZipFile(source) as a,zipfile.ZipFile(copy) as b:
            assert a.namelist()==b.namelist()
            changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
            assert changed==['word/document.xml']
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            assert etree.fromstring(a.read('word/document.xml')).xpath('//w:t/text()',namespaces=ns)==etree.fromstring(b.read('word/document.xml')).xpath('//w:t/text()',namespaces=ns)
        (out/(id+'.local.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        results.append({'id':id,'target':target,'native_before':True,'native_after':False,'other_native_messages_unchanged':True,'only_main_xml_changed':True,'text_preserved':True,'changed_runs':row['changes']})
    result={'cases':results,'all_pass':True,'build232_repair_open':False,
            'limits':'Two synthetic ordinary-body master font repairs only. No complex-document layout QA, protected-content native pair, A4/color/other-mode proof. Historical machinery used to generate experimental copies; no build232 public repair promotion.'}
    (out/'comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()

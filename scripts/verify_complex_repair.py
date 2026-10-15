"""Hash-bound native pairs and exact OOXML preservation; layout acceptance separate."""
import json,hashlib,zipfile
from pathlib import Path
from lxml import etree
from argparse import Namespace
from repair_build232 import plan
from check_document import check_file
from compare_native_trial import compare,load_capture
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'evidence/v028/complex-repair';rows=json.loads((out/'inputs.json').read_text(encoding='utf-8'));results=[]
    for row in rows:
        before,after=out/row['before'],out/row['after']
        assert sha(before)==row['before_sha256'] and sha(after)==row['after_sha256']
        generated,doc=plan(before,['font_size_anomalies'],14,'master',require_acceptance=False)
        with zipfile.ZipFile(before) as a,zipfile.ZipFile(after) as b:
            assert a.namelist()==b.namelist()
            assert all(a.read(n)==b.read(n) for n in a.namelist() if n!='word/document.xml')
            assert (doc.part.blob if generated['changes'] else a.read('word/document.xml'))==b.read('word/document.xml')
            # Reverse only explicitly logged size writes; every other XML node must match.
            xml=etree.fromstring(b.read('word/document.xml'));original=etree.fromstring(a.read('word/document.xml'))
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            for c in generated['changes']:
                target=xml.xpath(c['xml_path'],namespaces=ns)[0];old=original.xpath(c['xml_path'],namespaces=ns)[0]
                target.find('w:rPr/w:sz',ns).set('{'+ns['w']+'}val',old.find('w:rPr/w:sz',ns).get('{'+ns['w']+'}val'))
            assert etree.tostring(xml)==etree.tostring(original),'Unlogged XML edit'
        comparisons=[]
        for path,capture_id in [(before,row['id']+'B' if row['id']!='C03' else 'C01A'),(after,'C01A')]:
            # Identical-byte copies share a retained capture; never invent another execution.
            capture=load_capture(out/(capture_id+'.capture.json'))
            args=Namespace(work_type='master',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False)
            report=check_file(path,args);comparisons.append(compare(report,capture))
        marker='Контроль основного текста'
        if row['id']!='C03':
            rule='Word.FontSizeTooSmall' if row['id']=='C01' else 'Word.FontSizeTooLarge'
            assert any(d['rule_id']==rule and marker in d['message'] for d in comparisons[0]['native_diagnostics'])
            assert not any(d['rule_id']==rule and marker in d['message'] for d in comparisons[1]['native_diagnostics'])
            filtered=lambda c:[d['message'] for d in c['native_diagnostics'] if d['rule_id']!=rule]
            assert filtered(comparisons[0])==filtered(comparisons[1])
        else:assert generated['changes']==[] and before.read_bytes()==after.read_bytes()
        results.append({'id':row['id'],'changes':len(generated['changes']),'exact_output_matches_new_implementation':True,'all_other_xml_and_zip_parts_unchanged':True,'native_target_body_excerpt_removed':row['id']!='C03','negative_control':row['id']=='C03','after_capture_reused_from_identical_bytes':'C01A','layout_validation':'separate_required'})
    summary={'build':232,'cases':results,'native_execution_count':3,'all_structural_and_native_checks_pass':True,'layout_acceptance':False,'limits':'Three distinct byte inputs executed natively; identical-byte aliases reuse captures explicitly. Formula warnings remain intentionally; no whole-program pass claim.'}
    (out/'structural-native-validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
if __name__=='__main__':main()

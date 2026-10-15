"""Freeze only synthetic build232 probes; real theses remain private."""
import argparse,hashlib,json,shutil
from pathlib import Path
from argparse import Namespace
from check_document import check_file
from compare_native_trial import parse_diagnostics
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('private_capture_dir');a=p.parse_args();private=Path(a.private_capture_dir);out=ROOT/'evidence/build-232/controls';inputs=json.loads((out/'inputs.json').read_text(encoding='utf-8'));results=[]
    for row in inputs:
        id=row['id'];source=out/(id+'.docx');capture=json.loads((private/(id+'.capture.json')).read_text(encoding='utf-8'));assert sha(source)==capture['input_sha256']==row['sha256']
        for suffix in ['.original.txt','.uia.json','.screen-0.jpg']:shutil.copyfile(private/(id+suffix),out/(id+suffix))
        assert sha(out/(id+'.original.txt'))==capture['text_sha256'];assert sha(out/(id+'.screen-0.jpg'))==capture['screenshots'][0]['sha256']
        capture['text_path']=id+'.original.txt';(out/(id+'.capture.json')).write_text(json.dumps(capture,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        local=check_file(source,Namespace(work_type='master',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False))
        (out/(id+'.local.json')).write_text(json.dumps(local,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        native={d['rule_id'] for d in parse_diagnostics((out/(id+'.original.txt')).read_text(encoding='utf-8'),'docx')};local_ids={f['rule_id'] for f in local['findings']}
        expected_small=id=='Z01';expected_large=id=='Z04';small='Word.FontSizeTooSmall';large='Word.FontSizeTooLarge'
        results.append({**row,'native_small':small in native,'native_large':large in native,'local_small':small in local_ids,'local_large':large in local_ids,'pass':(small in native)==(small in local_ids)==expected_small and (large in native)==(large in local_ids)==expected_large,'text_sha256':capture['text_sha256'],'screenshot_sha256':capture['screenshots'][0]['sha256']})
    assert all(r['pass'] for r in results)
    report={'build':232,'executable_sha256':capture['executable_sha256'],'cases':results,'all_pass':True,'scope':'Four synthetic master DOCX font predicates: 7/8/18/18.5pt ordinary body. Other diagnostics intentionally not adjudicated; no general whole-rule, other-format or repair validation.'}
    (out/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'font_control_cases':len(results),'all_pass':True}))
if __name__=='__main__':main()

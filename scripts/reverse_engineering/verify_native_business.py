"""Cross-check branch snapshots, actual diagnostics, and the clean-room CLI."""
import hashlib,json,re,sys
from argparse import Namespace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from native_reference_cli import validate_native_run
from check_document import check_file
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    base=ROOT/'evidence/business-map-232';rows=[];sources={}
    for name,expected_units,expected_toc,missing in [('g_chars43199',43199,48,1),('g_chars43200',43200,48,None),('g_toc47',73679,47,1),('g_toc48',73679,48,None)]:
        folder=base/('native-volume-'+name+'-r3');trace=json.loads((folder/'trace.json').read_text());text=(folder/'native-result.txt').read_bytes().decode('utf-8');diagnostics=validate_native_run(trace,text)
        original=ROOT/'evidence/graduate-structure'/(name+'.docx');assert sha(original)==trace['probe_document']['sha256']
        assert sha(folder/'tracer-source.py.txt')==trace['tracer_sha256']
        state=next(h['volume_state'] for h in trace['breakpoint_hits'] if h['label']=='volume_decision')
        assert state['work_code']['prefix']=='1' and state['minimum']==48 and state['divisor']==900 and state['text_units_candidate']==expected_units and state['toc_page_candidate']==expected_toc and state['supplement_candidate']==0
        emitted=any(h['label']=='volume_insufficient_emit' for h in trace['breakpoint_hits']);assert emitted==(missing is not None)
        if emitted:assert state['candidate_after_sentinel']==47 and any('Не хватает 1 стр.' in d['message'] for d in diagnostics)
        else:assert state['candidate_after_sentinel']==-1 and not diagnostics
        local=check_file(original,Namespace(work_type='master',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False))
        local_size=[f for f in local['findings'] if f['rule_id']=='Graduate.ThesisSizeTooSmall'];assert bool(local_size)==emitted
        if local_size:assert local_size[0]['threshold']['missing_equivalent_pages']==missing
        sources[str((folder/'trace.json').relative_to(ROOT))]=sha(folder/'trace.json');sources[str((folder/'native-result.txt').relative_to(ROOT))]=sha(folder/'native-result.txt')
        rows.append({'case':name,'input_sha256':sha(original),'native_state':state,'insufficient_branch_hit':emitted,'native_diagnostics':len(diagnostics),'local_size_finding':bool(local_size),'native_report_exact_completed':True})
    folder=base/'native-direct-complex-reference-r3';trace=json.loads((folder/'trace.json').read_text());text=(folder/'native-result.txt').read_bytes().decode('utf-8');assert len(validate_native_run(trace,text))==13
    reference=ROOT/'evidence/v028/complex-repair';capture=json.loads((reference/'C01A.capture.json').read_text());assert capture['build']==232 and capture['work_type']=='master' and capture['input_sha256']==trace['probe_document']['sha256']==sha(reference/'C01A.docx')
    assert sha(reference/capture['text_path'])==capture['text_sha256']
    for image in capture['screenshots']:assert sha(reference/image['file'])==image['sha256']
    def normalize(value):return re.sub(r'\s+',' ',re.sub(r'^.*?(?=1\.)','',value,flags=re.S)).strip()
    assert normalize(text)==normalize((reference/capture['text_path']).read_text(encoding='utf-8'))
    for path in [folder/'trace.json',folder/'native-result.txt',reference/'C01A.capture.json',reference/capture['text_path'],base/'file-entry-decompilation-r1/function.c',base/'file-entry-decompilation-r1/status.txt']:
        sources[path.relative_to(ROOT).as_posix()]=sha(path)
    status=(base/'file-entry-decompilation-r1/status.txt').read_text();assert 'success=true' in status and 'entry=0047a528' in status
    out=base/'native-business-verification-r2';out.mkdir(exist_ok=False)
    sender=ROOT/'scripts/reverse_engineering/SendOwnedDrop.cs';assert all(json.loads((base/('native-volume-'+row['case']+'-r3')/'trace.json').read_text())['probe_document']['sender_source_sha256']==sha(sender) for row in rows)
    (out/'sender-source.cs.txt').write_bytes(sender.read_bytes())
    result={'status':'passed_bounded_instrumented_native_business_verification','target_sha256':trace['target_sha256'],'sources':sources,'master_volume':rows,'complex_reference':{'input_sha256':capture['input_sha256'],'numbered_diagnostics':13,'all_diagnostics_equal_after_whitespace_and_filename_normalization':True,'original_screenshot_hashes_verified':True},'file_entry_recovery':{'address':'0047a528','pseudocode_bytes':(base/'file-entry-decompilation-r1/function.c').stat().st_size,'status':'recovered_with_longer_decompile_timeout'},'limits':['Instrumented startup and entry; not an unmodified native run.','Only these master DOCX cases; no PDF/doctoral native harness claim.','Local build232 rule verification statuses and all repair gates remain unchanged.']}
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':result['status'],'volume_cases':len(rows),'complex_diagnostics_matched':13,'recovered_file_entry_bytes':result['file_entry_recovery']['pseudocode_bytes']}))
if __name__=='__main__':main()

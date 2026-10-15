"""Run native-reference and independent-check MCP tools on the same public PDF."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_native_pixels import publish
from native_reference_cli import validate_native_run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=ROOT/'evidence/business-map-232/pixel-boundaries-r1/inputs/pdf_4001x4000.pdf';out=ROOT/'evidence/business-map-232/pixel-mcp-default-r1';out.mkdir(exist_ok=False)
 requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},{'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'check_native_reference_experimental','arguments':{'file_path':str(source),'native_executable_path':str(ROOT.parent/'runtime/TestVkr232.exe'),'work_type':'phd'}}},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'check_thesis_document','arguments':{'file_path':str(source),'native_build':232,'work_type':'phd'}}}]
 run=subprocess.run([sys.executable,str(ROOT/'mcp/server.py')],input='\n'.join(json.dumps(r) for r in requests)+'\n',capture_output=True,text=True,encoding='utf-8',timeout=65)
 assert run.returncode==0,run.stderr
 replies=[json.loads(s) for s in run.stdout.splitlines()];assert len(replies)==3 and not any('error' in r for r in replies),replies
 native=replies[1]['result']['structuredContent'];local=replies[2]['result']['structuredContent'];assert native['source_sha256']==local['source_sha256']==sha(source)
 pixel=next(f for f in local['findings'] if f['rule_id']=='Pic.PixelSizeTooLarge');assert pixel['verification_status']=='verified_against_original' and pixel['verification_scope']['build']==232 and not pixel['action_eligibility']['automatic_repair_allowed']
 assert native['pixel_unit_codepage_fix_enabled'] and native['diagnostic_count']==10 and len([d for d in native['diagnostics'] if '16000000' in d['message']])==1
 private=Path(native['evidence_directory']);(private/'mcp-response.json').write_text(run.stdout,encoding='utf-8');publish(private,out/'native')
 trace=json.loads((out/'native/trace.json').read_text(encoding='utf-8'));text=(out/'native/native-result.txt').read_bytes().decode('utf-8');validate_native_run(trace,text,'phd','pdf',sha(source),True)
 assert sha(out/'native/tracer-source.py.txt')==sha(ROOT/'scripts/reverse_engineering/trace_startup_windows.py')==trace['tracer_sha256'] and trace['cleanup_verified']
 receipt={'status':'actual_native_and_independent_pixel_mcp_pass','server_version':replies[0]['result']['serverInfo']['version'],'native_build':232,'work_type':'phd','file_type':'pdf','input_sha256':sha(source),'native_diagnostics':native['diagnostic_count'],'local_pixel_count':pixel['threshold']['count_images'],'local_pixel_verification_scope':pixel['verification_scope'],'native_pixel_unit_corrected_in_process':True,'native_cleanup_verified':True,'automatic_image_repair_allowed':False,'raw_response_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'limits':'Raw MCP response stays private. Only same-input scoped detection and original-wrapper proof.'}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
if __name__=='__main__':main()

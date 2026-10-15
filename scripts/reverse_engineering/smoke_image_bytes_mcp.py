"""Same-input native232 / independent MCP checks of the ZIP-size diagnostic."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_native_pixels import publish
from native_reference_cli import validate_native_run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=ROOT/'evidence/business-map-232/image-bytes-boundaries-r1/inputs/above.docx';out=ROOT/'evidence/business-map-232/image-bytes-mcp-r1';out.mkdir(exist_ok=False)
 requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},{'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'check_native_reference_experimental','arguments':{'file_path':str(source),'native_executable_path':str(ROOT.parent/'runtime/TestVkr232.exe'),'work_type':'phd'}}},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'check_thesis_document','arguments':{'file_path':str(source),'native_build':232,'work_type':'phd'}}}]
 run=subprocess.run([sys.executable,str(ROOT/'mcp/server.py')],input='\n'.join(json.dumps(r) for r in requests)+'\n',capture_output=True,text=True,encoding='utf-8',timeout=65);assert run.returncode==0
 replies=[json.loads(s) for s in run.stdout.splitlines()];assert len(replies)==3 and not any('error' in r for r in replies),replies
 native=replies[1]['result']['structuredContent'];local=replies[2]['result']['structuredContent'];assert native['source_sha256']==local['source_sha256']==sha(source)
 f=next(f for f in local['findings'] if f['rule_id']=='Pic.FileSizeTooLarge');assert f['verification_status']=='verified_against_original' and f['verification_scope']['build']==232 and f['threshold']['value']==30000000
 assert native['diagnostic_count']==1 and '40 Mb' in native['diagnostics'][0]['message'] and f['threshold']['count_images']==1 and not f['action_eligibility']['automatic_repair_allowed']
 private=Path(native['evidence_directory']);(private/'mcp-response.json').write_text(run.stdout,encoding='utf-8');publish(private,out/'native')
 trace=json.loads((out/'native/trace.json').read_text(encoding='utf-8'));text=(out/'native/native-result.txt').read_bytes().decode('utf-8');validate_native_run(trace,text,'phd','docx',sha(source),True);assert trace['cleanup_verified']
 receipt={'status':'actual_same_input_image_bytes_mcp_pass','server_version':replies[0]['result']['serverInfo']['version'],'source_sha256':sha(source),'native_build':232,'native_diagnostics':1,'local_image_count':f['threshold']['count_images'],'local_verification_scope':f['verification_scope'],'actual_declared_bytes':f['threshold']['actual_max_bytes'],'threshold_bytes':f['threshold']['value'],'native_report_mb':f['threshold']['native_message_value'],'automatic_image_repair_allowed':False,'raw_response_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'limits':'One public synthetic case. Full response is private; detection agreement is not school compliance.'}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
if __name__=='__main__':main()

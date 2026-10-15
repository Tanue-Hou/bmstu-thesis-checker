"""Actual bounded native MCP check on the public anonymous complex fixture."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},{'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'check_native_reference_experimental','arguments':{'file_path':str(ROOT/'evidence/v028/complex-repair/C01A.docx'),'native_executable_path':str(ROOT.parent/'runtime/TestVkr232.exe'),'work_type':'master'}}}]
    run=subprocess.run([sys.executable,str(ROOT/'mcp/server.py')],input='\n'.join(json.dumps(r) for r in requests)+'\n',capture_output=True,text=True,encoding='utf-8',timeout=55)
    assert run.returncode==0,run.stderr
    replies=[json.loads(line) for line in run.stdout.splitlines()];assert len(replies)==3 and not any('error' in r for r in replies)
    tool_names=[t['name'] for t in replies[1]['result']['tools']];assert 'check_native_reference_experimental' in tool_names
    report=replies[2]['result']['structuredContent'];assert report['status']=='completed_instrumented_native_reference' and report['diagnostic_count']==13 and report['source_unchanged']
    private=Path(report['evidence_directory']);(private/'mcp-response.json').write_text(run.stdout,encoding='utf-8')
    summary={'status':'actual_native_mcp_pass','server_version':replies[0]['result']['serverInfo']['version'],'tool_count':len(tool_names),'native_build':report['native_build'],'input_sha256':report['source_sha256'],'diagnostic_count':report['diagnostic_count'],'source_unchanged':report['source_unchanged'],'native_text_sha256':report['native_text_sha256'],'raw_mcp_response_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'limits':'Raw response retained privately. Instrumented master DOCX only, not independent clone or new repair permission.'}
    out=ROOT/'evidence/business-map-232/native-mcp-smoke-final';out.mkdir(exist_ok=False);(out/'receipt.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
if __name__=='__main__':main()

"""Retain an actual local MCP initialize/list/preview/copy exchange."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/multipage-phd-repair'
def main():
    receipt=OUT/'mcp-smoke.json'
    if receipt.exists():raise SystemExit('Retained MCP smoke exists; verify rather than overwrite')
    args={'file_path':str(OUT/'phd_combined.docx'),'output_dir':str(OUT/'mcp_outputs'),'work_type':'phd','body_font_pt':14}
    requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}},{'jsonrpc':'2.0','id':2,'method':'tools/list'}]+[{'jsonrpc':'2.0','id':i,'method':'tools/call','params':{'name':name,'arguments':args}} for i,name in enumerate(['preview_thesis_fixes','fix_thesis_copy'],3)]
    p=subprocess.run([sys.executable,str(ROOT/'mcp/server.py')],input='\n'.join(json.dumps(r) for r in requests)+'\n',text=True,encoding='utf-8',capture_output=True,timeout=30,env={**os.environ,'PYTHONUTF8':'1'})
    assert p.returncode==0,p.stderr;responses=[json.loads(line) for line in p.stdout.splitlines()];assert len(responses)==4 and all('error' not in r for r in responses)
    assert responses[0]['result']['serverInfo']['version']=='0.2.4'
    for tool in responses[1]['result']['tools']:
        if tool['name'] in ('preview_thesis_fixes','fix_thesis_copy'):assert 'phd' in tool['inputSchema']['properties']['work_type']['enum']
    preview=responses[2]['result']['structuredContent'];copy=responses[3]['result']['structuredContent'];assert preview['dry_run'] and len(preview['changes'])==5;assert copy['source_unchanged'] and copy['after_rule_ids']==[]
    native_copy=OUT/'phd_combined_after.docx';assert hashlib.sha256(Path(copy['output_file']).read_bytes()).hexdigest()==hashlib.sha256(native_copy.read_bytes()).hexdigest()
    receipt.write_text(json.dumps({'requests':requests,'responses':responses,'exit_code':p.returncode,'stderr':p.stderr,'mcp_copy_identical_to_native_checked_copy':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'mcp_version':'0.2.4','exchanges':len(responses),'identical_native_checked_copy':True}))
if __name__=='__main__':main()

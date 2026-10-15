"""Actual MCP calls matched to retained same-input native font counters."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);private=ROOT.parent/'private_trials'/out.name;private.mkdir(exist_ok=False)
 audit=json.loads((ROOT/'evidence/business-map-232/font-audit-r1/audit.json').read_text());wanted={('smallSpacePad','master'),('tinyEqual','master'),('largeAfter101','master'),('characterInheritedLarge','phd'),('small11','phd')};cases=[r for r in audit['cases'] if (r['case'],r['work_type']) in wanted];assert len(cases)==len(wanted)
 requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'font-audit','version':'1'}}}]
 for i,row in enumerate(cases,2):requests.append({'jsonrpc':'2.0','id':i,'method':'tools/call','params':{'name':'check_thesis_document','arguments':{'file_path':str(ROOT/row['input']),'native_build':232,'work_type':row['work_type']}}})
 run=subprocess.run([sys.executable,str(ROOT/'mcp/server.py')],input=''.join(json.dumps(r)+'\n' for r in requests),text=True,encoding='utf-8',capture_output=True,timeout=120);assert run.returncode==0,run.stderr;raw=private/'responses.jsonl';raw.write_text(run.stdout,encoding='utf-8',newline='\n');responses=[json.loads(line) for line in run.stdout.splitlines()];assert len(responses)==len(requests);version=responses[0]['result']['serverInfo']['version'];rows=[]
 for response,row in zip(responses[1:],cases):
  result=response['result']['structuredContent'];assert result['source_sha256']==row['sha256']==sha(ROOT/row['input']);obs=result['native_word_observations'];assert obs['profile_supported'];found={f['rule_id']:f for f in result['findings']}
  for bucket in ['small','tiny','large']:assert obs['font_counters'][bucket]==row['font_state'][bucket+'_count']
  for bucket,rule in [('small','Word.FontSizeTooSmall'),('large','Word.FontSizeTooLarge')]:
   assert (rule in found)==(row['font_state'][bucket+'_count']>10)
   if rule in found:assert found[rule]['verification_status']=='verified_against_original' and found[rule]['verification_scope']['work_type']==row['work_type'] and sum(l['utf16_units'] for l in found[rule]['precise_locations']['occurrences'])==row['font_state'][bucket+'_count']
  rows.append({'case':row['case'],'work_type':row['work_type'],'source_sha256':row['sha256'],'native_capture':row['evidence_directory'],'font_counters':obs['font_counters'],'two_families_and_three_counters_agree':True})
 receipt={'status':'passed_actual_font_mcp_with_retained_same_input_native','server_version':version,'cases':rows,'raw_response_sha256':sha(raw),'limits':'Actual MCP transport; original executions retained by source hash, not rerun here. Font families/counters only; no school or repair certification.'};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'version':version,'cases':len(rows),'status':receipt['status']}))
if __name__=='__main__':main()

"""Exercise real MCP transport against hash-matched retained native drawing runs."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--audit',type=Path,default=ROOT/'evidence/business-map-232/drawing-audit-r1/audit.json');p.add_argument('--cases',nargs='+',default=['anchor501','labels11','anchorSquare501']);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False)
 private=ROOT.parent/'private_trials'/out.name;private.mkdir(exist_ok=False)
 audit=json.loads(a.audit.absolute().read_text(encoding='utf-8'));cases=[r.copy() for r in audit['cases'] if r['case'] in a.cases];assert {r['case'] for r in cases}==set(a.cases)
 for row in cases:
  if 'source_sha256' not in row:row['source_sha256']=row['sha256']
  if 'native_family_counts' not in row:
   state=row['drawing_state'];row['native_family_counts']={'Pic.FloatingImages':int(row['floating_image_emit']),'Pic.SmallLabels':int(row['small_labels_emit']),'Pic.FloatingShapes':int(state['count_slot_28']+state['count_slot_29']>0),'Pic.FloatingLabels':int(state['count_slot_30']+state['count_slot_32']>0)}
 requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'drawing-audit','version':'1'}}}]
 for i,row in enumerate(cases,2):requests.append({'jsonrpc':'2.0','id':i,'method':'tools/call','params':{'name':'check_thesis_document','arguments':{'file_path':str(ROOT/row['input']),'native_build':232,'work_type':'phd'}}})
 run=subprocess.run([sys.executable,str(ROOT/'mcp/server.py')],input=''.join(json.dumps(r)+'\n' for r in requests),text=True,encoding='utf-8',capture_output=True,timeout=120);assert run.returncode==0,run.stderr
 raw=private/'responses.jsonl';raw.write_text(run.stdout,encoding='utf-8',newline='\n');responses=[json.loads(line) for line in run.stdout.splitlines()];version=responses[0]['result']['serverInfo']['version'];rows=[]
 for response,row in zip(responses[1:],cases):
  report=response['result']['structuredContent'];assert report['source_sha256']==row['source_sha256']==sha(ROOT/row['input'])
  found={f['rule_id']:f for f in report['findings']};matched=[]
  for rule,count in row['native_family_counts'].items():
   assert (rule in found)==bool(count),(row['case'],rule)
   if rule in found:
    f=found[rule];expected_status='verified_against_original' if row.get('profile_supported',True) else 'pending_original_program_comparison';assert f['verification_status']==expected_status and not f['action_eligibility']['automatic_repair_allowed'];matched.append(rule)
  rows.append({'case':row['case'],'source_sha256':row['source_sha256'],'native_capture':row['evidence_directory'],'matched_families':matched,'all_four_families_agree':True,'drawing_repair_allowed':False})
 assert len(responses)==len(requests) and len(rows)==len(a.cases)
 receipt={'status':'passed_actual_mcp_with_retained_same_input_native','server_version':version,'cases':rows,'raw_response_sha256':sha(raw),'limits':'Actual local MCP calls; original runs retained by identical source hash, not rerun here. Four drawing families only, not full report or school equivalence.'}
 (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'version':version,'cases':len(rows),'status':receipt['status']}))
if __name__=='__main__':main()

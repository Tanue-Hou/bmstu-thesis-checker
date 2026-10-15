"""Freeze the final synthetic native wrapper runs and release evidence hashes."""
import hashlib,json,re,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from native_reference_cli import validate_native_run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'evidence/business-map-232';out=base/'native-modes-final-r1';out.mkdir(exist_ok=False);runs=[]
 for name,relative,mode in [('master_complex','v028/complex-repair/C01A.docx','master'),('phd_pdf','multipage-phd-repair/structure_no_abstract.pdf','phd')]:
  source=ROOT/'evidence'/relative;expected=sha(source);candidates=[]
  for p in (ROOT.parent/'private_trials/native-reference').glob('*/native/trace.json'):
   trace=json.loads(p.read_text(encoding='utf-8'))
   if trace.get('probe_document',{}).get('sha256')==expected and trace.get('cleanup_verified') and trace['probe_document'].get('requested_work_type')==mode:candidates.append(p)
  trace_path=max(candidates,key=lambda p:p.stat().st_mtime);native=trace_path.parent;trace=json.loads(trace_path.read_text(encoding='utf-8'));text=(native/'native-result.txt').read_bytes().decode('utf-8')
  ds=validate_native_run(trace,text,mode,source.suffix[1:],expected)
  dest=out/name;dest.mkdir()
  for filename in ['trace.json','native-result.txt','collection-length.txt','selected-mode.txt','tracer-source.py.txt']:shutil.copyfile(native/filename,dest/filename)
  shutil.copyfile(native.parent/'sender-source.cs.txt',dest/'sender-source.cs.txt')
  assert sha(dest/'tracer-source.py.txt')==trace['tracer_sha256']==sha(ROOT/'scripts/reverse_engineering/trace_startup_windows.py')
  assert sha(dest/'sender-source.cs.txt')==trace['probe_document']['sender_source_sha256']==sha(ROOT/'scripts/reverse_engineering/SendOwnedDrop.cs')
  runs.append({'case':name,'source_fixture':'evidence/'+relative,'source_sha256':expected,'work_type':mode,'file_type':source.suffix[1:],'diagnostic_count':len(ds),'cleanup_verified':True,'source_unchanged':sha(source)==expected})
 (out/'receipt.json').write_text(json.dumps({'status':'final_native_hardening_pass','runs':runs,'supersedes':'Earlier traces contain a stale generic no-forced-invocation limitation; explicit intervention records remain authoritative. These final traces correct the limitation and verify owned-process exit.'},indent=2),encoding='utf-8')
 log=base/'regression-v0210-final2.log';count=int(re.search(r'Ran (\d+) tests',log.read_text(encoding='utf-8'))[1]);assert '\nOK\n' in log.read_text(encoding='utf-8')
 repair=ROOT/'scripts/repair_build232.py';assert sha(repair)=='1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad'
 evidence=[]
 for folder in ['native-modes-r1','native-complex-phd-r1','native-modes-audit-r1','native-modes-final-r1','native-mcp-phd-pdf-r1','native-mcp-phd-pdf-r2']:
  evidence.extend(p for p in (base/folder).rglob('*') if p.is_file())
 evidence.extend([log,base/'regression-v0210.log',base/'regression-v0210-final.log',base/'STAGE_v0210_FINAL.zh.md'])
 paths=['README.md','CHANGELOG.md','.codex-plugin/plugin.json','mcp/server.py','scripts/native_reference_cli.py','scripts/repair_build232.py','skills/bmstu-thesis-checker/SKILL.md','docs/NATIVE_REFERENCE_CLI.zh.md','docs/RULE_CHAIN.zh.md','docs/VERSION_HISTORY.zh.md','releases/v0.2.10.md','tests/test_native_reference.py']
 paths.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts/reverse_engineering').glob('*.py') if p.name in ['freeze_native_modes.py','audit_native_modes.py','verify_native_modes.py','trace_startup_windows.py','smoke_native_mcp.py'])
 paths.append('scripts/reverse_engineering/SendOwnedDrop.cs')
 manifest={'release':'0.2.10','regression_tests_passed':count,'repair_implementation_unchanged':True,'source_files':{p:sha(ROOT/p) for p in paths},'evidence_files':{p.relative_to(ROOT).as_posix():sha(p) for p in evidence},'limits':'Finite instrumented native reference validation; residual pixel-unit encoding difference retained. Independent replica and new repair actions not accepted.'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps({'tests':count,'evidence_files':len(evidence),'final_runs':len(runs)}))
if __name__=='__main__':main()

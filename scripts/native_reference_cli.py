"""Experimental Windows native-reference CLI; original TestVkr232 is required.

Runs a newly owned hidden form through a documented instrumented entry. Inputs
and results stay in the private trials directory. This is not a standalone clone.
"""
import argparse,hashlib,json,os,re,shutil,subprocess,sys,uuid,struct
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT.parent/'private_trials/native-reference'
REVERSE=ROOT/'scripts/reverse_engineering'
IDENTITY='5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def resolved(path):return Path(os.path.abspath(path)).resolve()
def validate_native_run(trace,text,work_type="master",file_type="docx",source_sha256=None):
    if work_type not in {"master","phd"} or file_type not in {"docx","pdf"}:raise ValueError("Unsupported native mode or format")
    if trace.get('target_sha256')!=IDENTITY or trace.get('error') or not trace.get('binary_unchanged'):raise ValueError('Native target / trace integrity failed')
    probe=trace.get('probe_document',{})
    if source_sha256 is not None and probe.get('sha256')!=source_sha256:raise ValueError('Native probe content differs from original input')
    if trace.get('cleanup_errors'):raise ValueError('Owned native process cleanup failed')
    if not probe.get('unchanged') or probe.get('sender_exit_code')!=0:raise ValueError('Input changed or native report collection incomplete')
    units=len(text.encode('utf-16le'))//2
    if probe.get('report_utf16_units_expected')!=units or probe.get('report_utf16_units_collected')!=units:raise ValueError('Native report collection length mismatch or missing receipt')
    labels={h['label'] for h in trace['breakpoint_hits']}
    if not {'file_check_entry',file_type+'_load','structure_volume_check','file_check_return'}<=labels:raise ValueError('Required native entry / loader / return not observed')
    if probe.get('requested_work_type',work_type)!=work_type or probe.get('file_type',file_type)!=file_type:raise ValueError('Requested native mode or format differs from trace')
    expected_code={'master':'1','phd':'5'}[work_type]
    selections=[h.get('volume_state',{}) for h in trace['breakpoint_hits'] if h['label']=='volume_selected_threshold']
    if len(selections)!=1 or selections[0].get('work_code',{}).get('prefix')!=expected_code:raise ValueError('Actual native mode was not observed or differs from request')
    if selections[0].get('minimum')!={'master':48,'phd':0}[work_type] or selections[0].get('divisor')!=900:raise ValueError('Native mode threshold differs from validated branch')
    if any(e.get('exception_code')=='0xc0000005' for e in trace['events']):raise ValueError('Native access violation observed')
    changes=[c for c in trace['large_buffer_codepage_calls'] if 'intervention_codepage' in c]
    if len(changes)!=8 or {c.get('matched_resource') for c in changes}!={'RU_FORMS','RU_PREFS','RU_ENDS','TITUL'} or any(c.get('codepage')!=0 or c.get('intervention_codepage')!=1251 for c in changes):raise ValueError('Native resource intervention set differs')
    if not text.lstrip().startswith('Файл:'):raise ValueError('Not a completed native report')
    matches=list(re.finditer(r'(?m)^(\d+)\.\s+',text));diagnostics=[]
    for i,match in enumerate(matches):
        number=int(match.group(1))
        if number!=i+1:raise ValueError('Native numbering is incomplete or reordered')
        end=matches[i+1].start() if i+1<len(matches) else len(text)
        diagnostics.append({'number':number,'message':text[match.end():end].strip()})
    if not diagnostics and 'Замечаний нет.' not in text:raise ValueError('Missing diagnostics and native no-remarks completion text')
    return diagnostics
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--native-exe',type=Path,default=ROOT.parent/'runtime/TestVkr232.exe');p.add_argument('--work-type',choices=['master','phd'],default='master');p.add_argument('--out',type=Path);p.add_argument('--timeout',type=float,default=25);a=p.parse_args()
    if os.name!='nt':raise RuntimeError('This native reference harness requires Windows')
    if struct.calcsize('P')!=8:raise RuntimeError('Native reference requires 64-bit Python on 64-bit Windows')
    source=resolved(a.input);binary=resolved(a.native_exe)
    if source.suffix.lower() not in {'.docx','.pdf'}:raise ValueError('Native harness accepts DOCX/PDF only')
    file_type=source.suffix.lower()[1:]
    if sha(binary)!=IDENTITY:raise ValueError('Unsupported native build; re-identify before execution')
    if not 5<=a.timeout<=30:raise ValueError('Timeout must be between5 and30 seconds')
    original_hash=sha(source)
    out=resolved(a.out or PRIVATE/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]))
    if not out.is_relative_to(ROOT.parent/'private_trials'):raise ValueError('Native input copies and reports must remain inside private_trials')
    out.mkdir(parents=True,exist_ok=False)
    copy=out/('input.'+file_type);shutil.copyfile(source,copy)
    if sha(copy)!=original_hash:raise ValueError('Input copy hash mismatch')
    isolated_binary=out/'TestVkr232.exe';shutil.copyfile(binary,isolated_binary)
    if sha(isolated_binary)!=IDENTITY:raise ValueError('Native executable copy hash mismatch')
    sender=out/'SendOwnedDrop.exe';sender_source=REVERSE/'SendOwnedDrop.cs'
    shutil.copyfile(sender_source,out/'sender-source.cs.txt')
    compiler=Path(os.environ.get('WINDIR','C:/Windows'))/'Microsoft.NET/Framework/v4.0.30319/csc.exe'
    build=subprocess.run([str(compiler),'/nologo','/platform:x86','/out:'+str(sender),str(sender_source)],capture_output=True)
    (out/'sender-build.log').write_bytes(build.stdout+build.stderr)
    if build.returncode:raise RuntimeError('Sender compiler failed; see private build log')
    native=out/'native';command=[sys.executable,str(REVERSE/'trace_startup_windows.py'),'--binary',str(isolated_binary),'--dictionary-cp1251','--probe-document',str(copy),'--direct-file-entry','--work-type',a.work_type,'--out',str(native),'--seconds',str(a.timeout),'--sender-executable',str(sender)]
    execution=subprocess.run(command,capture_output=True,timeout=a.timeout+15)
    (out/'execution.log').write_bytes(execution.stdout+execution.stderr)
    if execution.returncode:raise RuntimeError('Native trace failed; see private execution log')
    trace=json.loads((native/'trace.json').read_text(encoding='utf-8'));text_path=native/'native-result.txt';text=text_path.read_bytes().decode('utf-8')
    diagnostics=validate_native_run(trace,text,a.work_type,file_type,original_hash)
    if sha(copy)!=original_hash:raise ValueError('Native input copy changed or differs from source')
    if not trace.get('cleanup_verified'):raise ValueError('Owned process exit was not verified')
    if sha(source)!=original_hash:raise ValueError('Original input changed during native run')
    if sha(binary)!=IDENTITY:raise ValueError('Original native executable changed during run')
    report={'status':'completed_instrumented_native_reference','experimental':True,'native_build':232,'executable_sha256':IDENTITY,'source_sha256':original_hash,'source_unchanged':True,'work_type':a.work_type,'file_type':file_type,'diagnostic_count':len(diagnostics),'diagnostics':diagnostics,'evidence_directory':str(out),'trace_sha256':sha(native/'trace.json'),'native_text_sha256':sha(text_path),'sender_source_sha256':sha(sender_source),'sender_binary_sha256':sha(sender),'limits':['Requires the original executable and Windows; not a standalone open-source replacement.','Uses process-local resource codepage and controlled file-entry interventions.','Only instrumented master / NKR postgraduate DOCX/PDF references; no rule or repair promotion implied.','Known residual codepage defect: the pixel unit in oversized-image diagnostics may be garbled; raw native text is preserved.']}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=True))
if __name__=='__main__':
    try:main()
    except Exception as exc:print(json.dumps({'status':'failed','error':str(exc)},ensure_ascii=True));sys.exit(1)

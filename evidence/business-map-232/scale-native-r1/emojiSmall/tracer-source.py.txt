"""Bounded Windows CLI debugger for an OWNED hash-bound TestVkr232 process.

No attachment to existing processes, UI input, disk patching or locale changes.
One-shot software breakpoints record actual registers, then restore the byte.
"""
import argparse,ctypes as C,hashlib,json,struct,time,zlib,subprocess
from ctypes import wintypes as W
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
IDENTITY='5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0'
D=W.DWORD;P=C.c_void_p;H=W.HANDLE
class STARTUPINFO(C.Structure):
    _fields_=[('cb',D),('lpReserved',W.LPWSTR),('lpDesktop',W.LPWSTR),('lpTitle',W.LPWSTR),('dwX',D),('dwY',D),('dwXSize',D),('dwYSize',D),('dwXCountChars',D),('dwYCountChars',D),('dwFillAttribute',D),('dwFlags',D),('wShowWindow',W.WORD),('cbReserved2',W.WORD),('lpReserved2',P),('hStdInput',H),('hStdOutput',H),('hStdError',H)]
class PROCESS_INFORMATION(C.Structure):
    _fields_=[('hProcess',H),('hThread',H),('dwProcessId',D),('dwThreadId',D)]
class EXCEPTION_RECORD(C.Structure):
    _fields_=[('code',D),('flags',D),('record',P),('address',P),('parameter_count',D),('information',C.c_size_t*15)]
class EXCEPTION_INFO(C.Structure):_fields_=[('record',EXCEPTION_RECORD),('first_chance',D)]
class CREATE_INFO(C.Structure):
    _fields_=[('file',H),('process',H),('thread',H),('base',P),('debug_offset',D),('debug_size',D),('tls',P),('start',P),('name',P),('unicode',W.WORD)]
class LOAD_INFO(C.Structure):
    _fields_=[('file',H),('base',P),('debug_offset',D),('debug_size',D),('name',P),('unicode',W.WORD)]
class EVENT_UNION(C.Union):_fields_=[('exception',EXCEPTION_INFO),('create',CREATE_INFO),('load',LOAD_INFO),('raw',C.c_byte*160)]
class DEBUG_EVENT(C.Structure):_fields_=[('code',D),('pid',D),('tid',D),('u',EVENT_UNION)]
class FLOAT_SAVE(C.Structure):
    _fields_=[(n,D) for n in ['ControlWord','StatusWord','TagWord','ErrorOffset','ErrorSelector','DataOffset','DataSelector']]+[('RegisterArea',C.c_byte*80),('Cr0NpxState',D)]
class WOW64_CONTEXT(C.Structure):
    _pack_=4
    _fields_=[('ContextFlags',D)]+[(n,D) for n in ['Dr0','Dr1','Dr2','Dr3','Dr6','Dr7']]+[('FloatSave',FLOAT_SAVE)]+[(n,D) for n in ['SegGs','SegFs','SegEs','SegDs','Edi','Esi','Ebx','Edx','Ecx','Eax','Ebp','Eip','SegCs','EFlags','Esp','SegSs']]+[('ExtendedRegisters',C.c_byte*512)]
class PROCESS_ENTRY(C.Structure):
    _fields_=[('size',D),('usage',D),('pid',D),('heap',C.c_size_t),('module',D),('threads',D),('parent',D),('priority',W.LONG),('flags',D),('exe',W.WCHAR*260)]
class THREAD_ENTRY(C.Structure):
    _fields_=[('size',D),('usage',D),('tid',D),('pid',D),('base_priority',W.LONG),('delta_priority',W.LONG),('flags',D)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,default=ROOT.parent/'runtime/TestVkr232.exe');p.add_argument('--out',type=Path,required=True);p.add_argument('--seconds',type=float,default=8);p.add_argument('--argument',default='--help');p.add_argument('--russian',action='store_true');p.add_argument('--russian-suspended',action='store_true');p.add_argument('--trace-codepage',action='store_true');p.add_argument('--dictionary-cp1251',action='store_true');p.add_argument('--probe-document',type=Path);p.add_argument('--direct-file-entry',action='store_true');p.add_argument('--drawing-trace',action='store_true');p.add_argument('--font-trace',action='store_true');p.add_argument('--scale-trace',action='store_true');p.add_argument('--paragraph-trace',action='store_true');p.add_argument('--image-bytes-trace',action='store_true');p.add_argument('--pixel-trace',action='store_true');p.add_argument('--pixel-cp1251',action='store_true');p.add_argument('--work-type',choices=['master','phd'],default='master');p.add_argument('--sender-executable',type=Path,default=ROOT.parent/'runtime/SendOwnedDrop.exe');a=p.parse_args()
    # Additional business trace uses the same bounded, owned process.
    if a.scale_trace:a.font_trace=True
    if a.direct_file_entry and not a.probe_document:raise ValueError('Direct entry requires a synthetic document probe')
    if a.probe_document and not a.direct_file_entry:raise ValueError('Only controlled direct-entry probes are supported; natural cross-process HDROP is not validated')
    if a.dictionary_cp1251:a.trace_codepage=True
    if a.russian_suspended:a.russian=True
    if not 0<a.seconds<=30:raise ValueError('Trace duration must be <=30 seconds')
    drawing_trace=a.drawing_trace
    image_bytes_trace=a.image_bytes_trace
    probe_raw=None
    # Opt-in business tracing is kept separate from the default wrapper.
    pixel_trace=a.pixel_trace
    pixel_cp1251=a.pixel_cp1251
    if pixel_cp1251 and not pixel_trace:raise ValueError('Pixel intervention requires pixel tracing')
    pixel_literal=raw_pixel_literal=None
    if a.probe_document:
        a.probe_document=a.probe_document.resolve()
        if not a.dictionary_cp1251 or not any(a.probe_document.is_relative_to(root) for root in [ROOT/'evidence',ROOT.parent/'private_trials']) or a.probe_document.suffix.lower() not in {'.docx','.pdf'}:raise ValueError('Probe requires dictionary intervention and a controlled evidence/private-trials DOCX/PDF')
        probe_raw=a.probe_document.read_bytes()
    binary=a.binary.resolve();raw=binary.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=IDENTITY:raise ValueError('Target identity mismatch')
    if pixel_trace:
        raw_pixel_literal=raw[3033452:3033464]
        if raw_pixel_literal!=bytes.fromhex('20efe8eaf1e5ebe5e9293a20'):raise ValueError('Pixel literal identity mismatch')
        pixel_literal=raw_pixel_literal
    dictionary_buffers={}
    if a.trace_codepage:
        inventory=json.loads((ROOT/'evidence/business-map-232/pe-resources-REA.json').read_text(encoding='utf-8'))
        if inventory['normalized_result']['artifact']['sha256']!=IDENTITY:raise ValueError('Resource evidence identity mismatch')
        for resource in inventory['normalized_result']['resources']:
            name=resource['name'].get('name')
            if resource['type'].get('name')!='TESTDATA' or name not in ['RU_FORMS','RU_PREFS','RU_ENDS','TITUL']:continue
            location=resource['payload']['location'];data=raw[location['offset']:location['offset']+location['bytes']]
            if hashlib.sha256(data).hexdigest()!=resource['payload']['sha256']:raise ValueError('Resource payload mismatch')
            decoder=zlib.decompressobj();decoded=decoder.decompress(data,16*1024*1024)
            if not decoder.eof or decoder.unconsumed_tail or decoder.unused_data:raise ValueError('Incomplete/budget-exceeded dictionary')
            dictionary_buffers[(len(decoded),hashlib.sha256(decoded).hexdigest())]=name
    out=a.out.resolve()
    if not any(out.is_relative_to(root) for root in [ROOT/'evidence',ROOT.parent/'private_trials']):raise ValueError('Trace output must stay inside evidence/private_trials')
    out.mkdir(parents=True,exist_ok=False)
    (out/'tracer-source.py.txt').write_bytes(Path(__file__).read_bytes())
    k=C.WinDLL('kernel32',use_last_error=True)
    prototypes={
      'CreateProcessW':([W.LPCWSTR,W.LPWSTR,P,P,W.BOOL,D,P,W.LPCWSTR,C.POINTER(STARTUPINFO),C.POINTER(PROCESS_INFORMATION)],W.BOOL),
      'WaitForDebugEvent':([C.POINTER(DEBUG_EVENT),D],W.BOOL),'ContinueDebugEvent':([D,D,D],W.BOOL),
      'ReadProcessMemory':([H,P,P,C.c_size_t,C.POINTER(C.c_size_t)],W.BOOL),'WriteProcessMemory':([H,P,P,C.c_size_t,C.POINTER(C.c_size_t)],W.BOOL),
      'VirtualAllocEx':([H,P,C.c_size_t,D,D],P),
      'Wow64GetThreadContext':([H,C.POINTER(WOW64_CONTEXT)],W.BOOL),'Wow64SetThreadContext':([H,C.POINTER(WOW64_CONTEXT)],W.BOOL),
      'OpenThread':([D,W.BOOL,D],H),'OpenProcess':([D,W.BOOL,D],H),'CloseHandle':([H],W.BOOL),'TerminateProcess':([H,W.UINT],W.BOOL),'WaitForSingleObject':([H,D],D),'FlushInstructionCache':([H,P,C.c_size_t],W.BOOL),'QueryFullProcessImageNameW':([H,D,W.LPWSTR,C.POINTER(D)],W.BOOL)}
    for name,(args,result) in prototypes.items():getattr(k,name).argtypes=args;getattr(k,name).restype=result
    extra={'CreateToolhelp32Snapshot':([D,D],H),'Process32FirstW':([H,C.POINTER(PROCESS_ENTRY)],W.BOOL),'Process32NextW':([H,C.POINTER(PROCESS_ENTRY)],W.BOOL),'Thread32First':([H,C.POINTER(THREAD_ENTRY)],W.BOOL),'Thread32Next':([H,C.POINTER(THREAD_ENTRY)],W.BOOL),'DebugActiveProcess':([D],W.BOOL),'ResumeThread':([H],D)}
    for name,(args,result) in extra.items():getattr(k,name).argtypes=args;getattr(k,name).restype=result
    def checked(ok):
        if not ok:raise C.WinError(C.get_last_error())
    pi=PROCESS_INFORMATION();si=STARTUPINFO();si.cb=C.sizeof(si);si.dwFlags=1;si.wShowWindow=0
    application=binary
    command='"'+str(binary)+'" '+a.argument
    if a.russian:
        if a.argument!='--help':raise ValueError('Russian probe currently accepts only --help')
        folder=ROOT.parent/'runtime/locale-emulator-2.5.0.1'
        application=folder/'RussianLocaleProbe.exe'
        command=' '.join('"'+str(part)+'"' for part in [application,folder,binary,out])
        if a.russian_suspended:command+=' suspended'
    cmd=C.create_unicode_buffer(command)
    checked(k.CreateProcessW(str(application),cmd,None,None,False,(0 if a.russian_suspended else 1 if a.russian else 2)|0x08000000,None,str(out),C.byref(si),C.byref(pi)))
    target_handle=pi.hProcess;target_pid=None if a.russian else pi.dwProcessId;owned={int(pi.dwProcessId):pi.hProcess}
    def read(addr,size):
        buf=C.create_string_buffer(size);done=C.c_size_t();checked(k.ReadProcessMemory(target_handle,addr,buf,size,C.byref(done)));return buf.raw[:done.value]
    def write(addr,data):
        buf=C.create_string_buffer(data);done=C.c_size_t();checked(k.WriteProcessMemory(target_handle,addr,buf,len(data),C.byref(done)));checked(k.FlushInstructionCache(target_handle,addr,len(data)))
    def signed(addr):return int.from_bytes(read(addr,4),'little',signed=True)
    def unsigned(addr):return int.from_bytes(read(addr,4),'little')
    def unicode_object(addr):
        pointer=unsigned(addr);length=signed(pointer-4)
        if not 0<=length<=1000000:raise ValueError('String budget')
        return {'length':length,'prefix':read(pointer,min(length,256)*2).decode('utf-16le',errors='replace')}
    events=[];hits=[];breakpoints={};base=None;exited=False;error=None;started=time.monotonic();form_pointer=None;fault_count=0;stop_reason='duration_limit';cleanup_errors=[];pending_steps={};codepage_calls=[];api_calls=0;sender=None;sender_status=None
    pixel_api_active=False;pixel_api_calls=0;pixel_output_object=None;pixel_dimensions={};pixel_hit_counts={}
    event_limit=4096 if a.trace_codepage or a.paragraph_trace or a.font_trace else 512
    try:
        if a.russian_suspended:
            candidates=[]
            while time.monotonic()-started<min(a.seconds,8):
                snap=k.CreateToolhelp32Snapshot(2,0)
                if snap==C.c_void_p(-1).value:raise C.WinError(C.get_last_error())
                try:
                    item=PROCESS_ENTRY();item.size=C.sizeof(item);ok=k.Process32FirstW(snap,C.byref(item));candidates=[]
                    while ok:
                        if item.parent==pi.dwProcessId and item.exe.lower()==binary.name.lower():candidates.append(int(item.pid))
                        ok=k.Process32NextW(snap,C.byref(item))
                finally:k.CloseHandle(snap)
                if candidates:break
                time.sleep(.05)
            if len(candidates)!=1:raise RuntimeError('Expected exactly one owned launcher child: '+repr(candidates))
            # Allow the loader's own initialization to settle before attaching.
            # This delay alone is not proof that its injected initialization completed.
            time.sleep(1)
            child=candidates[0];handle=k.OpenProcess(0x1fffff,False,child);checked(handle);owned[child]=handle
            name=C.create_unicode_buffer(32768);length=D(len(name));checked(k.QueryFullProcessImageNameW(handle,0,name,C.byref(length)))
            if Path(name.value).resolve()!=binary or hashlib.sha256(Path(name.value).read_bytes()).hexdigest()!=IDENTITY:raise RuntimeError('Owned child identity mismatch')
            snap=k.CreateToolhelp32Snapshot(4,0)
            if snap==C.c_void_p(-1).value:raise C.WinError(C.get_last_error())
            tids=[]
            try:
                item=THREAD_ENTRY();item.size=C.sizeof(item);ok=k.Thread32First(snap,C.byref(item))
                while ok:
                    if item.pid==child:tids.append(int(item.tid))
                    ok=k.Thread32Next(snap,C.byref(item))
            finally:k.CloseHandle(snap)
            if len(tids)!=1:raise RuntimeError('Ambiguous initial target thread set: '+repr(tids))
            checked(k.DebugActiveProcess(child));target_pid=child;target_handle=handle
            thread=k.OpenThread(0x1fffff,False,tids[0]);checked(thread)
            try:previous=int(k.ResumeThread(thread))
            finally:k.CloseHandle(thread)
            events.append({'event':'owned_suspended_attach','pid':child,'parent_pid':int(pi.dwProcessId),'primary_tid':tids[0],'previous_suspend_count':previous,'image_name':name.value})
            if previous not in [1,2]:raise RuntimeError('Unexpected initial suspend count: '+str(previous))
        while time.monotonic()-started<a.seconds and len(events)<event_limit:
            event=DEBUG_EVENT()
            if not k.WaitForDebugEvent(C.byref(event),200):
                if a.probe_document and sender is None and form_pointer and int(form_pointer,16)>0:
                    sender=subprocess.Popen([str(a.sender_executable),str(target_pid),str(binary),str(a.probe_document),str(out),'instrumented-entry-v2',a.work_type],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    events.append({'event':'owned_file_drop_sender','pid':sender.pid,'target_pid':int(target_pid),'elapsed_ms':round((time.monotonic()-started)*1000)})
                if sender and sender.poll() is not None:
                    sender_status=sender.returncode;stop_reason='drop_sender_finished';break
                continue
            status=0x00010002;entry={'event':int(event.code),'pid':int(event.pid),'tid':int(event.tid),'elapsed_ms':round((time.monotonic()-started)*1000)}
            if event.code==3:
                if int(event.pid) not in owned:
                    retained=k.OpenProcess(0x1fffff,False,event.pid);checked(retained);owned[int(event.pid)]=retained
                if a.russian:
                    name=C.create_unicode_buffer(32768);length=D(len(name));checked(k.QueryFullProcessImageNameW(event.u.create.process,0,name,C.byref(length)))
                    entry['image_name']=name.value
                    if Path(name.value).resolve()==binary:
                        target_pid=event.pid;target_handle=event.u.create.process
            if int(event.pid) not in owned:raise RuntimeError('Unexpected non-owned process debug event')
            if event.pid!=target_pid:
                if event.code==3 and event.u.create.file:k.CloseHandle(event.u.create.file)
                if event.code==6 and event.u.load.file:k.CloseHandle(event.u.load.file)
                if event.code==1:
                    entry['exception_code']=hex(event.u.exception.record.code)
                    entry['first_chance']=bool(event.u.exception.first_chance)
                    if event.u.exception.record.code not in [0x80000003,0x4000001f]:status=0x80010001
                if event.code==5:entry['exit_code']=int.from_bytes(bytes(event.u.raw[:4]),'little')
                events.append(entry);checked(k.ContinueDebugEvent(event.pid,event.tid,status))
                if event.code==5 and event.pid==pi.dwProcessId and target_pid is None:
                    exited=True;stop_reason='launcher_exit_without_observed_target';break
                continue
            try:
                if event.code==3:
                    base=int(event.u.create.base);entry['image_base']=hex(base)
                    for va,label in [(0x00572a38,'parameter_reader'),(0x0044a748,'work_name_check'),(0x00449eec,'token_matcher'),(0x0042d890,'startup_bucket_candidate')]:
                        addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                    if a.trace_codepage:
                        addr=base+0x2bf90c;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,'MultiByteToWideChar_thunk')
                    if a.probe_document:
                        for va,label in [(0x00481794,'single_file_drop_handler'),(0x0047a528,'file_check_entry'),(0x0043dd1c,'docx_load'),(0x0046ba90,'pdf_load'),(0x00451e54,'structure_volume_check'),(0x00452ac5,'volume_selected_threshold'),(0x00452b94,'volume_decision'),(0x00452bb3,'volume_insufficient_emit')]:
                            addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                        if pixel_trace:
                            for va,label in [(0x0042ae4b,'docx_image_dimensions'),(0x0042ae4e,'docx_image_area_compare'),(0x0042ae56,'docx_large_image_flag'),(0x0042ae5c,'docx_image_flag_result'),(0x00472be7,'pdf_image_area_compare'),(0x00472bef,'pdf_large_image_emit'),(0x0047c709,'image_counter_report_gate'),(0x0047c795,'pixel_literal_conversion'),(0x0047c79a,'pixel_literal_return')]:
                                addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                        if image_bytes_trace:
                            for va,label in [(0x00438dd3,'image_bytes_zip_lookup'),(0x0044405a,'image_bytes_zip_header_read'),(0x00438dd8,'image_bytes_compare'),(0x00438ddf,'image_bytes_emit'),(0x0047c5e7,'image_bytes_report_gate')]:
                                addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                        if drawing_trace:
                            for va,label in [(0x00438a32,'shape_bounds_compare'),(0x00438a99,'shape_bounds_emit')]:
                                addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                        if a.font_trace:
                            for va,label in [(0x0040992a,'font_run_state'),(0x00409ad7,'font_small_add'),(0x00409afc,'font_tiny_add'),(0x00409b61,'font_large_add'),(0x0047b5e3,'font_small_report_gate'),(0x0047b7cd,'font_large_report_gate'),(0x0047b5ed,'font_small_report_emit'),(0x0047b7d7,'font_large_report_emit')]:
                                addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                        if a.paragraph_trace:
                            addr=base+0x3318;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,'paragraph_bucket_add')
                            for va,label in [(0x00437abd,'paragraph_activation_count'),(0x00437ae2,'paragraph_activation_gate')]:
                                addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                            for va,label in [(0x00437b69,'paragraph_properties'),(0x00437b7a,'paragraph_left_compare'),(0x00437bd0,'paragraph_left_add'),(0x00437bf6,'paragraph_right_compare'),(0x00437c4c,'paragraph_right_add'),(0x00437c8e,'paragraph_line_compare'),(0x00437cf7,'paragraph_line_add')]:
                                addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                            for va,label in [(0x0047eac2,'paragraph_left_report_gate'),(0x0047ebde,'paragraph_right_report_gate'),(0x0047ecfa,'paragraph_line_report_gate'),(0x0047ee16,'paragraph_first_report_gate'),(0x0047eacf,'paragraph_left_report_emit'),(0x0047ebeb,'paragraph_right_report_emit'),(0x0047ed07,'paragraph_line_report_emit'),(0x0047ee23,'paragraph_first_report_emit')]:
                                addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                        if a.scale_trace:
                            for va,label in [(0x00409bc6,'scale_small_add'),(0x00409bf7,'scale_tiny_add'),(0x00409cf9,'scale_large_add'),(0x0047bacd,'scale_small_report_gate'),(0x0047bbe6,'scale_large_report_gate'),(0x0047bad7,'scale_small_report_emit'),(0x0047bbf2,'scale_large_report_emit')]:
                                addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                        if drawing_trace:
                            for va,label in [(0x0047c8fe,'drawing_report_state'),(0x0047c939,'floating_image_emit'),(0x0047d051,'small_labels_report_gate'),(0x0047d05e,'small_labels_emit'),(0x0041d672,'small_label_geometry'),(0x00438805,'drawing_area_geometry'),(0x0041d581,'textbox_overflow_emit'),(0x0041d693,'textbox_small_width_emit'),(0x0041d7a6,'textbox_small_height_emit'),(0x0041d665,'textbox_exclusion_flag'),(0x0041d799,'textbox_autofit_flag'),(0x0041d537,'textbox_bounds_compare')]:
                                addr=base+va-0x400000;original=read(addr,1);write(addr,b'\xcc');breakpoints[addr]=(original,label)
                    if event.u.create.file:k.CloseHandle(event.u.create.file)
                elif event.code==6:
                    if event.u.load.file:k.CloseHandle(event.u.load.file)
                elif event.code==1:
                    ex=event.u.exception;addr=int(ex.record.address or 0);entry.update(exception_code=hex(ex.record.code),address=hex(addr),first_chance=bool(ex.first_chance))
                    if ex.record.code in [0x80000003,0x4000001f] and addr in breakpoints:
                        thread=k.OpenThread(0x1fffff,False,event.tid);checked(thread)
                        try:
                            context=WOW64_CONTEXT();context.ContextFlags=0x10007;checked(k.Wow64GetThreadContext(thread,C.byref(context)))
                            original,label=breakpoints.pop(addr);write(addr,original);context.Eip=addr;checked(k.Wow64SetThreadContext(thread,C.byref(context)))
                            if label=='MultiByteToWideChar_thunk':
                                api_calls+=1
                                if pixel_api_active:pixel_api_calls+=1
                                values=struct.unpack('<7I',read(context.Esp,28));ret,cp,flags,source,length,destination,capacity=values
                                if 0<length<=16*1024*1024:
                                    prefix=read(source,min(length,64))
                                    if length>5000 or any(key[0]==length for key in dictionary_buffers) or pixel_api_active:
                                        input_sha=hashlib.sha256(read(source,length)).hexdigest()
                                        resource_name=dictionary_buffers.get((length,input_sha))
                                        call={'call_number':api_calls,'return_address':hex(ret),'return_preferred_va':hex(ret-base+0x400000),'codepage':cp,'flags':flags,'input_length':length,'input_prefix_hex':prefix.hex(),'input_sha256':input_sha,'matched_resource':resource_name,'output_pointer':hex(destination),'output_capacity':capacity}
                                        if a.dictionary_cp1251 and resource_name and cp==0:
                                            write(context.Esp+4,struct.pack('<I',1251));call['intervention_codepage']=1251
                                        if pixel_api_active and length==len(pixel_literal) and input_sha==hashlib.sha256(pixel_literal).hexdigest():
                                            call['matched_literal']='pixel_unit_006e5f6c'
                                            if pixel_cp1251 and cp in {0,936} and ret-base+0x400000==0x5746f5:write(context.Esp+4,struct.pack('<I',1251));call['intervention_codepage']=1251
                                        codepage_calls.append(call)
                                if api_calls<1000 or (pixel_api_active and pixel_api_calls<4):
                                    pending_steps[int(event.tid)]=(addr,original,label)
                                    context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)))
                            hit={'label':label,'address':hex(addr),'registers':{n:hex(getattr(context,n)) for n in ['Eip','Esp','Eax','Edx','Ecx']},'stack_dwords':list(struct.unpack('<4I',read(context.Esp,16))),'one_shot':label!='MultiByteToWideChar_thunk'};hits.append(hit);entry['hit']=label
                            if label=='drawing_report_state':hit['drawing_state']={'count_slot_26':signed(context.Ecx+0x98),'count_slot_27':signed(context.Ecx+0x9c),'count_slot_28':signed(context.Ecx+0xa0),'count_slot_29':signed(context.Ecx+0xa4),'count_slot_30':signed(context.Ecx+0xc0),'count_slot_32':signed(context.Ecx+0xc8),'floating_area_float':struct.unpack('<f',read(context.Ecx+0x1cc,4))[0],'small_label_count':signed(context.Ecx+0xb8),'overflow_label_count':signed(context.Ecx+0xbc)}
                            if label=='drawing_report_state':hit['drawing_state']['shape_bounds_count']=signed(context.Ecx+0xa8)
                            if label.startswith('font_'):
                                if 'report_' in label:hit['font_report_state']={'small_count':signed(context.Ecx+0x2c),'tiny_count':signed(context.Ecx+0x30),'large_count':signed(context.Ecx+0x34)}
                                else:
                                    parser=unsigned(context.Ebp-0x34);style=unsigned(context.Ebp-0x3c);text_object=unsigned(context.Ebp-0x38)
                                    hit['font_state']={'size_half_points':signed(style+0x94),'vertical_align_flag':read(style+0xac,1)[0],'enabled_flag':read(parser+0x11d,1)[0],'table_gate_c8':signed(parser+0xc8),'textbox_gate_f0':signed(parser+0xf0),'textbox_count_110':signed(parser+0x110),'small_count_before':signed(parser+0x184),'tiny_count_before':signed(parser+0x188),'large_count_before':signed(parser+0x18c),'text':unicode_object(text_object) if unsigned(text_object) else {'length':0,'prefix':''}}
                                    hit['font_state']['role_gate_120']=signed(parser+0x120)
                                    hit['font_state']['scale_pct']=signed(style+0xa0)
                                pixel_hit_counts[label]=pixel_hit_counts.get(label,0)+1
                                if 'report_' not in label and pixel_hit_counts[label]<256:
                                    pending_steps[int(event.tid)]=(addr,original,label);context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)));hit['one_shot']=False
                            if label.startswith('scale_'):
                                if 'report_' in label:
                                    state=unsigned(context.Ebp-0x5dc)
                                    hit['scale_report_state']={name:signed(state+offset) for name,offset in [('small_count',0x40),('tiny_count',0x44),('large_count',0x48)]}
                                else:
                                    parser=unsigned(context.Ebp-0x34);style=unsigned(context.Ebp-0x3c);text_object=unsigned(context.Ebp-0x38)
                                    hit['scale_state']={'scale_pct':signed(style+0xa0),'enabled_flag':read(parser+0x11d,1)[0],'role_gate_ac':read(style+0xac,1)[0],'textbox_gate_f0':signed(parser+0xf0),'textbox_count_110':signed(parser+0x110),'text':unicode_object(text_object) if unsigned(text_object) else {'length':0,'prefix':''}}
                                    pixel_hit_counts[label]=pixel_hit_counts.get(label,0)+1
                                    if pixel_hit_counts[label]<256:
                                        pending_steps[int(event.tid)]=(addr,original,label);context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)));hit['one_shot']=False
                            if label.startswith('paragraph_'):
                                if label=='paragraph_bucket_add':
                                    hit['paragraph_bucket_state']={'index':context.Edx,'parser':hex(context.Eax),'return_preferred_va':hex(unsigned(context.Esp)-base+0x400000),'text':unicode_object(context.Ecx) if unsigned(context.Ecx) else {'length':0,'prefix':''}}
                                    pixel_hit_counts[label]=pixel_hit_counts.get(label,0)+1
                                    if pixel_hit_counts[label]<256:
                                        pending_steps[int(event.tid)]=(addr,original,label);context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)));hit['one_shot']=False
                                elif 'report_' in label:
                                    state=unsigned(context.Ebp-0x5dc)
                                    hit['paragraph_report_state']={name:signed(state+offset) for name,offset in [('left',0x138),('right',0x13c),('line',0x140),('first',0x144)]}
                                else:
                                    parser=unsigned(context.Ebp-0x88);style=unsigned(context.Ebp-0x90)
                                    hit['paragraph_property_state']={name:struct.unpack('<f',read(style+offset,4))[0] for name,offset in [('left',0x10),('right',8),('first',0x1c),('line',0x20)]}
                                    hit['paragraph_property_state'].update({'enabled_11d':read(parser+0x11d,1)[0],'parser':hex(parser),'style':hex(style),'prior_text':unicode_object(context.Ebp-0x1c) if unsigned(context.Ebp-0x1c) else {'length':0,'prefix':''},'rounded_line_candidate':signed(context.Ebp-0xb8) if label=='paragraph_line_compare' else None})
                                    if label.startswith('paragraph_activation_'):
                                        text_object=unsigned(context.Ebp-0x8c)
                                        hit['paragraph_property_state']['input_text']=unicode_object(text_object) if text_object and unsigned(text_object) else {'length':0,'prefix':''}
                                        if label=='paragraph_activation_count':hit['paragraph_property_state']['native_paragraph_count']=context.Eax
                                    pixel_hit_counts[label]=pixel_hit_counts.get(label,0)+1
                                    if pixel_hit_counts[label]<128:
                                        pending_steps[int(event.tid)]=(addr,original,label);context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)));hit['one_shot']=False
                            if label.startswith('shape_bounds_'):
                                state=unsigned(context.Ebp-0x74);hit['shape_bounds_state']={name:struct.unpack('<f',read(state+offset,4))[0] for name,offset in [('width',0x120),('height',0x124),('inset_138',0x138),('inset_13c',0x13c),('inset_140',0x140),('inset_144',0x144),('rotation',0x148)]}
                                hit['shape_bounds_state'].update({name:struct.unpack('<f',read(context.Ebp-offset,4))[0] for name,offset in [('selected_width',0xa0),('selected_height',0xa4),('width_base',0x90),('height_base',0x94)]})
                                pixel_hit_counts[label]=pixel_hit_counts.get(label,0)+1
                                if pixel_hit_counts[label]<128:
                                    pending_steps[int(event.tid)]=(addr,original,label);context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)));hit['one_shot']=False
                            if label.startswith('textbox_'):
                                state=unsigned(context.Ebp-0xbc);hit['textbox_branch_state']={'width_mm':struct.unpack('<f',read(state+0x100,4))[0],'height_mm':struct.unpack('<f',read(state+0x104,4))[0],'small_count_before':signed(state+0x210),'overflow_count_before':signed(state+0x214)}
                                if label in ['textbox_exclusion_flag','textbox_autofit_flag']:hit['textbox_flags']={'fc':read(context.Eax+0xfc,1)[0],'fe':read(context.Eax+0xfe,1)[0]}
                                if label=='textbox_bounds_compare':hit['textbox_bounds']={'width_base':struct.unpack('<f',read(context.Ebp-0xcc,4))[0],'height_base':struct.unpack('<f',read(context.Ebp-0xd0,4))[0],'width_addend':5.0,'height_subtrahend':5.0,'width_comparison':'strict_greater','height_comparison':'strict_greater'}
                                pixel_hit_counts[label]=pixel_hit_counts.get(label,0)+1
                                if pixel_hit_counts[label]<128:
                                    pending_steps[int(event.tid)]=(addr,original,label);context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)));hit['one_shot']=False
                            if label=='small_labels_report_gate':hit['small_label_count']=signed(context.Ecx+0xb8)
                            if label in ['small_label_geometry','drawing_area_geometry']:
                                if label=='small_label_geometry':
                                    state=unsigned(context.Ebp-0xbc);hit['label_geometry']={'width_candidate':struct.unpack('<f',read(state+0x100,4))[0],'height_candidate':struct.unpack('<f',read(state+0x104,4))[0],'counter_before':signed(state+0x210)}
                                else:hit['area_geometry']={'width_mm_candidate':struct.unpack('<f',read(context.Eax+0x38,4))[0],'height_mm_candidate':struct.unpack('<f',read(context.Eax+0x3c,4))[0],'native_type':signed(context.Ebp-0x78)}
                                pixel_hit_counts[label]=pixel_hit_counts.get(label,0)+1
                                if pixel_hit_counts[label]<128:
                                    pending_steps[int(event.tid)]=(addr,original,label);context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)));hit['one_shot']=False
                            if label.startswith('image_bytes_'):
                                if label=='image_bytes_zip_lookup':hit['zip_entry_path']=unicode_object(context.Edx)
                                if label=='image_bytes_zip_header_read':
                                    header=read(context.Ecx,30);hit['zip_local_header']={'hex':header.hex(),'signature':hex(int.from_bytes(header[:4],'little')),'flags':int.from_bytes(header[6:8],'little'),'compressed_size':int.from_bytes(header[18:22],'little'),'uncompressed_size':int.from_bytes(header[22:26],'little')}
                                if label=='image_bytes_compare':hit['image_bytes_state']={'size_unsigned32':int(context.Eax),'threshold_bytes':30000000,'comparison':'unsigned_strict_greater'}
                                if label=='image_bytes_report_gate':hit['image_bytes_counter']=signed(context.Ecx+0x90)
                                pixel_hit_counts[label]=pixel_hit_counts.get(label,0)+1
                                if label!='image_bytes_report_gate' and pixel_hit_counts[label]<128:
                                    pending_steps[int(event.tid)]=(addr,original,label);context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)));hit['one_shot']=False
                            if label=='image_counter_report_gate':hit['pixel_counter_state']={'state_pointer':hex(context.Ecx),'slot_offset':'0x94','count':signed(context.Ecx+0x94)}
                            if label in ['docx_image_dimensions','docx_image_area_compare','docx_large_image_flag','docx_image_flag_result','pdf_image_area_compare','pdf_large_image_emit']:
                                pixel_hit_counts[label]=pixel_hit_counts.get(label,0)+1
                                if label=='docx_image_dimensions':pixel_dimensions[int(event.tid)]=(C.c_int32(context.Ebx).value,C.c_int32(context.Eax).value)
                                if label=='docx_image_area_compare':
                                    width,height=pixel_dimensions[int(event.tid)];hit['pixel_state']={'getter24_value':width,'getter30_value':height,'width_px':height,'height_px':width,'area_signed32':C.c_int32(context.Ebx).value,'threshold':16000000}
                                if label=='docx_image_flag_result':hit['pixel_output_flag']=read(unsigned(context.Ebp+8),1)[0]
                                if label=='pdf_image_area_compare':hit['pixel_state']={'dimension_1bc':signed(context.Edx+0x1bc),'dimension_1c0':signed(context.Edx+0x1c0),'area_signed32':C.c_int32(context.Ecx).value,'threshold':16000000}
                                if pixel_hit_counts[label]<64:
                                    pending_steps[int(event.tid)]=(addr,original,label);context.EFlags|=0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)));hit['one_shot']=False
                            if label=='pixel_literal_conversion':
                                literal_bytes=read(context.Edx,len(pixel_literal))
                                if literal_bytes!=pixel_literal:raise ValueError('Actual pixel literal differs from static input')
                                hit['literal_hex']=literal_bytes.hex();pixel_output_object=context.Eax;pixel_api_active=True;pixel_api_calls=0
                                thunk=base+0x2bf90c
                                if thunk not in breakpoints:
                                    thunk_byte=read(thunk,1);write(thunk,b'\xcc');breakpoints[thunk]=(thunk_byte,'MultiByteToWideChar_thunk')
                            if label=='pixel_literal_return':
                                hit['converted_literal']=unicode_object(pixel_output_object);pixel_api_active=False
                                thunk=base+0x2bf90c
                                if thunk in breakpoints:
                                    thunk_byte,_=breakpoints.pop(thunk);write(thunk,thunk_byte)
                            if label=='file_check_entry':
                                ret=hit['stack_dwords'][0]
                                if ret not in breakpoints:
                                    retbyte=read(ret,1);write(ret,b'\xcc');breakpoints[ret]=(retbyte,'file_check_return')
                            if label=='single_file_drop_handler' and a.direct_file_entry:
                                utf16=str(a.probe_document).encode('utf-16le');length=len(utf16)//2
                                static_string=struct.pack('<HHiI',1200,2,-1,length)+utf16+b'\0\0'
                                object_offset=(len(static_string)+3)&~3
                                allocation=k.VirtualAllocEx(target_handle,None,object_offset+4,0x3000,4);checked(allocation)
                                write(allocation,static_string);write(allocation+object_offset,struct.pack('<I',allocation+12))
                                context.Eip=base+0x7a528;context.Edx=allocation+object_offset
                                checked(k.Wow64SetThreadContext(thread,C.byref(context)))
                                hit['direct_entry_intervention']={'function_preferred_va':'0047a528','eax_form':hex(context.Eax),'edx_unicode_string_object':hex(context.Edx),'unicode_string_data':hex(allocation+12),'utf16_units':length,'header_hex':static_string[:12].hex(),'stack_return_preserved':True,'scope':'Owned main thread: replace drop-handler entry with the shared native file-processing entry; no disk patch'}
                            if label in ['startup_bucket_candidate','file_check_entry','docx_load','pdf_load']:
                                try:
                                    pointer=int.from_bytes(read(context.Edx,4),'little');length=int.from_bytes(read(pointer-4,4),'little',signed=True)
                                    hit['candidate_input_string_length']=length
                                    if 0<length<1000000:hit['candidate_input_utf16_prefix']=read(pointer,min(length,256)*2).decode('utf-16le',errors='replace')
                                except OSError as exc:hit['candidate_input_read_error']=str(exc)
                            if label in ['volume_selected_threshold','volume_decision','volume_insufficient_emit']:
                                state=unsigned(context.Ebp-0xb4);root=unsigned(state)
                                hit['volume_state']={'state_pointer':hex(state),'work_code':unicode_object(state+0x80),'minimum':signed(context.Ebp-0xdc),'divisor':signed(context.Ebp-0xd8),'toc_page_candidate':signed(state+0xe0),'text_units_candidate':signed(state+0xe4),'supplement_candidate':signed(root+0x1b0),'candidate_after_sentinel':signed(context.Ebp-0xe0) if label!='volume_selected_threshold' else None}
                            if label=='token_matcher':
                                try:hit['string_arguments']={'Eax':unicode_object(context.Eax),'Edx':unicode_object(context.Edx)}
                                except (OSError,ValueError) as exc:hit['string_argument_read_error']=str(exc)
                        finally:k.CloseHandle(thread)
                    elif ex.record.code in [0x80000004,0x4000001e] and int(event.tid) in pending_steps:
                        bp,original,label=pending_steps.pop(int(event.tid));write(bp,b'\xcc');breakpoints[bp]=(original,label)
                        thread=k.OpenThread(0x1fffff,False,event.tid);checked(thread)
                        try:
                            context=WOW64_CONTEXT();context.ContextFlags=0x10007;checked(k.Wow64GetThreadContext(thread,C.byref(context)));context.EFlags&=~0x100;checked(k.Wow64SetThreadContext(thread,C.byref(context)))
                        finally:k.CloseHandle(thread)
                        entry['single_step_rearmed']=label
                    elif ex.record.code not in [0x80000003,0x4000001f]:
                        status=0x80010001
                        if ex.record.code==0xc0000005:
                            fault_count+=1
                            if fault_count==1:
                                thread=k.OpenThread(0x1fffff,False,event.tid);checked(thread)
                                try:
                                    context=WOW64_CONTEXT();context.ContextFlags=0x10007;checked(k.Wow64GetThreadContext(thread,C.byref(context)))
                                    entry['registers']={n:hex(getattr(context,n)) for n in ['Eip','Esp','Ebp','Eax','Ebx','Ecx','Edx','Esi','Edi']}
                                    entry['access_information']=[hex(ex.record.information[i]) for i in range(min(ex.record.parameter_count,15))]
                                    entry['instruction_bytes']=read(context.Eip,24).hex()
                                    entry['preferred_va']=hex(context.Eip-base+0x400000)
                                    if addr!=context.Eip:
                                        entry['register_scope']='WOW64 context does not match fault address; not the faulting architecture context'
                                        entry['preferred_va']=None
                                    if entry['preferred_va']=='0x42db4a':
                                        entry['bucket_index']=context.Ecx
                                        entry['inferred_first_utf16_unit']=hex(context.Ecx+0x430)
                                        entry['locals_hex']=read(context.Ebp-0x80,128).hex()
                                        try:
                                            data=read(context.Edx,128)
                                            entry['candidate_item_utf16_prefix']=data.decode('utf-16le',errors='replace').split('\0',1)[0]
                                            entry['candidate_item_bytes']=data.hex()
                                        except OSError as exc:entry['candidate_item_read_error']=str(exc)
                                finally:k.CloseHandle(thread)
                elif event.code==5:exited=True;entry['exit_code']=int.from_bytes(bytes(event.u.raw[:4]),'little')
                if base:
                    try:form_pointer=hex(int.from_bytes(read(base+0x338e1c,4),'little'))
                    except OSError:pass
                events.append(entry)
            finally:checked(k.ContinueDebugEvent(event.pid,event.tid,status))
            if exited:stop_reason='process_exit';break
            if fault_count>=8:stop_reason='repeated_access_violation_limit';break
        if len(events)>=event_limit:stop_reason='event_limit'
    except Exception as e:error=repr(e)
    finally:
        for handle in set(owned.values()):
            try:
                if k.WaitForSingleObject(handle,0)!=0:checked(k.TerminateProcess(handle,0xdead))
                # A debuggee cannot finish termination until its pending debug
                # events are continued. Drain only this owned debugging session.
                deadline=time.monotonic()+2
                while k.WaitForSingleObject(handle,0)!=0 and time.monotonic()<deadline:
                    cleanup_event=DEBUG_EVENT()
                    if k.WaitForDebugEvent(C.byref(cleanup_event),100):
                        if cleanup_event.code==6 and cleanup_event.u.load.file:k.CloseHandle(cleanup_event.u.load.file)
                        events.append({'event':'cleanup_debug_event','code':int(cleanup_event.code),'pid':int(cleanup_event.pid)})
                        checked(k.ContinueDebugEvent(cleanup_event.pid,cleanup_event.tid,0x10002))
                if k.WaitForSingleObject(handle,0)!=0:raise OSError('Owned process did not signal exit after cleanup')
            except OSError as exc:cleanup_errors.append(str(exc))
        for handle in set(owned.values()):
            if handle!=pi.hProcess:
                try:k.CloseHandle(handle)
                except OSError as exc:cleanup_errors.append(str(exc))
        if not exited:k.WaitForSingleObject(pi.hProcess,2000)
        k.CloseHandle(pi.hThread);k.CloseHandle(pi.hProcess)
        if sender:
            if sender.poll() is None:sender.terminate()
            try:
                sender_stdout,sender_stderr=sender.communicate(timeout=2);sender_status=sender.returncode
                (out/'sender-stdout.log').write_bytes(sender_stdout);(out/'sender-stderr.log').write_bytes(sender_stderr)
            except subprocess.TimeoutExpired:sender.kill();sender.communicate()
    result={'target_sha256':IDENTITY,'argument':a.argument,'owned_pid':int(pi.dwProcessId),'debug_event_size':C.sizeof(DEBUG_EVENT),'wow64_context_size':C.sizeof(WOW64_CONTEXT),'events':events,'breakpoint_hits':hits,'last_main_form_pointer':form_pointer,'exited_before_timeout':exited,'error':error,'binary_unchanged':binary.read_bytes()==raw,'limits':'Actual owned Windows process execution; one-shot observed entries only, not full call counts. No UI input or forced business-function invocation. Absence of a hit is bounded to this startup/argument run; Chinese-locale initialization may differ from Russian execution.'}
    result['stop_reason']=stop_reason
    result['locale_mode']='ru-RU LoaderWrapper (no registry redirection)' if a.russian else 'system'
    result['target_pid']=int(target_pid) if target_pid else None
    result['owned_pids']=list(owned)
    result['cleanup_errors']=cleanup_errors
    result['cleanup_verified']=not cleanup_errors
    if a.probe_document:result['limits']='Actual owned Windows process execution with hash-matched resource codepage and explicit shared file-entry redirection. Bounded entry/branch observations, image points limited to64 hits each, not full call counts. Raw report retained; this is instrumented native reference evidence, not an unmodified run or independent replica.'
    result['codepage_api_calls_observed']=api_calls
    result['large_buffer_codepage_calls']=codepage_calls
    if pixel_cp1251:result['pixel_literal_intervention_scope']='Exact CP1251 pixel-unit input hash and native conversion call; only CP_ACP/936 argument becomes1251, no report rewriting'
    result['pixel_trace']={'enabled':pixel_trace,'literal_cp1251_intervention':pixel_cp1251,'hit_counts':pixel_hit_counts}
    result['intervention_mode']='Hash-matched dictionary conversion calls only: CP_ACP to CP1251 in owned process stack; no disk patch' if a.dictionary_cp1251 else 'none'
    if a.probe_document:
        result['probe_document']={'path':str(a.probe_document),'requested_work_type':a.work_type,'file_type':a.probe_document.suffix.lower()[1:],'sha256':hashlib.sha256(probe_raw).hexdigest(),'unchanged':a.probe_document.read_bytes()==probe_raw,'sender_exit_code':sender_status,'sender_source_sha256':hashlib.sha256((Path(__file__).parent/'SendOwnedDrop.cs').read_bytes()).hexdigest()}
        length_path=out/'collection-length.txt'
        if length_path.exists():
            expected,actual=map(int,length_path.read_text().splitlines())
            result['probe_document'].update(report_utf16_units_expected=expected,report_utf16_units_collected=actual)
    if a.russian:result['limits']='Own helper and observed descendants only. LoaderWrapper uses process-local Russian settings, no registry redirection. Target creation is not proof of successful initialization; no checking interface or business predicate established by this run.'
    result['tracer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (out/'trace.json').write_text(json.dumps(result,indent=2),encoding='utf-8');summary={k:result[k] for k in ['owned_pid','debug_event_size','wow64_context_size','last_main_form_pointer','exited_before_timeout','error','binary_unchanged','stop_reason']};summary['business_breakpoint_labels']=[h['label'] for h in hits if h['label']!='MultiByteToWideChar_thunk'];summary['volume_states']=[h['volume_state'] for h in hits if h['label']=='volume_decision'];summary['codepage_api_calls']=api_calls;summary['interventions']=sum('intervention_codepage' in c for c in codepage_calls);print(json.dumps(summary))
if __name__=='__main__':main()

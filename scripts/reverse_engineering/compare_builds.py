"""Compare explicit PE releases without executing or claiming semantic rule equivalence."""
import argparse,hashlib,json
from pathlib import Path
import pefile

def digest(raw):return hashlib.sha256(raw).hexdigest()
def identify(path):
    raw=Path(path).read_bytes();pe=pefile.PE(data=raw);version=pe.VS_FIXEDFILEINFO[0]
    resources={}
    def walk(node,names):
        for e in node.entries:
            key=str(e.name) if e.name is not None else str(e.id)
            if hasattr(e,'directory'):walk(e.directory,names+[key])
            else:resources['/'.join(names+[key])]=digest(pe.get_data(e.data.struct.OffsetToData,e.data.struct.Size))
    walk(pe.DIRECTORY_ENTRY_RESOURCE,[])
    return {'sha256':digest(raw),'bytes':len(raw),'file_version':'.'.join(str(x) for x in [version.FileVersionMS>>16,version.FileVersionMS&65535,version.FileVersionLS>>16,version.FileVersionLS&65535]),'sections':[{'name':s.Name.rstrip(b'\0').decode(),'rva':s.VirtualAddress,'raw_offset':s.PointerToRawData,'raw_bytes':s.SizeOfRawData,'sha256':digest(s.get_data())} for s in pe.sections],'resource_hashes':resources}
def main():
    p=argparse.ArgumentParser();p.add_argument('old');p.add_argument('new');p.add_argument('--out',required=True);a=p.parse_args();old=identify(a.old);new=identify(a.new)
    result={'old':old,'new':new,'section_comparison':[{'name':s['name'],'byte_identical':any(x['name']==s['name'] and x['sha256']==s['sha256'] for x in old['sections'])} for s in new['sections']],'resource_changes':[k for k in sorted(set(old['resource_hashes'])|set(new['resource_hashes'])) if old['resource_hashes'].get(k)!=new['resource_hashes'].get(k)],'limits':'Static file, section and resource identity only. Not decompiled source or changed-rule semantics; runtime proof must bind the executable hash.'}
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'old_version':old['file_version'],'new_version':new['file_version'],'resource_changes':result['resource_changes']}))
if __name__=='__main__':main()

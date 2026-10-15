"""Compare retained native text with local candidates, without changing rule validation."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATTERNS={
'Word.FontSizeTooSmall':r'размер которых меньше 8',
'Word.FontSizeTooLarge':r'размер которых больше 18',
'Word.TextColorNotBlack':r'цвет которых отличается от черного',
'Word.PageSizeNotA4':r'формат.*(?:не соответствует|отличается).*А4|размер.*страниц.*А4',
'Pic.PixelSizeTooLarge':r'изображени.*(?:16000000|16 000 000)',
}
def compare(local,capture):
    if capture.get('status')!='captured':return {'status':'pending_native_capture','reason':capture.get('reason','No retained native result')}
    for key,value in [('input_sha256',local['source_sha256']),('work_type',local['work_type'])]:
        if capture.get(key)!=value:raise ValueError('Native/local identity mismatch: '+key)
    if capture.get('build')!=230:raise ValueError('Unrecognized native build')
    text_path=Path(capture['text_path']);raw=text_path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=capture.get('text_sha256'):raise ValueError('Native capture hash mismatch')
    text=raw.decode('utf-8-sig');local_ids={f['rule_id'] for f in local['findings']};pairs=[]
    for rule,pattern in PATTERNS.items():
        matches=list(re.finditer(pattern,text,re.I));native=bool(matches);present=rule in local_ids
        pairs.append({'rule_id':rule,'native_pattern_match':native,'local_candidate':present,'status':'pattern_agreement_requires_review' if native==present else 'difference_requires_review','native_character_offsets':[[m.start(),m.end()] for m in matches]})
    return {'status':'captured_partial_pattern_comparison','pairs':pairs,'unmapped_native_text_requires_review':True,'native_document_kind':'nkr' if capture['work_type']=='phd' else 'vkr','local_document_kind':local['document_kind'],'document_kind_mismatch':local['document_kind']=='dissertation','limits':'Presence patterns only, not semantic or occurrence equivalence. Review all raw native diagnostics. No accuracy or native-proof promotion.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('local_report');p.add_argument('native_capture');p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out).resolve()
    if out.is_relative_to(ROOT):raise ValueError('Private comparisons must remain outside the repository')
    result=compare(json.loads(Path(a.local_report).read_text(encoding='utf-8-sig')),json.loads(Path(a.native_capture).read_text(encoding='utf-8-sig')))
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status']}))
if __name__=='__main__':main()

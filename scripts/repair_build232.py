"""Independently gated, narrow master-DOCX font repair implementation."""
import hashlib,json,re,uuid,zipfile
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def capability():
    gate=ROOT/'evidence/v028/complex-repair/acceptance.json'
    if not gate.exists():return {'enabled':False,'reason':'Independent complex before/after acceptance pending'}
    data=json.loads(gate.read_text(encoding='utf-8'))
    if data.get('enabled') is not True:return {'enabled':False,'reason':data.get('reason','Acceptance incomplete')}
    if data.get('build')!=232 or data.get('actions')!=['font_size_anomalies']:return {'enabled':False,'reason':'Wrong acceptance scope'}
    if data.get('implementation_sha256')!=sha(Path(__file__).read_bytes()):return {'enabled':False,'reason':'Repair implementation differs from accepted candidate'}
    for name,digest in data.get('evidence_hashes',{}).items():
        p=(ROOT/name).resolve()
        if not p.is_relative_to(ROOT/'evidence') or not p.is_file() or sha(p.read_bytes())!=digest:return {'enabled':False,'reason':'Evidence missing or changed'}
    if not data.get('evidence_hashes'):return {'enabled':False,'reason':'Empty evidence ledger'}
    return {'enabled':True,'actions':['font_size_anomalies'],'work_types':['master'],'target_font_pt':14,'acceptance_sha256':sha(gate.read_bytes())}

def plan(source,actions,target,work_type,expected_hash=None,require_acceptance=True):
    if require_acceptance and not capability()['enabled']:raise ValueError('Build232 font repair acceptance incomplete')
    if actions!=['font_size_anomalies'] or work_type!='master' or target!=14:
        raise ValueError('Build232 supports explicit master font_size_anomalies to14pt only; A4/color/other modes remain closed')
    source=Path(source).resolve();raw=source.read_bytes()
    if source.suffix.lower()!='.docx':raise ValueError('Build232 repair supports DOCX only')
    if expected_hash and sha(raw)!=expected_hash:raise ValueError('Source changed since preview')
    from parsers.docx_parser import DocxParser
    parser=DocxParser(str(source));document=parser.doc
    records=parser.parse_structure_paragraphs()
    intro=next((p for p in records if p['text'].strip().lower()=='введение'),None)
    if intro is None:raise ValueError('Exact introduction anchor required; front matter must not be guessed')
    front=' '.join(p['text'] for p in records if p['index']<intro['index'])
    if re.search(r'(?:кандидата|доктора)\s+.{0,45}?наук',front.lower()):raise ValueError('Degree dissertation is not VKR master')
    if len(document.sections)!=1 or document.sections[0].page_width>document.sections[0].page_height:raise ValueError('Build232 validated for one portrait section only')
    if document.styles['Normal'].font.size is None or document.styles['Normal'].font.size.pt!=14:raise ValueError('Normal style must explicitly establish14pt body font')
    changes=[];skipped=[];position={p.get('xml_path'):p['index'] for p in records}
    protected={'fldChar','fldSimple','instrText','drawing','pict','hyperlink','sdt','ins','del','oMath','oMathPara','numPr','footnoteReference','endnoteReference','commentReference'}
    for pi,p in enumerate(document.paragraphs):
        path=p._p.getroottree().getpath(p._p)
        reason=None
        if position.get(path,-1)<=intro['index']:reason='Front matter/introduction anchor'
        elif p.style.style_id!='Normal' or len(p.text.strip())<=40:reason='Non-body style or short paragraph'
        elif any(etree.QName(n).localname in protected for n in p._p.iter()):reason='Equation/field/drawing/hyperlink/control/revision/list paragraph'
        elif re.match(r'\s*(?:рисунок|таблица|формула|\d+[.)])\b',p.text,re.I):reason='Caption or numbered content'
        if reason:skipped.append({'paragraph':pi+1,'reason':reason});continue
        for ri,r in enumerate(p.runs):
            props,_=parser.style_resolver.properties(p._p,r._r)
            size=props.find(qn('w:sz'))
            if size is None or props.find(qn('w:vertAlign')) is not None or props.find(qn('w:vanish')) is not None:continue
            actual=float(size.get(qn('w:val')))/2
            if not r.text.strip() or 8<=actual<=18:continue
            r.font.size=document.styles['Normal'].font.size
            changes.append({'paragraph':pi+1,'run':ri+1,'xml_path':r._r.getroottree().getpath(r._r),'property':'font_size_pt','before_effective':actual,'after':14,'rule_id':'Word.FontSizeTooSmall' if actual<8 else 'Word.FontSizeTooLarge'})
    result={'schema_version':2,'native_build':232,'work_type':work_type,'actions':actions,'body_font_pt':target,'input_file':str(source),'input_sha256':sha(raw),'dry_run':True,'changes':changes,'skipped':skipped,'source_unchanged':source.read_bytes()==raw,'scope':'Ordinary Normal-style main-body runs after exact introduction; all special paragraphs and other ZIP parts preserved; no full-program/school pass guarantee'}
    result['plan_id']=sha(json.dumps({k:result[k] for k in ['native_build','input_sha256','work_type','actions','body_font_pt','changes','skipped']},sort_keys=True).encode())
    return result,document

def repair(source,output_dir,actions,target,work_type,dry_run,expected_hash=None):
    result,document=plan(source,actions,target,work_type,expected_hash)
    if dry_run:return result
    source=Path(source).resolve();raw=source.read_bytes()
    if sha(raw)!=result['input_sha256']:raise ValueError('Source changed before write')
    out=Path(output_dir).resolve() if output_dir else source.parent/'thesis_repairs';out.mkdir(parents=True,exist_ok=True)
    dest=out/(source.stem+'.repaired-'+uuid.uuid4().hex[:10]+'.docx')
    with zipfile.ZipFile(source) as a,dest.open('xb') as stream,zipfile.ZipFile(stream,'w') as b:
        entries=a.infolist()
        if len(set(a.namelist()))!=len(entries):raise ValueError('Duplicate ZIP members unsupported')
        for entry in entries:b.writestr(entry,document.part.blob if entry.filename=='word/document.xml' and result['changes'] else a.read(entry.filename))
    result.update(dry_run=False,output_file=str(dest),output_sha256=sha(dest.read_bytes()),source_unchanged=source.read_bytes()==raw)
    if not result['source_unchanged']:raise ValueError('Original changed; reject output')
    from argparse import Namespace
    from check_document import check_file
    args=Namespace(work_type='master',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False)
    before=check_file(source,args);after=check_file(dest,args)
    result.update(before_rule_ids=[f['rule_id'] for f in before['findings']],after_rule_ids=[f['rule_id'] for f in after['findings']],recheck_build=232)
    log=dest.with_suffix('.changes.json');result['change_log']=str(log);log.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

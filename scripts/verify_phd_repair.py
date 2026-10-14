"""Verify a real doctoral copy repair against native before/after and XML invariants."""
import copy,hashlib,json,re,zipfile
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/multipage-phd-repair';NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    repair=json.loads((OUT/'repair-execution.json').read_text(encoding='utf-8-sig'));source=Path(repair['input_file']);dest=Path(repair['output_file']);assert repair['source_unchanged'];assert sha(source)==repair['input_sha256'];assert sha(dest)==repair['output_sha256']==sha(OUT/'phd_combined_after.docx')
    captures={}
    for name in ['phd_combined','phd_combined_after']:
        p=OUT/(name+'.original.json');data=json.loads(p.read_text(encoding='utf-8'));t=re.search(r'编辑 Value: (Файл:.*?) ID:',data['accessibility']['tree'])[1];assert '\\'+name+'.docx ' in t;captures[name]={'sha256':sha(p),'native_text':t,'diagnostics':len(re.findall(r' \d+\. ',t))}
    assert captures['phd_combined']['diagnostics']==4 and captures['phd_combined_after']['diagnostics']==0 and 'Замечаний нет.' in captures['phd_combined_after']['native_text']
    with zipfile.ZipFile(source) as a,zipfile.ZipFile(dest) as b:
        assert a.namelist()==b.namelist();changed=[n for n in a.namelist() if a.read(n)!=b.read(n)];assert changed==['word/document.xml'];x=etree.fromstring(a.read(changed[0]));y=etree.fromstring(b.read(changed[0]));assert x.xpath('//w:t/text()',namespaces=NS)==y.xpath('//w:t/text()',namespaces=NS)
        for path in ['//w:tbl','//w:drawing','//w:pgMar']:
            assert [etree.tostring(n) for n in x.xpath(path,namespaces=NS)]==[etree.tostring(n) for n in y.xpath(path,namespaces=NS)]
        undo=copy.deepcopy(y)
        for c in reversed(repair['changes']):
            if c['property']=='page_size':
                node=undo.xpath('//w:sectPr/w:pgSz',namespaces=NS)[c['section']-1];node.attrib.clear();node.attrib.update(c['before'])
            else:
                p=undo.xpath('/w:document/w:body/w:p',namespaces=NS)[c['paragraph']-1];run=p.findall('.//w:r',NS)[c['run']-1];rpr=run.find('w:rPr',NS);node=rpr.find('w:'+c['property'],NS)
                if c['before_direct_xml'] is None:rpr.remove(node)
                else:rpr.replace(node,etree.fromstring(c['before_direct_xml'].encode()))
                # Remove newly introduced empty rPr only when absent in the source.
                oldp=x.xpath('/w:document/w:body/w:p',namespaces=NS)[c['paragraph']-1];oldrun=oldp.findall('.//w:r',NS)[c['run']-1]
                if len(rpr)==0 and oldrun.find('w:rPr',NS) is None:run.remove(rpr)
        assert etree.tostring(undo,method='c14n')==etree.tostring(x,method='c14n'),'Unlogged XML change'
    rules=sorted({c['rule_id'] for c in repair['changes']});receipt={'source_sha256':sha(source),'output_sha256':sha(dest),'native_before_after':captures,'changes':len(repair['changes']),'changed_zip_parts':changed,'all_text_table_drawing_margin_parts_preserved':True,'all_xml_changes_reversible_from_log':True,'source_unchanged':True,'repaired_rules':rules,'scope':'Single portrait doctoral DOCX, ordinary body text, ordinary tables and one inline PNG; no margin or special-content repair.'}
    p=OUT/'repair-comparison.json';p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    registry_path=ROOT/'scripts/testvkr-service/rules/rules_verified.json';registry=json.loads(registry_path.read_text(encoding='utf-8'))
    for rule in registry['rules']:
        if rule['rule_id'] in rules:
            context=rule['verification_by_context']['docx:phd'];context.update(repair_evidence_ref='evidence/multipage-phd-repair/repair-comparison.json',repair_evidence_sha256=sha(p))
    registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'changes':receipt['changes'],'native_before':captures['phd_combined']['diagnostics'],'native_after':captures['phd_combined_after']['diagnostics'],'logged_xml_reversible':True}))
if __name__=='__main__':main()

"""Accept only the inspected finite font scope; no other repair action promotion."""
import argparse,hashlib,json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--accept-inspected-five-distinct-pages',action='store_true');a=p.parse_args()
    if not a.accept_inspected_five_distinct_pages:raise ValueError('Visual inspection of the five distinct rendered pages is required')
    out=ROOT/'evidence/v028/complex-repair';native=json.loads((out/'structural-native-validation.json').read_text(encoding='utf-8'))
    assert native['all_structural_and_native_checks_pass']
    rendering=json.loads((out/'rendered/render-receipt.json').read_text(encoding='utf-8'))
    assert len(rendering['cases'])==3 and all(len(r['pages'])==3 and r['source_unchanged'] for r in rendering['cases'])
    for i in [0,2]:assert len({r['pages'][i]['sha256'] for r in rendering['cases']})==1
    for record in rendering['cases']:
        pdf=out/'rendered'/record['pdf'];assert sha(pdf)==record['pdf_sha256']
        with fitz.open(pdf) as doc:
            assert len(doc)==3 and len(doc[2].get_images())==1
            for page in doc:
                for block in page.get_text('dict')['blocks']:
                    x0,y0,x1,y1=block['bbox'];assert -1<=x0<=x1<=page.rect.width+1 and -1<=y0<=y1<=page.rect.height+1
        for page in record['pages']:assert sha(out/'rendered'/page['image'])==page['sha256']
    visual={'reviewed_distinct_pages':['C01A-page1','C01A-page2','C01A-page3','C01B-page2','C02B-page2'],
            'page1_and_page3_pixel_identical_across_all_three_inputs':True,
            'visual_result':'No added clipping/overlap or missing equation/image/table observed; intended body-size change only. Deliberately tiny protected equation context remains unchanged.',
            'scope':'Finite 3-page synthetic fixtures; not a layout guarantee for arbitrary real theses'}
    (out/'visual-acceptance.json').write_text(json.dumps(visual,indent=2),encoding='utf-8')
    evidence={str(f.relative_to(ROOT)):sha(f) for f in out.rglob('*') if f.is_file() and f.name!='acceptance.json'}
    gate={'build':232,'enabled':True,'actions':['font_size_anomalies'],'work_type':'master','body_font_pt':14,
          'implementation_sha256':sha(ROOT/'scripts/repair_build232.py'),'evidence_hashes':evidence,
          'limits':'One portrait section, explicit14pt Normal style, exact introduction anchor, ordinary long main-body paragraphs only. A4/color/PDF/degree/other modes closed. Formula and special content warnings remain; no whole-program or school pass claim.'}
    with (out/'acceptance.json').open('x',encoding='utf-8') as f:json.dump(gate,f,indent=2)
    print(json.dumps({'enabled':True,'actions':gate['actions'],'hashed_evidence_files':len(evidence)}))
if __name__=='__main__':main()

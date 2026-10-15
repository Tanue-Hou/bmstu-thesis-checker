"""Register only independently audited native232 PNG detection contexts."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 audit_path=ROOT/'evidence/business-map-232/pixel-audit-r2/audit.json';audit=json.loads(audit_path.read_text(encoding='utf-8'))
 assert audit['status']=='passed_bounded_native232_pixel_predicate_and_encoding_audit' and len(audit['cases'])==6
 for name,digest in audit['sources'].items():assert sha(ROOT/name)==digest,name
 refs={audit_path.relative_to(ROOT).as_posix():sha(audit_path),**audit['sources']}
 implementations={p:sha(ROOT/p) for p in ['scripts/check_document.py','scripts/testvkr-service/checkers/pictures.py','scripts/testvkr-service/parsers/docx_parser.py','scripts/testvkr-service/parsers/pdf_parser.py']}
 contexts={}
 for kind,profile in [('docx','native232_single_inline_png'),('pdf','native232_single_page_png_pdf')]:
  cases=[r for r in audit['cases'] if r['format']==kind]
  assert [r['large_branch_observed'] for r in cases]==[False,False,True]
  contexts[kind+':phd']={'evidence_refs':list(refs),'verification_evidence_sha256':sha(audit_path),'evidence_hashes':refs,'implementation_hashes':implementations,'verified_policy':{'IMAGE_PIXEL_AREA_MAX':16000000},'scope':{'build':232,'format':kind,'work_type':'phd','profile':profile,'limits':'RGB8 PNG only, one ordinary inline DOCX image or one-page unrotated embedded-TNR PDF with one image. Strict signed32 area comparison at tested boundary; no overflow, vectors, alpha images, reused objects or repair permission.'}}
 path=ROOT/'scripts/testvkr-service/rules/rules_verified.json';data=json.loads(path.read_text(encoding='utf-8'));rule=next(r for r in data['rules'] if r['rule_id']=='Pic.PixelSizeTooLarge')
 rule.setdefault('verification_by_build',{})['232']=contexts
 rule['source_va_by_build']={'232':{'docx_image_decode':'0042a6b0','docx_area_compare':'0042ae4e','pdf_image_decode':'00472b90','pdf_area_compare':'00472be7','report_constructor':'0047a528','pixel_literal_conversion_call':'0047c795'}}
 rule['message_template']=rule['message_template'].replace('540','16000000')
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps({'rule_id':rule['rule_id'],'build':232,'contexts':list(contexts),'repair_actions_added':0}))
if __name__=='__main__':main()

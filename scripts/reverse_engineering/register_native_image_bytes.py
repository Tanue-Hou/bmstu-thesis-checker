"""Register the independently measured build232 NKR DOCX ZIP-byte predicate."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 audit_path=ROOT/'evidence/business-map-232/image-bytes-audit-r1/audit.json';audit=json.loads(audit_path.read_text(encoding='utf-8'));assert audit['status']=='passed_native232_docx_image_bytes_audit' and len(audit['cases'])==5
 for path,digest in audit['sources'].items():assert sha(ROOT/path)==digest,path
 refs={audit_path.relative_to(ROOT).as_posix():sha(audit_path),**audit['sources']};impl={p:sha(ROOT/p) for p in ['scripts/check_document.py','scripts/issue_locations.py','scripts/testvkr-service/checkers/pictures.py','scripts/testvkr-service/parsers/docx_parser.py']}
 context={'verification_status':'verified_against_original','confidence':'high','threshold_origin':'native232_unsigned_per_entry_zip_local_header_comparison','evidence_refs':list(refs),'verification_evidence_sha256':sha(audit_path),'evidence_hashes':refs,'implementation_hashes':impl,'verified_policy':{},'scope':{'build':232,'format':'docx','work_type':'phd','profile':'native232_docx_image_zip_bytes','limits':'One/two ordinary inline RGB8 PNG images; standard local ZIP headers flags0/8. Per-entry declared size, not aggregate or central-directory size. Sentinel, ZIP64, malformed headers, vectors, other modes and repair remain unverified.'}}
 p=ROOT/'scripts/testvkr-service/rules/rules_verified.json';data=json.loads(p.read_text(encoding='utf-8'));rule=next(r for r in data['rules'] if r['rule_id']=='Pic.FileSizeTooLarge');rule.setdefault('verification_by_build',{})['232']={'docx:phd':context};rule['predicate_by_build']={'232':audit['predicate']}
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'rule_id':rule['rule_id'],'new_context':'232/docx:phd','global230_status_unchanged':rule['verification_status']}))
if __name__=='__main__':main()

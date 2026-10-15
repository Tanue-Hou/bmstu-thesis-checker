"""Add independently proven native232 font contexts, preserving old evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 proof=ROOT/'evidence/business-map-232/font-audit-r1/audit.json';audit=json.loads(proof.read_text());assert audit['status']=='passed_native232_font_counter_role_and_inheritance_audit' and len(audit['cases'])==29
 for p,d in audit['sources'].items():assert sha(ROOT/p)==d,p
 refs={proof.relative_to(ROOT).as_posix():sha(proof),**audit['sources']};impl={p:sha(ROOT/p) for p in ['scripts/check_document.py','scripts/issue_locations.py','scripts/testvkr-service/checkers/word_format.py','scripts/testvkr-service/checkers/native_font_counts.py','scripts/testvkr-service/parsers/docx_parser.py','scripts/testvkr-service/parsers/style_resolver.py','scripts/testvkr-service/config.py']}
 path=ROOT/'scripts/testvkr-service/rules/rules_verified.json';data=json.loads(path.read_text(encoding='utf-8'))
 for rule_id in ['Word.FontSizeTooSmall','Word.FontSizeTooLarge']:
  rule=next(r for r in data['rules'] if r['rule_id']==rule_id);contexts={}
  for mode in ['master','phd']:
   contexts['docx:'+mode]={'verification_status':'verified_against_original','confidence':'high','threshold_origin':'native232_UTF16_counter_size_and_role_branches','verification_evidence_sha256':sha(proof),'evidence_refs':list(refs),'evidence_hashes':refs,'implementation_hashes':impl,'verified_policy':{'FONT_SIZE_MIN_PT':8.0,'FONT_SIZE_MAX_PT':18.0,'FONT_VIOLATION_MIN_CHARS':10},'scope':{'build':232,'format':'docx','work_type':mode,'profile':'native232_plain_docx_fonts','limits':'Plain resolved DOCX text, at most one single-cell table and one ungrouped absolute50x50mm VML textbox/one paragraph/two runs; no extra stories, fields, math or complex content. UTF16 including spaces, tiny bucket separate, prior-textbox count gate; no new repair permission.'}}
  rule.setdefault('verification_by_build',{})['232']=contexts
  rule.setdefault('predicate_by_build',{})['232']={'ordinary_small':'4 < pt <8','tiny_unreported_bucket':'0 < pt <=4','large':'pt >18, plus native role gates','count':'UTF16 units including whitespace >10','textbox_large_gate':'prior processed UTF16 units >100'}
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'new_contexts':4,'rule_ids':len(data['rules'])}))
if __name__=='__main__':main()

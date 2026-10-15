"""Register a source/evidence-bound native textbox dimension diagnostic."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 proof=ROOT/'evidence/business-map-232/textbox-bounds-audit-r1/audit.json';audit=json.loads(proof.read_text());assert audit['status']=='passed_native232_textbox_dimension_bounds_audit' and len(audit['cases'])==13
 for p,d in audit['sources'].items():assert sha(ROOT/p)==d,p
 refs={proof.relative_to(ROOT).as_posix():sha(proof),**audit['sources']};impl={p:sha(ROOT/p) for p in ['scripts/check_document.py','scripts/issue_locations.py','scripts/testvkr-service/checkers/pictures.py','scripts/testvkr-service/parsers/docx_parser.py','scripts/testvkr-service/parsers/drawing_geometry.py']}
 ctx={'verification_status':'verified_against_original','confidence':'high','threshold_origin':'native_dimension_compare_branch_counter_report','verification_evidence_sha256':sha(proof),'evidence_refs':list(refs),'evidence_hashes':refs,'implementation_hashes':impl,'verified_policy':{},'scope':{'build':232,'format':'docx','work_type':'phd','profile':'native232_simple_vml_bounds','limits':'Single-section A4 portrait/landscape, ordinary absolute VML textboxes, explicit mm dimensions <=300, zero offsets, plain one paragraph/run; no fit/insets/groups/rotation, general shape or repair proof.'}}
 rule={'rule_id':'Pic.LabelsOutOfBounds','threshold':0,'comparator':'>','source_va':None,'sample_trigger':[],'observed_message':None,'message_template':'** Документ содержит надписи, выходящие за границы текста:','verification_status':'pending_original_program_comparison','confidence':'low','threshold_origin':'build_specific_context_required','enabled_by_default':True,'evidence_refs':[],'verification_by_build':{'232':{'docx:phd':ctx}},'predicate_by_build':{'232':{'counter_slot':'0x2f','count_minimum_exclusive':0,'width_limit_mm':{'portrait':177,'landscape':264},'height_limit_mm':{'portrait':254,'landscape':167},'comparison':'strict_greater','precedence':'dimension overflow bypasses small-label geometry branch'}}}
 path=ROOT/'scripts/testvkr-service/rules/rules_verified.json';data=json.loads(path.read_text(encoding='utf-8'));data['rules']=[r for r in data['rules'] if r['rule_id']!=rule['rule_id']]+[rule];path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'rule_ids':len(data['rules']),'registered':rule['rule_id']}))
if __name__=='__main__':main()

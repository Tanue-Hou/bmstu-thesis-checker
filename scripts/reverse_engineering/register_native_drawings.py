"""Register four independently audited drawing families in one exact build/profile."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 audit_path=ROOT/'evidence/business-map-232/drawing-audit-r1/audit.json';audit=json.loads(audit_path.read_text(encoding='utf-8'));assert audit['status']=='passed_bounded_native232_drawing_family_audit' and len(audit['cases'])==15
 for p,digest in audit['sources'].items():assert sha(ROOT/p)==digest,p
 refs={audit_path.relative_to(ROOT).as_posix():sha(audit_path),**audit['sources']};impl={p:sha(ROOT/p) for p in ['scripts/check_document.py','scripts/issue_locations.py','scripts/testvkr-service/checkers/pictures.py','scripts/testvkr-service/parsers/docx_parser.py','scripts/testvkr-service/parsers/drawing_geometry.py']}
 textbox_path=ROOT/'evidence/business-map-232/textbox-audit-r1/audit.json'
 if textbox_path.exists():
  extra=json.loads(textbox_path.read_text(encoding='utf-8'));assert extra['status']=='passed_native232_textbox_units_fit_and_branch_audit' and len(extra['cases'])==32
  for p,digest in extra['sources'].items():assert sha(ROOT/p)==digest,p
  refs.update(extra['sources']);refs[textbox_path.relative_to(ROOT).as_posix()]=sha(textbox_path)
 path=ROOT/'scripts/testvkr-service/rules/rules_verified.json';data=json.loads(path.read_text(encoding='utf-8'))
 for rule_id in ['Pic.FloatingImages','Pic.SmallLabels','Pic.FloatingShapes','Pic.FloatingLabels']:
  rule=next((r for r in data['rules'] if r['rule_id']==rule_id),None)
  if rule is None:
   rule={'rule_id':rule_id,'verification_status':'pending_original_program_comparison','confidence':'low','enabled_by_default':True,'evidence_refs':[],'threshold_origin':'build_specific_context_required'};data['rules'].append(rule)
  profile='native232_plain_floating_png' if rule_id=='Pic.FloatingImages' else 'native232_simple_vml_labels'
  rule.setdefault('observed_message',None)
  if rule_id in {'Pic.FloatingShapes','Pic.FloatingLabels'}:
   rule.setdefault('threshold',0);rule.setdefault('comparator','>');rule.setdefault('source_va',None);rule.setdefault('sample_trigger',[])
   rule.setdefault('message_template','** Документ содержит плавающие '+('графические фигуры. Встройте фигуры в текст:' if rule_id=='Pic.FloatingShapes' else 'надписи. Встройте надписи в текст:'))
  context={'verification_status':'verified_against_original','confidence':'high','threshold_origin':'native232_geometry_counter_and_report_gate','evidence_refs':list(refs),'verification_evidence_sha256':sha(audit_path),'evidence_hashes':refs,'implementation_hashes':impl,'verified_policy':{},'scope':{'build':232,'format':'docx','work_type':'phd','profile':profile,'limits':('One/two RGB8 PNGs, matching simple extents, no crop/rotation; wrapNone area accumulated as float32 and wrapSquare contributes zero.' if rule_id=='Pic.FloatingImages' else 'Simple absolute VML textboxes, one plain paragraph/run, explicit mm dimensions <=5, no group/insets/auto-fit. General drawings, other units/types and modes unverified.')}}
  rule.setdefault('verification_by_build',{})['232']={'docx:phd':context}
  if textbox_path.exists() and rule_id!='Pic.FloatingImages':
   context['scope']['limits']='Simple absolute VML textboxes, one plain paragraph/run, native mm/cm/pt/in/unitless conversions, dimensions <=50mm; measured shape/textbox fit values and two literal inset configurations only. px/pc, groups, rotation, overflow and other modes unverified.'
   context['scope']['textbox_extension_evidence']=textbox_path.relative_to(ROOT).as_posix()
   if rule_id=='Pic.SmallLabels':context['scope']['shape_autofit_behavior']='Shape t/true makes effective height10mm; width below2mm still counts. Same textbox-layer values did not set the flag in observed inputs.'
  rule['predicate_by_build']={'232':{'Pic.FloatingImages':{'count_slots':['0x26','0x27'],'area_slot':'0x73','area_threshold_exclusive':500,'unit':'mm2','precision':'float32','wrapSquare_area_contribution':0},'Pic.SmallLabels':{'counter_slot':'0x2e','count_minimum_exclusive':10,'width_or_height_minimum_exclusive_mm':2},'Pic.FloatingShapes':{'count_slots':['0x28','0x29'],'count_minimum_exclusive':0},'Pic.FloatingLabels':{'count_slots':['0x30','0x32'],'count_minimum_exclusive':0}}[rule_id]}
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'contexts_added':4,'registered_rule_ids':len(data['rules']),'build232_contexts':sum(len(r.get('verification_by_build',{}).get('232',{})) for r in data['rules'])}))
if __name__=='__main__':main()

"""Same-input bounds predicate/counter/branch comparison."""
import argparse,hashlib,json,sys
from pathlib import Path
from argparse import Namespace
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import parse_document,check_file
from native_reference_cli import validate_native_run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);base=ROOT/'evidence/business-map-232';rows=[];sources={}
 for folder in ['textbox-bounds-native-r1','textbox-bounds-native-r2']:
  matrix=base/folder/'matrix.json';sources[matrix.relative_to(ROOT).as_posix()]=sha(matrix)
  for row in json.loads(matrix.read_text())['cases']:
   source=ROOT/row['input'];d=ROOT/row['evidence_directory'];trace=json.loads((d/'trace.json').read_text());assert sha(source)==row['sha256'];native=validate_native_run(trace,(d/'native-result.txt').read_bytes().decode('utf-8'),'phd','docx',sha(source),True)
   _,data=parse_document(source);labels=data['labels'];hits=trace['breakpoint_hits'];observed=[h for h in hits if h['label']=='textbox_bounds_compare'];assert len(observed)==len(labels)==11
   for hit,l in zip(observed,labels):
    b=hit['textbox_bounds'];assert l['native_width_limit_mm']==b['width_base']+5 and l['native_height_limit_mm']==b['height_base']-5
   count=sum(l['overflow_geometry_candidate'] for l in labels);branch_count=sum(h['label']=='textbox_overflow_emit' for h in hits);assert count==branch_count==row['drawing_state']['overflow_label_count']
   report=check_file(source,Namespace(work_type='phd',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False));found={f['rule_id'] for f in report['findings']};assert ('Pic.LabelsOutOfBounds' in found)==bool(count);assert ('Pic.SmallLabels' in found)==bool(row['small_labels_emit']);assert ('Pic.FloatingLabels' in found)==bool(row['drawing_state']['count_slot_30']+row['drawing_state']['count_slot_32']);assert 'Pic.FloatingShapes' in found
   phrase='надписи, выходящие за границы текста';assert any(phrase in diag['message'] for diag in native)==bool(count)
   rows.append({**row,'overflow_branch_hits':branch_count,'local_overflow_count':count,'first_bounds':observed[0]['textbox_bounds'],'four_families_agree':True,'native_total_diagnostics':len(native),'limits':'Other graphic-bounds diagnostics preserved but not included in this family agreement.'})
   for f in [source,*d.iterdir()]:
    if f.is_file():sources[f.relative_to(ROOT).as_posix()]=sha(f)
 assert len(rows)==13
 (out/'audit.json').write_text(json.dumps({'status':'passed_native232_textbox_dimension_bounds_audit','cases':rows,'sources':sources,'limits':['Single-section A4 portrait/landscape simple VML only; no school or rendered-layout certification.','Dimension bounds and position exclusions are separate; other graphic diagnostics are still coverage gaps.']},indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'cases':len(rows),'all_agree':True}))
if __name__=='__main__':main()

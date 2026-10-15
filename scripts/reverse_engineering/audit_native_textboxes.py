"""Audit each textbox branch/counter against the independent parser."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import parse_document,check_file
from argparse import Namespace
from native_reference_cli import validate_native_run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);base=ROOT/'evidence/business-map-232';rows=[];sources={}
 for folder in ['textbox-boundaries-r1','textbox-boundaries-r2','textbox-fit-boundaries-r1','textbox-boundaries-r3']:
  matrix=base/folder/'matrix.json';sources[matrix.relative_to(ROOT).as_posix()]=sha(matrix)
  for row in json.loads(matrix.read_text(encoding='utf-8'))['cases']:
   path=ROOT/row['input'];d=ROOT/row['evidence_directory'];assert sha(path)==row['sha256'];trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));native=validate_native_run(trace,(d/'native-result.txt').read_bytes().decode('utf-8'),'phd','docx',sha(path),True)
   _,data=parse_document(path);labels=data['labels'];hits=trace['breakpoint_hits'];geometry=[h['label_geometry'] for h in hits if h['label']=='small_label_geometry'];assert len(geometry)==len(labels)==11
   for g,label in zip(geometry,labels):assert (g['width_candidate'],g['height_candidate'])==(label['width_mm'],label['native_effective_height_mm']),(row['case'],g,label)
   expected=sum(l['small_geometry_candidate'] for l in labels);actual=row['drawing_state']['small_label_count'];assert expected==actual,(row['case'],expected,actual)
   width_hits=sum(h['label']=='textbox_small_width_emit' for h in hits);height_hits=sum(h['label']=='textbox_small_height_emit' for h in hits);assert width_hits+height_hits==actual
   report=check_file(path,Namespace(work_type='phd',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False));findings={f['rule_id'] for f in report['findings']}
   assert ('Pic.SmallLabels' in findings)==(actual>10)==row['small_labels_emit'];assert 'Pic.FloatingShapes' in findings and 'Pic.FloatingLabels' in findings
   assert row['drawing_state']['overflow_label_count']==0 and not any(h['label']=='textbox_overflow_emit' for h in hits)
   rows.append({**row,'local_small_count':expected,'geometry_hits':len(geometry),'width_branch_hits':width_hits,'height_branch_hits':height_hits,'profile_supported':data['native232_vml_label_profile_supported'],'all_three_families_agree':True,'first_geometry':geometry[0],'flags_observed':[h['textbox_flags'] for h in hits if 'textbox_flags' in h][:1]})
   for f in [path,*d.iterdir()]:
    if f.is_file():sources[f.relative_to(ROOT).as_posix()]=sha(f)
 assert len(rows)==32
 result={'status':'passed_native232_textbox_units_fit_and_branch_audit','cases':rows,'sources':sources,'limits':['32 public synthetic DOCX/NKR inputs; finite geometry/branch evidence, not school or layout certification.','px observed and reconstructed but remains pending without negative/equal-boundary native tests; pc static only.','Overflow path statically found but not triggered; unknown flags/groups/rotations remain unverified.']}
 (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'cases':len(rows),'supported_cases':sum(r['profile_supported'] for r in rows),'all_agree':True}))
if __name__=='__main__':main()

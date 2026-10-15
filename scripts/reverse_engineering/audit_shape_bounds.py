"""Match native shape comparison operands, equal branches and report counters."""
import argparse,hashlib,json,sys
from pathlib import Path
from argparse import Namespace
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import parse_document,check_file
from native_reference_cli import validate_native_run
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--include-landscape',action='store_true');a=p.parse_args();out=a.out.absolute();out.mkdir(exist_ok=False);base=ROOT/'evidence/business-map-232';rows=[];sources={}
 for folder in ['shape-bounds-native-r1','shape-bounds-native-r2','shape-rotation-native-r1']+(['shape-landscape-native-r2'] if a.include_landscape else []):
  matrix=base/folder/'matrix.json';sources[matrix.relative_to(ROOT).as_posix()]=sha(matrix)
  for row in json.loads(matrix.read_text())['cases']:
   source=ROOT/row['input'];d=ROOT/row['evidence_directory'];trace=json.loads((d/'trace.json').read_text());assert sha(source)==row['sha256'];native=validate_native_run(trace,(d/'native-result.txt').read_bytes().decode('utf-8'),'phd','docx',sha(source),True)
   _,data=parse_document(source);labels=data['labels'];hits=trace['breakpoint_hits'];geometry=[h['shape_bounds_state'] for h in hits if h['label']=='shape_bounds_compare'];assert len(geometry)==len(labels)+1==12
   # These immutable fixtures have one preceding ordinary inline image.
   assert geometry[0]['width']==data['images'][0]['native_display_width_mm'] and geometry[0]['height']==data['images'][0]['native_display_height_mm']
   for g,l in zip(geometry[1:],labels):
    assert (g['width'],g['height'],g['rotation'],g['selected_width'],g['selected_height'])==(l['width_mm'],l['height_mm'],l['native_rotation_degrees'],l['native_shape_selected_width_mm'],l['native_shape_selected_height_mm'])
    assert all(g[k]==0 for k in ['inset_138','inset_13c','inset_140','inset_144']);assert l['native_shape_width_limit_mm']==g['width_base']+5 and l['native_shape_height_limit_mm']==g['height_base']-6
   expected=sum(l['shape_overflow_geometry_candidate'] for l in labels);actual=row['drawing_state']['shape_bounds_count'];branch_count=sum(h['label']=='shape_bounds_emit' for h in hits);assert expected==actual==branch_count
   report=check_file(source,Namespace(work_type='phd',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False));ids={f['rule_id'] for f in report['findings']};assert ('Pic.ShapesOutOfBounds' in ids)==bool(actual);assert any('графические фигуры, выходящие за рамки текста' in d['message'] for d in native)==bool(actual)
   assert data['native232_vml_shape_bounds_profile_supported']
   rows.append({**row,'native_shape_counter':actual,'branch_hits':branch_count,'local_shape_counter':expected,'first_shape_operands':geometry[1],'shape_family_agrees':True,'native_total_diagnostics':len(native)})
   for f in [source,*d.iterdir()]:
    if f.is_file():sources[f.relative_to(ROOT).as_posix()]=sha(f)
 assert len(rows)==(20 if a.include_landscape else 14)
 result={'status':'passed_native232_shape_bounds_and_rotation_audit','cases':rows,'sources':sources,'limits':['Actual synthetic DOCX/NKR executions, one image plus eleven simple VML textboxes.','Four adjustment fields were zero, including two textbox-inset controls; their full source semantics remain unknown.','No general shape, arbitrary angle, school or rendered-layout equivalence; exact input and supported profile only.']}
 (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'cases':len(rows),'all_agree':True}))
if __name__=='__main__':main()

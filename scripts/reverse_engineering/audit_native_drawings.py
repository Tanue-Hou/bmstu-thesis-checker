"""Audit drawing counters, native floating arithmetic and corrected local families."""
import hashlib,json,sys
from argparse import Namespace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from check_document import check_file,parse_document
from native_reference_cli import validate_native_run
from verify_native_pixels import publish
from parsers.drawing_geometry import f32
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
PATTERNS={'Pic.FloatingImages':'плавающие рисунки','Pic.SmallLabels':'мелкие надписи','Pic.FloatingShapes':'плавающие графические фигуры','Pic.FloatingLabels':'плавающие надписи'}
def main():
 base=ROOT/'evidence/business-map-232';out=base/'drawing-audit-r1';out.mkdir(exist_ok=False);rows=[];sources={}
 for folder in ['drawing-boundaries-r2','drawing-boundaries-r3']:
  matrix=base/folder/'matrix.json';sources[matrix.relative_to(ROOT).as_posix()]=sha(matrix)
  for row in json.loads(matrix.read_text(encoding='utf-8'))['cases']:
   source=ROOT/row['input'];d=ROOT/row['evidence_directory'];trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));text=(d/'native-result.txt').read_bytes().decode('utf-8');assert sha(source)==row['sha256']
   native=validate_native_run(trace,text,'phd','docx',sha(source),True);state=row['drawing_state'];kind,data=parse_document(source)
   local=check_file(source,Namespace(work_type='phd',native_build=232,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False));findings={f['rule_id']:f for f in local['findings']}
   counts={rule:sum(phrase in diag['message'] for diag in native) for rule,phrase in PATTERNS.items()}
   for rule,number in counts.items():assert bool(number)==(rule in findings),(row['case'],rule,number)
   small=sum(l['small_geometry_candidate'] for l in data['labels']);assert small==state['small_label_count']
   area=0.0
   for im in data['images']:
    if im['placement']=='floating' and im['wrap_mode']=='wrapNone':area=f32(area+im['native_display_area_mm2'])
   assert area==state['floating_area_float'],(row['case'],area,state)
   geometry_hits=[h for h in trace['breakpoint_hits'] if h['label']=='small_label_geometry']
   assert len(geometry_hits)==len(data['labels']),(row['case'],'geometry hit count')
   for hit,label in zip(geometry_hits,data['labels']):assert hit['label_geometry']['width_candidate']==label['width_mm'] and hit['label_geometry']['height_candidate']==label['height_mm']
   assert counts['Pic.FloatingImages']==int(row['floating_image_emit']) and counts['Pic.SmallLabels']==int(row['small_labels_emit'])
   rows.append({'case':row['case'],'input':row['input'],'source_sha256':sha(source),'native_family_counts':counts,'local_family_counts':{rule:int(rule in findings) for rule in PATTERNS},'native_drawing_state':state,'measured_local_area':area,'local_small_label_count':small,'all_four_families_agree':True,'evidence_directory':row['evidence_directory']})
   for p in [source,d/'trace.json',d/'native-result.txt',d/'tracer-source.py.txt',d/'sender-source.cs.txt']:sources[p.relative_to(ROOT).as_posix()]=sha(p)
 final=out/'final-label-counter';report=publish(ROOT.parent/'private_trials/native-reference/drawing-labels-final-r1',final);trace=json.loads((final/'trace.json').read_text(encoding='utf-8'));state=next(h['drawing_state'] for h in trace['breakpoint_hits'] if h['label']=='drawing_report_state');assert state['count_slot_28']+state['count_slot_29']==11 and state['count_slot_30']+state['count_slot_32']==11 and state['small_label_count']==11
 for p in final.iterdir():sources[p.relative_to(ROOT).as_posix()]=sha(p)
 result={'status':'passed_bounded_native232_drawing_family_audit','native_build':232,'work_type':'phd','cases':rows,'final_label_slots':state,'sources':sources,'limits':['Fifteen synthetic DOCX inputs; same diagnostic families, not full native text or school compliance.','Early snapshots named slots26/27 raster/shape; wrapSquare proves that semantic alias incorrect. Slot offsets and values remain authoritative.','Simple VML textbox geometry and ordinary wrapNone/wrapSquare PNGs only; other shapes, fit/crop/rotation, units and modes need separate proof.']}
 (out/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'cases':len(rows),'families':len(PATTERNS),'final_small_counter':state['small_label_count']}))
if __name__=='__main__':main()

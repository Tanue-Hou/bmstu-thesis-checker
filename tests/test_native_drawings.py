import copy,json,sys,tempfile,unittest,zipfile,hashlib
from argparse import Namespace
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import check_file,parse_document,load_rule_registry,verification_context,context_evidence_valid
from native_reference_cli import validate_native_run
BASE=ROOT/'evidence/business-map-232'
FAMILIES={'Pic.FloatingImages','Pic.SmallLabels','Pic.FloatingShapes','Pic.FloatingLabels'}
def check(path,mode='phd',build=232):return check_file(path,Namespace(work_type=mode,native_build=build,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False))
def source(name):return BASE/'drawing-probes-r3'/(name+'.docx')
class NativeDrawingTests(unittest.TestCase):
 def test_all_retained_native_branches_and_geometry(self):
  audit=json.loads((BASE/'drawing-audit-r1/audit.json').read_text(encoding='utf-8'));self.assertEqual(len(audit['cases']),15)
  for row in audit['cases']:
   with self.subTest(case=row['case']):
    path=ROOT/row['input'];self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),row['source_sha256'])
    d=ROOT/row['evidence_directory'];trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));validate_native_run(trace,(d/'native-result.txt').read_bytes().decode('utf-8'),'phd','docx',row['source_sha256'],True)
    _,data=parse_document(path);hits=[h for h in trace['breakpoint_hits'] if h['label']=='small_label_geometry'];self.assertEqual(len(hits),len(data['labels']))
    for hit,label in zip(hits,data['labels']):
     self.assertEqual(hit['label_geometry']['width_candidate'],label['width_mm']);self.assertEqual(hit['label_geometry']['height_candidate'],label['height_mm'])
    findings={f['rule_id']:f for f in check(path)['findings']}
    for rule in FAMILIES:
     self.assertEqual(rule in findings,bool(row['native_family_counts'][rule]))
     if rule in findings:
      f=findings[rule];self.assertEqual(f['verification_status'],'verified_against_original');self.assertFalse(f['action_eligibility']['automatic_repair_allowed']);self.assertGreater(f['precise_locations']['occurrence_count'],0)
 def test_area_exclusive_boundary_aggregate_and_wrap_square(self):
  for name,expected in [('anchor499',False),('anchor500',False),('anchor501',True),('anchors2Equal',False),('anchors2Above',True),('anchorSquare501',False),('inline501',False)]:
   self.assertEqual('Pic.FloatingImages' in {f['rule_id'] for f in check(source(name))['findings']},expected,name)
 def test_small_body_is_not_small_label_and_axis_count_boundaries(self):
  ids={f['rule_id'] for f in check(source('body7'))['findings']};self.assertIn('Word.FontSizeTooSmall',ids);self.assertNotIn('Pic.SmallLabels',ids)
  for name,expected in [('labels1',False),('labels10',False),('labels11',True),('labels2mm',False),('labelsHeight1',True),('labelsHeight2',False)]:
   self.assertEqual('Pic.SmallLabels' in {f['rule_id'] for f in check(source(name))['findings']},expected,name)
 def test_version_format_degree_and_tamper_are_isolated(self):
  registry=load_rule_registry()
  for rule in FAMILIES:
   ctx=verification_context(registry[rule],'docx','phd',232);self.assertTrue(context_evidence_valid(ctx))
   for fmt,mode,build in [('pdf','phd',232),('docx','master',232),('docx','phd',999)]:self.assertIsNone(verification_context(registry[rule],fmt,mode,build))
   changed=copy.deepcopy(ctx);changed['implementation_hashes']['scripts/testvkr-service/parsers/drawing_geometry.py']='0'*64;self.assertFalse(context_evidence_valid(changed))
  for f in check(source('labels11'),'master')['findings']:
   if f['rule_id'] in FAMILIES:self.assertEqual(f['verification_status'],'pending_original_program_comparison')
 def test_unverified_geometry_never_inherits_label_proof(self):
  V='urn:schemas-microsoft-com:vml'
  with tempfile.TemporaryDirectory() as td:
   for variant in ['inset','unit','extra','group']:
    target=Path(td)/(variant+'.docx')
    with zipfile.ZipFile(source('labels11')) as src,zipfile.ZipFile(target,'w') as dst:
     for info in src.infolist():
      payload=src.read(info.filename)
      if info.filename=='word/document.xml':
       root=etree.fromstring(payload);shape=root.find('.//{'+V+'}shape')
       if variant=='inset':shape.find('{'+V+'}textbox').set('inset','0,0,0,0')
       elif variant=='unit':shape.set('style',shape.get('style').replace('1mm','1pt'))
       elif variant=='extra':shape.set('filled','f')
       else:
        parent=shape.getparent();parent.remove(shape);etree.SubElement(parent,'{'+V+'}group').append(shape)
       payload=etree.tostring(root)
      dst.writestr(info,payload)
    _,data=parse_document(target);self.assertFalse(data['native232_vml_label_profile_supported'],variant)
    for f in check(target)['findings']:
     if f['rule_id'] in FAMILIES:self.assertEqual(f['verification_status'],'pending_original_program_comparison')
 def test_crop_rotation_and_extent_mismatch_stay_pending(self):
  A='http://schemas.openxmlformats.org/drawingml/2006/main'
  with tempfile.TemporaryDirectory() as td:
   for variant in ['crop','rotation','extent','unknown_wrap']:
    path=Path(td)/(variant+'.docx')
    with zipfile.ZipFile(source('anchor501')) as src,zipfile.ZipFile(path,'w') as dst:
     for info in src.infolist():
      payload=src.read(info.filename)
      if info.filename=='word/document.xml':
       root=etree.fromstring(payload);xfrm=root.find('.//{'+A+'}xfrm')
       if variant=='rotation':xfrm.set('rot','60000')
       elif variant=='extent':xfrm.find('{'+A+'}ext').set('cx','100')
       elif variant=='crop':etree.SubElement(root.find('.//{'+A+'}blip').getparent(),'{'+A+'}srcRect',l='10')
       else:
        wrap=root.find('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}wrapNone');wrap.tag='{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}wrapTopAndBottom'
       payload=etree.tostring(root)
      dst.writestr(info,payload)
    _,data=parse_document(path);self.assertFalse(data['native232_floating_profile_supported'])
    findings=[f for f in check(path)['findings'] if f['rule_id']=='Pic.FloatingImages']
    if variant=='unknown_wrap':self.assertFalse(findings)
    else:self.assertEqual(findings[0]['verification_status'],'pending_original_program_comparison')
if __name__=='__main__':unittest.main()

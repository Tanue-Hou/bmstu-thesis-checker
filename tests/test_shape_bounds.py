import copy,json,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from test_native_drawings import check
from check_document import parse_document,load_rule_registry,verification_context,context_evidence_valid
BASE=ROOT/'evidence/business-map-232'
class ShapeBoundsTests(unittest.TestCase):
 def test_twenty_real_operand_branch_and_counter_cases(self):
  audit=json.loads((BASE/'shape-bounds-audit-r2/audit.json').read_text());self.assertEqual(len(audit['cases']),20)
  for row in audit['cases']:
   with self.subTest(case=row['case']):
    path=ROOT/row['input'];_,data=parse_document(path);self.assertTrue(data['native232_vml_shape_bounds_profile_supported']);self.assertEqual(sum(l['shape_overflow_geometry_candidate'] for l in data['labels']),row['native_shape_counter'])
    findings={f['rule_id']:f for f in check(path)['findings']};self.assertEqual('Pic.ShapesOutOfBounds' in findings,bool(row['native_shape_counter']))
    if 'Pic.ShapesOutOfBounds' in findings:
     f=findings['Pic.ShapesOutOfBounds'];self.assertEqual(f['verification_status'],'verified_against_original');self.assertFalse(f['action_eligibility']['automatic_repair_allowed']);self.assertEqual(f['precise_locations']['occurrence_count'],11)
 def test_equal_shape_boundary_differs_from_textbox_boundary(self):
  for name in ['widthEqual','heightEqual']:
   findings={f['rule_id'] for f in check(BASE/'shape-bounds-inputs-r1'/(name+'.docx'))['findings']};self.assertIn('Pic.ShapesOutOfBounds',findings);self.assertNotIn('Pic.LabelsOutOfBounds',findings)
 def test_rotation_bin_boundary(self):
  audit=json.loads((BASE/'shape-bounds-audit-r2/audit.json').read_text());rows={r['case']:r for r in audit['cases']}
  self.assertEqual(rows['rotated44']['native_shape_counter'],11);self.assertEqual(rows['rotated45']['native_shape_counter'],0);self.assertEqual(rows['rotated46']['native_shape_counter'],0)
  self.assertEqual(rows['rotated90']['first_shape_operands']['selected_width'],5);self.assertEqual(rows['rotated180']['first_shape_operands']['selected_width'],253)
 def test_context_integrity_and_no_cross_mode_transfer(self):
  rule=load_rule_registry()['Pic.ShapesOutOfBounds'];ctx=verification_context(rule,'docx','phd',232);self.assertTrue(context_evidence_valid(ctx));changed=copy.deepcopy(ctx);changed['implementation_hashes']['scripts/testvkr-service/parsers/drawing_geometry.py']='0'*64;self.assertFalse(context_evidence_valid(changed))
  for fmt,mode,build in [('pdf','phd',232),('docx','master',232),('docx','phd',230)]:self.assertIsNone(verification_context(rule,fmt,mode,build))
 def test_unproven_angle_stays_pending(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'angle.docx'
   with zipfile.ZipFile(BASE/'shape-bounds-inputs-r1/rotated180.docx') as src,zipfile.ZipFile(path,'w') as dst:
    for info in src.infolist():
     payload=src.read(info.filename)
     if info.filename=='word/document.xml':payload=payload.replace(b'rotation:180',b'rotation:181')
     dst.writestr(info,payload)
   _,data=parse_document(path);self.assertFalse(data['native232_vml_shape_bounds_profile_supported']);f=next(f for f in check(path)['findings'] if f['rule_id']=='Pic.ShapesOutOfBounds');self.assertEqual(f['verification_status'],'pending_original_program_comparison')
 def test_generator_preserves_landscape_shape_dimensions(self):
  with tempfile.TemporaryDirectory(dir=ROOT) as td:
   out=Path(td)/'inputs';run=subprocess.run([sys.executable,str(ROOT/'scripts/reverse_engineering/generate_shape_bounds.py'),'--out',str(out)],capture_output=True);self.assertEqual(run.returncode,0,run.stderr)
   rows={r['case']:r for r in json.loads((out/'inputs.json').read_text())['cases']}
   for name,expected in [('landscapeWidthBelow',263.99),('landscapeWidthEqual',264),('landscapeWidthAbove',264.01)]:
    self.assertEqual(rows[name]['width_mm'],expected)
    with zipfile.ZipFile(out/(name+'.docx')) as src:
     root=etree.fromstring(src.read('word/document.xml'));style=root.find('.//{urn:schemas-microsoft-com:vml}shape').get('style');self.assertIn('width:'+str(expected)+'mm',style)
if __name__=='__main__':unittest.main()

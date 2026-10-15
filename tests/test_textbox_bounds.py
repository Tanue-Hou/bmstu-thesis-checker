import copy,json,sys,tempfile,unittest,zipfile
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from test_native_drawings import check
from check_document import parse_document,load_rule_registry,verification_context,context_evidence_valid
from compare_native_trial import parse_diagnostics
BASE=ROOT/'evidence/business-map-232'
class TextboxBoundsTests(unittest.TestCase):
 def test_real_boundaries_and_scope(self):
  audit=json.loads((BASE/'textbox-bounds-audit-r1/audit.json').read_text());self.assertEqual(len(audit['cases']),13)
  for row in audit['cases']:
   with self.subTest(case=row['case']):
    findings={f['rule_id']:f for f in check(ROOT/row['input'])['findings']};self.assertEqual('Pic.LabelsOutOfBounds' in findings,bool(row['local_overflow_count']))
    if row['local_overflow_count']:
     f=findings['Pic.LabelsOutOfBounds'];self.assertEqual(f['verification_status'],'verified_against_original');self.assertEqual(f['precise_locations']['occurrence_count'],11);self.assertEqual(f['precise_locations']['occurrences'][0]['kind'],'docx_textbox');self.assertFalse(f['action_eligibility']['automatic_repair_allowed'])
    self.assertNotIn('Pic.SmallLabels',findings)
    self.assertEqual('Pic.FloatingLabels' in findings,row['case'] not in {'positionRight','positionBelow'})
    text=(ROOT/row['evidence_directory']/'native-result.txt').read_bytes().decode('utf-8');mapped=parse_diagnostics(text,'docx');self.assertEqual(any(d['rule_id']=='Pic.LabelsOutOfBounds' for d in mapped),bool(row['local_overflow_count']))
 def test_dimension_precedence_and_orientation(self):
  for case in ['smallWidthTall','smallHeightWide']:
   _,data=parse_document(BASE/'textbox-bounds-inputs-r1'/(case+'.docx'));self.assertTrue(all(l['overflow_geometry_candidate'] and not l['small_geometry_candidate'] for l in data['labels']))
  _,data=parse_document(BASE/'textbox-bounds-inputs-r1/landscapeTall.docx');self.assertEqual(data['labels'][0]['native_height_limit_mm'],167);self.assertEqual(data['labels'][0]['native_width_limit_mm'],264)
 def test_context_hash_and_mode_isolation(self):
  rule=load_rule_registry()['Pic.LabelsOutOfBounds'];ctx=verification_context(rule,'docx','phd',232);self.assertTrue(context_evidence_valid(ctx))
  for fmt,mode,build in [('pdf','phd',232),('docx','master',232),('docx','phd',230)]:self.assertIsNone(verification_context(rule,fmt,mode,build))
  changed=copy.deepcopy(ctx);changed['implementation_hashes']['scripts/testvkr-service/parsers/drawing_geometry.py']='0'*64;self.assertFalse(context_evidence_valid(changed))
 def test_non_a4_cannot_inherit_fixed_profile(self):
  source=BASE/'textbox-bounds-inputs-r1/widthAbove.docx';W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'non-a4.docx'
   with zipfile.ZipFile(source) as src,zipfile.ZipFile(path,'w') as dst:
    for info in src.infolist():
     payload=src.read(info.filename)
     if info.filename=='word/document.xml':
      root=etree.fromstring(payload);root.find('.//{'+W+'}pgSz').set('{'+W+'}h','20000');payload=etree.tostring(root)
     dst.writestr(info,payload)
   _,data=parse_document(path);self.assertFalse(data['native232_vml_bounds_profile_supported'])
   for f in check(path)['findings']:
    if f['rule_id']=='Pic.LabelsOutOfBounds':self.assertEqual(f['verification_status'],'pending_original_program_comparison')
if __name__=='__main__':unittest.main()

import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from test_native_drawings import check
from check_document import parse_document
BASE=ROOT/'evidence/business-map-232'
class NativeTextboxTests(unittest.TestCase):
 def test_all_actual_branch_counter_and_dimension_records(self):
  audit=json.loads((BASE/'textbox-audit-r1/audit.json').read_text());self.assertEqual(len(audit['cases']),32)
  for row in audit['cases']:
   with self.subTest(case=row['case']):
    _,data=parse_document(ROOT/row['input']);labels=data['labels'];self.assertEqual(sum(l['small_geometry_candidate'] for l in labels),row['drawing_state']['small_label_count'])
    self.assertEqual((labels[0]['width_mm'],labels[0]['native_effective_height_mm']),(row['first_geometry']['width_candidate'],row['first_geometry']['height_candidate']))
    self.assertEqual(data['native232_vml_label_profile_supported'],row['case']!='px')
    findings={f['rule_id']:f for f in check(ROOT/row['input'])['findings']};self.assertEqual('Pic.SmallLabels' in findings,row['small_labels_emit'])
    for rule in ['Pic.SmallLabels','Pic.FloatingLabels','Pic.FloatingShapes']:
     if rule in findings:self.assertEqual(findings[rule]['verification_status'],'pending_original_program_comparison' if row['case']=='px' else 'verified_against_original');self.assertFalse(findings[rule]['action_eligibility']['automatic_repair_allowed'])
 def test_shape_fit_suppresses_only_height_and_textbox_layer_differs(self):
  audit=json.loads((BASE/'textbox-audit-r1/audit.json').read_text());rows={r['case']:r for r in audit['cases']}
  for name in ['shapeFitHeightTrue','shapeFitHeightT']:self.assertEqual(rows[name]['local_small_count'],0);self.assertEqual(rows[name]['first_geometry']['height_candidate'],10)
  for name in ['fitHeightTrue','fitHeight','shapeFitWidthT','shapeFitHeightFalse']:self.assertEqual(rows[name]['local_small_count'],11)
 def test_native_px_factor_is_not_assumed_screen_dpi(self):
  _,data=parse_document(BASE/'textbox-probes-r1/px.docx');self.assertAlmostEqual(data['labels'][0]['width_mm'],0.010431496426463127);self.assertFalse(data['native232_vml_label_profile_supported'])
if __name__=='__main__':unittest.main()

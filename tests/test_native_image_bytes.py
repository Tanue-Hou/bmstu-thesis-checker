import copy,json,sys,tempfile,unittest,zipfile
from argparse import Namespace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from check_document import check_file,load_rule_registry,verification_context,context_evidence_valid,parse_document
BASE=ROOT/'evidence/business-map-232'
def check(path,mode='phd',build=232):return check_file(path,Namespace(work_type=mode,native_build=build,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False))
class NativeImageByteTests(unittest.TestCase):
 def test_real_boundaries_aggregate_and_descriptor(self):
  audit=json.loads((BASE/'image-bytes-audit-r1/audit.json').read_text(encoding='utf-8'))
  for row in audit['cases']:
   with self.subTest(case=row['case']):
    report=check(ROOT/row['input']);findings=[f for f in report['findings'] if f['rule_id']=='Pic.FileSizeTooLarge'];self.assertEqual(bool(findings),bool(row['native_counter']))
    if findings:
     f=findings[0];self.assertEqual(f['threshold']['value'],30000000);self.assertEqual(f['threshold']['native_message_value'],40)
     self.assertEqual(f['verification_status'],'verified_against_original');self.assertEqual(f['verification_scope']['build'],232)
     self.assertEqual(f['precise_locations']['occurrence_count'],row['native_counter']);self.assertEqual(f['precise_locations']['occurrences'][0]['zip_local_uncompressed_size'],30000001)
     self.assertFalse(f['action_eligibility']['automatic_repair_allowed'])
 def test_aggregate_false_positive_and_30m_false_negative_corrected(self):
  folder=BASE/'image-bytes-boundaries-r1/inputs'
  self.assertIn('Pic.FileSizeTooLarge',{f['rule_id'] for f in check(folder/'aggregate.docx',build=230)['findings']})
  self.assertNotIn('Pic.FileSizeTooLarge',{f['rule_id'] for f in check(folder/'aggregate.docx')['findings']})
  self.assertNotIn('Pic.FileSizeTooLarge',{f['rule_id'] for f in check(folder/'above.docx',build=230)['findings']})
  self.assertIn('Pic.FileSizeTooLarge',{f['rule_id'] for f in check(folder/'above.docx')['findings']})
 def test_flags8_uses_local_zero_not_real_or_central_size(self):
  _,data=parse_document(BASE/'image-bytes-boundaries-r1/inputs/descriptor.docx');im=data['images'][0]
  self.assertEqual(im['zip_local_flags'],8);self.assertEqual(im['zip_local_uncompressed_size'],0);self.assertEqual(im['zip_central_uncompressed_size'],30000001)
 def test_proof_and_mode_do_not_transfer(self):
  rule=load_rule_registry()['Pic.FileSizeTooLarge'];ctx=verification_context(rule,'docx','phd',232);self.assertTrue(context_evidence_valid(ctx))
  self.assertIsNone(verification_context(rule,'pdf','phd',232));self.assertIsNone(verification_context(rule,'docx','master',232));self.assertIsNone(verification_context(rule,'docx','phd',230))
  ctx=copy.deepcopy(ctx);ctx['implementation_hashes']['scripts/issue_locations.py']='0'*64;self.assertFalse(context_evidence_valid(ctx))
  f=next(f for f in check(BASE/'image-bytes-boundaries-r1/inputs/above.docx','master')['findings'] if f['rule_id']=='Pic.FileSizeTooLarge');self.assertEqual(f['verification_status'],'pending_original_program_comparison')
 def test_zip64_profile_is_detected_and_not_verified(self):
  source=BASE/'image-bytes-boundaries-r1/inputs/above.docx'
  with tempfile.TemporaryDirectory() as td:
   target=Path(td)/'zip64.docx'
   with zipfile.ZipFile(source) as src,zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as dst:
    for info in src.infolist():
     if info.filename.startswith('word/media/'):
      with dst.open(info,'w',force_zip64=True) as output:output.write(src.read(info.filename))
     else:dst.writestr(info,src.read(info.filename))
   _,data=parse_document(target);self.assertTrue(data['images'][0]['zip_uses_zip64']);self.assertFalse(data['native232_image_bytes_profile_supported'])
   findings=[f for f in check(target)['findings'] if f['rule_id']=='Pic.FileSizeTooLarge'];self.assertTrue(all(f['verification_status']=='pending_original_program_comparison' for f in findings))
if __name__=='__main__':unittest.main()

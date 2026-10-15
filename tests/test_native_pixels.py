import copy,json,sys,tempfile,unittest,zipfile
from argparse import Namespace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_document import check_file,parse_document,load_rule_registry,verification_context,context_evidence_valid,finding_to_dict
from native_reference_cli import validate_native_run
from checkers.pictures import PicturesChecker
BASE=ROOT/'evidence/business-map-232'
def args(mode='phd',build=232):return Namespace(work_type=mode,native_build=build,skip_structure=False,skip_pictures=False,skip_word_format=False,skip_dictionary=False)
class NativePixelTests(unittest.TestCase):
 def test_six_real_branches_and_local_predicate(self):
  matrix=json.loads((BASE/'pixel-boundaries-r1/matrix.json').read_text(encoding='utf-8'))
  for row in matrix['cases']:
   with self.subTest(case=row['case']):
    d=ROOT/row['evidence_directory'];trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));text=(d/'native-result.txt').read_bytes().decode('utf-8')
    validate_native_run(trace,text,'phd',row['format'],row['input_sha256'],row['large_branch_observed'])
    report=check_file(ROOT/row['input'],args());pixels=[f for f in report['findings'] if f['rule_id']=='Pic.PixelSizeTooLarge']
    self.assertEqual(bool(pixels),row['large_branch_observed'])
    if pixels:
     self.assertEqual(pixels[0]['verification_status'],'verified_against_original');self.assertEqual(pixels[0]['verification_scope']['build'],232)
     self.assertEqual(pixels[0]['threshold']['count_images'],1);self.assertFalse(pixels[0]['action_eligibility']['automatic_repair_allowed'])
    self.assertTrue(all(f['verification_status']!='verified_against_original' for f in report['findings'] if f['rule_id']!='Pic.PixelSizeTooLarge'))
 def test_final_default_output_flags_and_aggregate_counters(self):
  receipt=json.loads((BASE/'pixel-final-r1/receipt.json').read_text(encoding='utf-8'));self.assertEqual(len(receipt['cases']),3)
  for row in receipt['cases']:
   d=BASE/'pixel-final-r1'/row['case'];trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));text=(d/'native-result.txt').read_bytes().decode('utf-8')
   validate_native_run(trace,text,'phd',row['file_type'],row['source_sha256'],True)
   self.assertTrue(trace['cleanup_verified']);self.assertTrue(row['pixel_fix_default_enabled'])
   self.assertEqual(next(h['pixel_counter_state']['count'] for h in trace['breakpoint_hits'] if h['label']=='image_counter_report_gate'),row['counter'])
 def test_codepage_pair_and_tampered_conversion_rejected(self):
  d=BASE/'pixel-audit-r2/pixel-treatment-r1';trace=json.loads((d/'trace.json').read_text(encoding='utf-8'));text=(d/'native-result.txt').read_bytes().decode('utf-8')
  validate_native_run(trace,text,'phd','docx',pixel_cp1251=True)
  with self.assertRaises(ValueError):validate_native_run(trace,text,'phd','docx')
  broken=copy.deepcopy(trace);next(c for c in broken['large_buffer_codepage_calls'] if c.get('matched_literal'))['return_preferred_va']='0x00000000'
  with self.assertRaises(ValueError):validate_native_run(broken,text,'phd','docx',pixel_cp1251=True)
  broken=copy.deepcopy(trace);broken['breakpoint_hits']=[h for h in broken['breakpoint_hits'] if h['label']!='pixel_literal_return']
  with self.assertRaises(ValueError):validate_native_run(broken,text,'phd','docx',pixel_cp1251=True)
 def test_native_build_and_context_are_not_cross_products(self):
  rule=load_rule_registry()['Pic.PixelSizeTooLarge']
  self.assertIsNone(verification_context(rule,'docx','master',232));self.assertIsNone(verification_context(rule,'docx','phd',999))
  context=verification_context(rule,'docx','phd',232);self.assertTrue(context_evidence_valid(context))
  context=copy.deepcopy(context);context['implementation_hashes']['scripts/testvkr-service/checkers/pictures.py']='0'*64;self.assertFalse(context_evidence_valid(context))
  p=BASE/'pixel-boundaries-r1/inputs/docx_4001x4000.docx'
  f=next(f for f in check_file(p,args('master'))['findings'] if f['rule_id']=='Pic.PixelSizeTooLarge');self.assertEqual(f['verification_status'],'pending_original_program_comparison')
 def test_resource_aliases_do_not_duplicate_image_count(self):
  import fitz
  p=BASE/'pixel-boundaries-r1/inputs/pdf_4001x4000.pdf'
  with fitz.open(p) as doc:
   self.assertGreater(len(doc[0].get_images()),len({x[0] for x in doc[0].get_images()}))
  _,data=parse_document(p);self.assertEqual(len(data['images']),1);self.assertEqual(len(data['images'][0]['bboxes']),1)
 def test_unsupported_geometry_and_document_kind_stay_pending(self):
  for kind in ['docx','pdf']:
   p=BASE/'pixel-boundaries-r1/inputs'/(kind+'_4001x4000.'+kind);_,data=parse_document(p);data['native_build']=232;data['document_kind']='nkr'
   finding=next(f for f in PicturesChecker(data,kind,'phd').check() if f.code=='Pic.PixelSizeTooLarge')
   data['native232_single_inline_png_profile_supported']=False;data['page_count']=2
   f=finding_to_dict(finding,load_rule_registry(),{},kind,'phd',data);self.assertEqual(f['verification_status'],'pending_original_program_comparison')
 def test_pdf_mask_cannot_inherit_rgb_proof(self):
  p=BASE/'pixel-boundaries-r1/inputs/pdf_4001x4000.pdf';_,data=parse_document(p);data['native_build']=232;data['document_kind']='nkr'
  finding=next(f for f in PicturesChecker(data,'pdf','phd').check() if f.code=='Pic.PixelSizeTooLarge')
  for attribute,value in [('soft_mask_xref',99),('has_color_mask',True)]:
   changed=copy.deepcopy(data);changed['images'][0][attribute]=value
   f=finding_to_dict(finding,load_rule_registry(),{},'pdf','phd',changed);self.assertEqual(f['verification_status'],'pending_original_program_comparison')
 def test_docx_grouped_blips_and_truncated_png_stay_pending(self):
  from lxml import etree
  source=BASE/'pixel-boundaries-r1/inputs/docx_4001x4000.docx'
  with tempfile.TemporaryDirectory() as td:
   for kind in ['group','truncated']:
    path=Path(td)/(kind+'.docx')
    with zipfile.ZipFile(source) as src,zipfile.ZipFile(path,'w') as dest:
     for info in src.infolist():
      payload=src.read(info.filename)
      if kind=='group' and info.filename=='word/document.xml':
       root=etree.fromstring(payload);blip=root.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip');blip.getparent().append(copy.deepcopy(blip));payload=etree.tostring(root)
      if kind=='truncated' and info.filename=='word/media/image1.png':payload=payload[:33]
      dest.writestr(info,payload)
    _,data=parse_document(path);self.assertFalse(data['native232_single_inline_png_profile_supported'])
    f=next(f for f in check_file(path,args())['findings'] if f['rule_id']=='Pic.PixelSizeTooLarge');self.assertEqual(f['verification_status'],'pending_original_program_comparison')
if __name__=='__main__':unittest.main()

import copy,json,sys,unittest,tempfile,zipfile
from lxml import etree
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from test_native_drawings import check
from check_document import parse_document,load_rule_registry,verification_context,context_evidence_valid
BASE=ROOT/'evidence/business-map-232'
class NativeFontTests(unittest.TestCase):
 def test_all_twenty_nine_actual_counter_and_diagnostic_cases(self):
  audit=json.loads((BASE/'font-audit-r1/audit.json').read_text());self.assertEqual(len(audit['cases']),29)
  for row in audit['cases']:
   with self.subTest(case=row['case'],mode=row['work_type']):
    report=check(ROOT/row['input'],row['work_type']);counts=report['native_word_observations']['font_counters'];self.assertTrue(report['native_word_observations']['profile_supported'])
    for bucket in ['small','tiny','large']:self.assertEqual(counts[bucket],row['font_state'][bucket+'_count'])
    found={f['rule_id']:f for f in report['findings']}
    for bucket,rule in [('small','Word.FontSizeTooSmall'),('large','Word.FontSizeTooLarge')]:
     self.assertEqual(rule in found,counts[bucket]>10)
     if rule in found:
      self.assertEqual(found[rule]['verification_status'],'verified_against_original');self.assertEqual(found[rule]['verification_scope']['build'],232);self.assertEqual(sum(l['utf16_units'] for l in found[rule]['precise_locations']['occurrences']),counts[bucket])
 def test_utf16_spaces_and_tiny_bucket_are_not_python_strip_counts(self):
  for case,count in [('smallSpacePad',12),('smallSpaces',11),('smallEmoji',12)]:
   f=next(f for f in check(BASE/'font-inputs-r1'/(case+'.docx'),'master')['findings'] if f['rule_id']=='Word.FontSizeTooSmall');self.assertEqual(f['threshold']['count_chars'],count)
  report=check(BASE/'font-inputs-r1/tinyEqual.docx','master');self.assertEqual(report['native_word_observations']['font_counters']['tiny'],11);self.assertNotIn('Word.FontSizeTooSmall',{f['rule_id'] for f in report['findings']})
 def test_textbox_count_gate_and_no_outer_paragraph_duplication(self):
  for case,large in [('largeTextbox',0),('largeTextbox101',0),('largeAfter100',0),('largeAfter101',11)]:
   report=check(BASE/'font-inputs-r1'/(case+'.docx'),'master');self.assertEqual(report['native_word_observations']['font_counters']['large'],large)
   _,data=parse_document(BASE/'font-inputs-r1'/(case+'.docx'));self.assertEqual(data['paragraphs'][-1]['runs'],[])
  f=next(f for f in check(BASE/'font-inputs-r1/largeAfter101.docx','master')['findings'] if f['rule_id']=='Word.FontSizeTooLarge');loc=f['precise_locations']['occurrences'][0];self.assertEqual(loc['kind'],'docx_textbox_run');self.assertEqual(loc['previous_textbox_utf16_units'],101)
 def test_font_style_chains_are_resolved_before_counting(self):
  for case,rule in [('paragraphInheritedSmall','Word.FontSizeTooSmall'),('characterInheritedLarge','Word.FontSizeTooLarge')]:
   f=next(f for f in check(BASE/'font-inputs-r2'/(case+'.docx'),'master')['findings'] if f['rule_id']==rule);self.assertEqual(f['threshold']['count_chars'],11)
 def test_contexts_do_not_transfer_to_pdf_other_modes_or_tampered_source(self):
  for rule_id in ['Word.FontSizeTooSmall','Word.FontSizeTooLarge']:
   rule=load_rule_registry()[rule_id]
   for mode in ['master','phd']:self.assertTrue(context_evidence_valid(verification_context(rule,'docx',mode,232)))
   for fmt,mode in [('pdf','master'),('pdf','phd'),('docx','bachelor')]:self.assertIsNone(verification_context(rule,fmt,mode,232))
   changed=copy.deepcopy(verification_context(rule,'docx','master',232));changed['implementation_hashes']['scripts/testvkr-service/checkers/native_font_counts.py']='0'*64;self.assertFalse(context_evidence_valid(changed))
 def test_unmeasured_control_in_anomalous_font_cannot_inherit_proof(self):
  W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'control.docx'
   with zipfile.ZipFile(BASE/'font-inputs-r1/small11.docx') as src,zipfile.ZipFile(path,'w') as dst:
    for info in src.infolist():
     payload=src.read(info.filename)
     if info.filename=='word/document.xml':
      root=etree.fromstring(payload);paragraph=root.find('{'+W+'}body').findall('{'+W+'}p')[-1];etree.SubElement(paragraph.find('{'+W+'}r'),'{'+W+'}br');payload=etree.tostring(root)
     dst.writestr(info,payload)
   report=check(path,'master');self.assertFalse(report['native_word_observations']['profile_supported']);f=next(f for f in report['findings'] if f['rule_id']=='Word.FontSizeTooSmall');self.assertEqual(f['verification_status'],'pending_original_program_comparison')
if __name__=='__main__':unittest.main()

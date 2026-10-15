import copy
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from test_native_drawings import check
from check_document import parse_document,load_rule_registry,verification_context,context_evidence_valid
from checkers.native_scale_counts import count_scale_candidates

BASE=ROOT/'evidence/business-map-232'


class NativeScaleTests(unittest.TestCase):
    def test_all_actual_scale_counters_and_diagnostics(self):
        audit=json.loads((BASE/'scale-audit-r1/audit.json').read_text())
        self.assertEqual(len(audit['cases']),52)
        for row in audit['cases']:
            with self.subTest(case=row['case'],mode=row['work_type']):
                report=check(ROOT/row['input'],row['work_type'])
                obs=report['native_scale_observations']
                self.assertTrue(obs['profile_supported'])
                self.assertEqual(obs['counters'],row['local_scale_counters'])
                found={f['rule_id']:f for f in report['findings']}
                for bucket,rule in [('small','Word.FontScaleTooSmall'),('large','Word.FontScaleTooLarge')]:
                    self.assertEqual(rule in found,obs['counters'][bucket]>10)
                    if rule in found:
                        self.assertEqual(found[rule]['verification_status'],'verified_against_original')
                        locations=found[rule]['precise_locations']['occurrences']
                        self.assertEqual(sum(l['utf16_units'] for l in locations),obs['counters'][bucket])
                        self.assertTrue(all(l['native_font_enabled'] and l['run_xml_path'] for l in locations))

    def test_tiny_and_ignored_scale_are_not_ordinary_small_diagnostics(self):
        for case,tiny in [('tiny30_11',11),('scale2_11',11),('scale1_11',0)]:
            report=check(BASE/'scale-inputs-r2'/(case+'.docx'),'master')
            self.assertEqual(report['native_scale_observations']['counters']['tiny'],tiny)
            self.assertNotIn('Word.FontScaleTooSmall',{f['rule_id'] for f in report['findings']})

    def test_large_textbox_scale_does_not_require_prior100_text_units(self):
        report=check(BASE/'scale-inputs-r2/textboxLarge.docx','master')
        finding=next(f for f in report['findings'] if f['rule_id']=='Word.FontScaleTooLarge')
        self.assertEqual(finding['threshold']['count_chars'],11)
        loc=finding['precise_locations']['occurrences'][0]
        self.assertEqual(loc['kind'],'docx_textbox_run')
        self.assertEqual(loc['actual'],131)

    def test_linked_scale_remains_separate_from_standard_ooxml_value(self):
        _,data=parse_document(BASE/'scale-inputs-r2/linkedLarge.docx')
        run=data['paragraphs'][-1]['runs'][0]
        self.assertEqual(run['scale_pct'],69)
        self.assertEqual(run['native_scale_pct'],131)
        counts,_=count_scale_candidates(data)
        self.assertEqual(counts,{'small':0,'tiny':0,'large':11})

    def test_fractional_scale_is_not_promoted_to_native_proof(self):
        W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'fractional.docx'
            with zipfile.ZipFile(BASE/'scale-inputs-r2/small69_11.docx') as src,zipfile.ZipFile(path,'w') as dst:
                for info in src.infolist():
                    payload=src.read(info.filename)
                    if info.filename=='word/document.xml':
                        root=etree.fromstring(payload)
                        node=root.find('{'+W+'}body').findall('{'+W+'}p')[-1].find('.//{'+W+'}w')
                        node.set('{'+W+'}val','69.5');payload=etree.tostring(root)
                    dst.writestr(info,payload)
            report=check(path,'master')
            self.assertFalse(report['native_scale_observations']['profile_supported'])
            self.assertFalse(any(f['verification_status']=='verified_against_original' for f in report['findings'] if f['rule_id'].startswith('Word.FontScale')))

    def test_evidence_and_format_scope_do_not_transfer(self):
        for rule_id in ['Word.FontScaleTooSmall','Word.FontScaleTooLarge']:
            rule=load_rule_registry()[rule_id]
            for mode in ['master','phd']:
                context=verification_context(rule,'docx',mode,232)
                self.assertTrue(context_evidence_valid(context))
                changed=copy.deepcopy(context)
                changed['implementation_hashes']['scripts/testvkr-service/checkers/native_scale_counts.py']='0'*64
                self.assertFalse(context_evidence_valid(changed))
            self.assertIsNone(verification_context(rule,'pdf','phd',232))
            self.assertIsNone(verification_context(rule,'docx','bachelor',232))

    def test_scaled_run_with_unmeasured_control_cannot_inherit_proof(self):
        W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'controlled.docx'
            with zipfile.ZipFile(BASE/'scale-inputs-r2/small69_11.docx') as src,zipfile.ZipFile(path,'w') as dst:
                for info in src.infolist():
                    payload=src.read(info.filename)
                    if info.filename=='word/document.xml':
                        root=etree.fromstring(payload)
                        p=root.find('{'+W+'}body').findall('{'+W+'}p')[-1]
                        etree.SubElement(p.find('{'+W+'}r'),'{'+W+'}br');payload=etree.tostring(root)
                    dst.writestr(info,payload)
            report=check(path,'master')
            self.assertFalse(report['native_scale_observations']['profile_supported'])
            finding=next(f for f in report['findings'] if f['rule_id']=='Word.FontScaleTooSmall')
            self.assertEqual(finding['verification_status'],'pending_original_program_comparison')


if __name__=='__main__':
    unittest.main()

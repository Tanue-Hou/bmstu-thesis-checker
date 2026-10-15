import copy,importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from native_reference_cli import validate_native_run

class NativeReferenceTests(unittest.TestCase):
    def run_record(self,name):
        folder=ROOT/'evidence/business-map-232'/name
        return json.loads((folder/'trace.json').read_text()),(folder/'native-result.txt').read_bytes().decode('utf-8')
    def test_real_native_volume_boundary_reports(self):
        for case,count in [('g_chars43199',1),('g_chars43200',0),('g_toc47',1),('g_toc48',0)]:
            with self.subTest(case=case):
                trace,text=self.run_record('native-volume-'+case+'-r3')
                self.assertEqual(len(validate_native_run(trace,text)),count)
                labels={hit['label'] for hit in trace['breakpoint_hits']}
                self.assertEqual('volume_insufficient_emit' in labels,bool(count))
    def test_complex_reference_reports_thirteen_diagnostics(self):
        trace,text=self.run_record('native-direct-complex-reference-r3')
        self.assertEqual(len(validate_native_run(trace,text)),13)
    def test_incomplete_return_cannot_be_success(self):
        trace,text=self.run_record('native-volume-g_chars43200-r3')
        trace['breakpoint_hits']=[h for h in trace['breakpoint_hits'] if h['label']!='file_check_return']
        with self.assertRaises(ValueError):validate_native_run(trace,text)
    def test_missing_completion_text_cannot_be_zero_findings(self):
        trace,_=self.run_record('native-volume-g_chars43200-r3')
        with self.assertRaises(ValueError):validate_native_run(trace,'Файл: input.docx\n')
    def test_changed_source_and_wrong_codepage_are_rejected(self):
        trace,text=self.run_record('native-volume-g_chars43200-r3')
        changed=copy.deepcopy(trace);changed['probe_document']['unchanged']=False
        with self.assertRaises(ValueError):validate_native_run(changed,text)
        changed=copy.deepcopy(trace)
        next(c for c in changed['large_buffer_codepage_calls'] if 'intervention_codepage' in c)['intervention_codepage']=65001
        with self.assertRaises(ValueError):validate_native_run(changed,text)
    def test_incomplete_numbering_is_rejected(self):
        trace,text=self.run_record('native-direct-complex-reference-r3')
        with self.assertRaises(ValueError):validate_native_run(trace,text.replace('\n2. ','\n20. ',1))
    def test_truncated_and_missing_length_receipt_are_rejected(self):
        trace,text=self.run_record('native-direct-complex-reference-r3')
        with self.assertRaises(ValueError):validate_native_run(trace,text[:-10])
        del trace['probe_document']['report_utf16_units_expected']
        with self.assertRaises(ValueError):validate_native_run(trace,text)
    def test_mcp_scope_prevents_unvalidated_native_modes(self):
        spec=importlib.util.spec_from_file_location('native_reference_test_server',ROOT/'mcp/server.py');server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        tool=next(t for t in server.tool_list_result()['tools'] if t['name']=='check_native_reference_experimental')
        self.assertEqual(tool['inputSchema']['properties']['work_type']['enum'],['master','phd'])
        with self.assertRaises(ValueError):server.handle_tool_call({'name':'check_native_reference_experimental','arguments':{'work_type':'bachelor'}})
    def test_actual_native_modes_and_formats(self):
        base=ROOT/'evidence/business-map-232/native-modes-r1'
        matrix=json.loads((base/'matrix.json').read_text())
        for row in matrix['cases']:
            with self.subTest(case=row['case']):
                trace=json.loads((base/row['case']/'trace.json').read_text())
                text=(base/row['case']/'native-result.txt').read_bytes().decode('utf-8')
                self.assertEqual(len(validate_native_run(trace,text,row['work_type'],row['file_type'])),row['diagnostic_count'])
                with self.assertRaises(ValueError):validate_native_run(trace,text,'master' if row['work_type']=='phd' else 'phd',row['file_type'])
                with self.assertRaises(ValueError):validate_native_run(trace,text,row['work_type'],'docx' if row['file_type']=='pdf' else 'pdf')
    def test_forged_mode_and_threshold_rejected(self):
        trace,text=self.run_record('native-volume-g_chars43200-r3')
        selection=next(h['volume_state'] for h in trace['breakpoint_hits'] if h['label']=='volume_selected_threshold')
        selection['minimum']=0
        with self.assertRaises(ValueError):validate_native_run(trace,text)
    def test_probe_hash_and_cleanup_failures_rejected(self):
        trace,text=self.run_record('native-volume-g_chars43200-r3')
        with self.assertRaises(ValueError):validate_native_run(trace,text,source_sha256='0'*64)
        trace['cleanup_errors']=['owned process still running']
        with self.assertRaises(ValueError):validate_native_run(trace,text)
    def test_complex_phd_and_historical_difference_preserved(self):
        base=ROOT/'evidence/business-map-232/native-complex-phd-r1'
        matrix=json.loads((base/'matrix.json').read_text(encoding='utf-8'))
        for row in matrix['cases']:
            trace=json.loads((base/row['case']/'trace.json').read_text(encoding='utf-8'))
            text=(base/row['case']/'native-result.txt').read_bytes().decode('utf-8')
            self.assertEqual(len(validate_native_run(trace,text,'phd','docx')),row['diagnostic_count'])
            self.assertNotIn('volume_insufficient_emit',{h['label'] for h in trace['breakpoint_hits']})
        audit=json.loads((ROOT/'evidence/business-map-232/native-modes-audit-r1/audit.json').read_text(encoding='utf-8'))
        differences=[r['case'] for r in audit['cases'] if r.get('historical_build230_comparison',{}).get('normalized_full_diagnostics_equal') is False]
        self.assertEqual(differences,['phd_complex_image'])

if __name__=='__main__':unittest.main()

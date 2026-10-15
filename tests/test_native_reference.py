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
        self.assertEqual(tool['inputSchema']['properties']['work_type']['enum'],['master'])
        with self.assertRaises(ValueError):server.handle_tool_call({'name':'check_native_reference_experimental','arguments':{'work_type':'phd'}})

if __name__=='__main__':unittest.main()

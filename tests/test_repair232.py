import sys,tempfile,json,zipfile,hashlib,unittest,subprocess
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/testvkr-service')]
from repair_document import repair_copy
import repair_build232

class Repair232Tests(unittest.TestCase):
    def test_complex_copy_exactly_matches_native_validated_candidate(self):
        base=ROOT/'evidence/v028/complex-repair'
        with tempfile.TemporaryDirectory() as td:
            for id in ['C01','C02','C03']:
                source=base/(id+'B.docx');raw=source.read_bytes()
                preview=repair_copy(source,actions=['font_size_anomalies'],body_font_pt=14,work_type='master',dry_run=True,native_build=232)
                result=repair_copy(source,td,actions=['font_size_anomalies'],body_font_pt=14,work_type='master',native_build=232,expected_input_sha256=preview['input_sha256'])
                self.assertEqual(preview['plan_id'],result['plan_id'])
                self.assertEqual(raw,source.read_bytes())
                with zipfile.ZipFile(result['output_file']) as actual,zipfile.ZipFile(base/(id+'A.docx')) as expected:
                    self.assertEqual(actual.namelist(),expected.namelist())
                    for n in actual.namelist():self.assertEqual(actual.read(n),expected.read(n),n)
                self.assertEqual(result['recheck_build'],232)
                self.assertTrue(Path(result['change_log']).is_file())
                self.assertEqual(len(result['changes']),0 if id=='C03' else 1)
    def test_unvalidated_actions_and_modes_are_closed(self):
        source=ROOT/'evidence/v028/complex-repair/C01B.docx'
        for action,mode,target in [('page_size_a4','master',14),('text_color_black','master',14),('font_size_anomalies','phd',14),('font_size_anomalies','master',12)]:
            with self.assertRaises(ValueError):repair_copy(source,actions=[action],body_font_pt=target,work_type=mode,dry_run=True,native_build=232)
    def test_modified_acceptance_evidence_disables_capability(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);out=root/'evidence/v028/complex-repair';out.mkdir(parents=True)
            (out/'acceptance.json').write_text(json.dumps({'enabled':True,'build':232,'actions':['font_size_anomalies'],'implementation_sha256':hashlib.sha256(Path(repair_build232.__file__).read_bytes()).hexdigest(),'evidence_hashes':{'evidence/proof.txt':'wrong'}}))
            (root/'evidence/proof.txt').write_text('changed')
            with patch.object(repair_build232,'ROOT',root):self.assertFalse(repair_build232.capability()['enabled'])
    def test_cli_new_plan_apply_and_mcp_capability(self):
        cli=[sys.executable,str(ROOT/'scripts/thesis_cli.py')];source=ROOT/'evidence/v028/complex-repair/C01B.docx'
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'plan.json'
            result=subprocess.run(cli+['--out',str(p),'plan',str(source),'--native-build','232','--work-type','master','--actions','font_size_anomalies','--body-font-pt','14'],capture_output=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            result=subprocess.run(cli+['apply',str(source),'--plan',str(p),'--output-dir',td],capture_output=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(json.loads(result.stdout)['native_build'],232)

if __name__=='__main__':unittest.main()

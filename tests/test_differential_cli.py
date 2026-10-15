"""Synthetic-only tests for differential family comparison and cached runs."""
from __future__ import annotations

from contextlib import ExitStack
from io import BytesIO
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import differential_cli as cli  # noqa: E402
from differential_mutations import ddmin  # noqa: E402

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def minimal_docx():
    out = BytesIO()
    xml = f'<w:document xmlns:w="{W}"><w:body><w:p><w:r><w:t>seed</w:t></w:r></w:p><w:sectPr/></w:body></w:document>'.encode()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr('word/document.xml', xml)
    return out.getvalue()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class DifferentialComparisonTests(unittest.TestCase):
    def test_comparison_counts_diagnostic_families_not_text_characters_and_limits_focus(self):
        def parser(text, _fmt):
            if 'A:' in text:
                return [{'rule_id': 'Rule.A'}]
            if 'B:' in text:
                return [{'rule_id': 'Rule.B'}]
            return []

        local = {'findings': [
            {'rule_id': 'Rule.A', 'message': 'short'},
            {'rule_id': 'Rule.A', 'message': 'a very long different message'},
            {'rule_id': 'Rule.B', 'message': 'unselected local-only family'},
        ]}
        native = {'diagnostics': [
            {'message': 'A: x'}, {'message': 'A: completely different text'},
        ]}
        with patch('compare_native_trial.parse_diagnostics', side_effect=parser):
            result = cli.compare_families(local, native, ['Rule.A'])
        self.assertEqual(result['status'], 'selected_families_equal')
        self.assertEqual(result['pairs'], [{'rule_id': 'Rule.A', 'native_message_count': 2, 'local_finding_count': 2, 'different': False}])
        self.assertIn('not affected-character', result['limits'])
        self.assertIn('semantic equivalence', result['limits'])

    def test_minimization_claim_is_scoped_to_preserving_family_counts(self):
        raw = minimal_docx()
        target = [{'rule_id': 'Rule.A', 'native_message_count': 1,
                   'local_finding_count': 0, 'different': True}]
        temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(temp.cleanup)
        out = Path(temp.name) / 'private_trials'
        out.mkdir()
        fake_runner = types.SimpleNamespace(out=out, evaluate=lambda _candidate: {
            'status': 'family_difference', 'differences': target,
        })
        result = cli.minimize(fake_runner, raw, {'differences': target}, 20)
        self.assertEqual(result['status'], 'certified_1minimal')
        self.assertEqual(result['target_difference'], target)
        self.assertIn('paragraphs only', result['reduction_scope'])
        self.assertIn('not globally minimal or property-minimal', result['reduction_scope'])
        self.assertNotIn('same semantic cause', result['reduction_scope'])

    def test_unmapped_native_message_cannot_be_silently_reported_as_family_agreement(self):
        local = {'findings': []}
        native = {'diagnostics': [{'message': 'unparseable native wording'}]}
        with patch('compare_native_trial.parse_diagnostics', return_value=[]):
            result = cli.compare_families(local, native, ['Rule.A'])
        self.assertNotEqual(result['status'], 'selected_families_equal')
        self.assertEqual(len(result['unmapped_native_diagnostics']), 1)

    def test_minimizer_does_not_accept_unresolved_or_invalid_as_mismatch(self):
        calls = []
        def unresolved_on_reduction(candidate):
            calls.append(candidate)
            if len(candidate) == 3:
                return True
            return None
        result = ddmin(('p0', 'p1', 'p2'), unresolved_on_reduction, 20)
        self.assertEqual(result['status'], 'unresolved')
        self.assertEqual(result['items'], ['p0', 'p1', 'p2'])
        self.assertGreater(result['unresolved_evaluations'], 0)
        self.assertNotEqual(result['status'], 'certified_1minimal')


class DifferentialCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        tmp = Path(self.temp.name)
        self.private = tmp / 'private_trials'
        self.private.mkdir()
        self.out = self.private / 'campaign'
        self.exe = tmp / 'fake-native.exe'
        self.exe.write_bytes(b'synthetic executable identity')
        self.executable_sha = sha(self.exe.read_bytes())
        self.raw = minimal_docx()
        self.local = {
            'source_sha256': sha(self.raw), 'work_type': 'master',
            'findings': [{'rule_id': 'Rule.A'}, {'rule_id': 'Rule.B'}, {'rule_id': 'Rule.B'}],
        }
        self.native = {
            'source_sha256': sha(self.raw), 'work_type': 'master', 'source_unchanged': True,
            'diagnostics': [{'message': 'A: one'}, {'message': 'B: one'}],
        }
        self.trace = {'synthetic': True}
        self.native_text = b'synthetic result'

        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(cli, 'PRIVATE', self.private))
        fake_native = types.ModuleType('native_reference_cli')
        fake_native.IDENTITY = self.executable_sha
        fake_native.validate_native_run = lambda *_args, **_kw: self.native['diagnostics']
        self.stack.enter_context(patch.dict(sys.modules, {'native_reference_cli': fake_native}))
        fake_check = types.ModuleType('check_document')
        fake_check.settings = types.SimpleNamespace(model_dump=lambda **_kw: {'synthetic': True})
        fake_check.check_file = lambda *_args, **_kw: dict(self.local)
        self.stack.enter_context(patch.dict(sys.modules, {'check_document': fake_check}))
        from compare_native_trial import PATTERNS
        self.stack.enter_context(patch('compare_native_trial.PATTERNS', {
            **PATTERNS, 'Rule.A': r'A:', 'Rule.B': r'B:'
        }))

    def _runner(self, focus=('Rule.A',)):
        return cli.Runner(self.out, self.exe, 'master', list(focus), max_native_runs=2)

    def _seed_cache(self, runner, *, omit_hashes=False, corrupt_identity=False):
        identity = {**runner.identity, 'input_sha256': sha(self.raw)}
        key = sha(json.dumps(identity, sort_keys=True).encode())
        folder = runner.out / 'cache' / key
        (folder / 'native' / 'native').mkdir(parents=True)
        (folder / 'input.docx').write_bytes(self.raw)
        cli.write_json(folder / 'native' / 'report.json', self.native)
        cli.write_json(folder / 'local.json', self.local)
        cli.write_json(folder / 'native' / 'native' / 'trace.json', self.trace)
        (folder / 'native' / 'native' / 'native-result.txt').write_bytes(self.native_text)
        files = {p.relative_to(folder).as_posix(): sha(p.read_bytes()) for p in folder.rglob('*') if p.is_file()}
        cache_identity = dict(identity)
        if corrupt_identity:
            cache_identity['mode'] = 'phd'
        cli.write_json(folder / 'cache.json', {'identity': cache_identity, 'files': {} if omit_hashes else files})
        return folder

    def test_focus_is_recomputed_on_verified_raw_cache_and_mode_changes_cache_identity(self):
        from compare_native_trial import parse_diagnostics
        def parser(text, _fmt):
            if 'A:' in text: return [{'rule_id': 'Rule.A'}]
            if 'B:' in text: return [{'rule_id': 'Rule.B'}]
            return []
        with patch('compare_native_trial.parse_diagnostics', side_effect=parser):
            runner_a = self._runner(('Rule.A',))
            self._seed_cache(runner_a)
            result_a = runner_a.evaluate(self.raw)
            runner_b = self._runner(('Rule.B',))
            result_b = runner_b.evaluate(self.raw)
        self.assertEqual(result_a['status'], 'selected_families_equal')
        self.assertEqual(result_b['status'], 'family_difference')
        self.assertEqual(runner_b.cache_hits, 1)
        runner_phd = cli.Runner(self.out, self.exe, 'phd', ['Rule.A'], max_native_runs=2)
        self.assertNotEqual(runner_phd.identity, runner_a.identity)
        self.assertEqual(runner_b.identity, runner_a.identity)  # focus scopes comparison, not raw report cache

    def test_cache_rejects_wrong_identity_and_incomplete_artifact_hash_manifest(self):
        runner = self._runner()
        folder = self._seed_cache(runner, corrupt_identity=True)
        with self.assertRaisesRegex(ValueError, 'Cache identity mismatch'):
            runner.evaluate(self.raw)
        cache = cli.read_json(folder / 'cache.json')
        correct_identity = {**runner.identity, 'input_sha256': sha(self.raw)}
        cli.write_json(folder / 'cache.json', {'identity': correct_identity, 'files': {}})
        with self.assertRaises(ValueError):
            runner.evaluate(self.raw)
        cli.write_json(folder / 'cache.json', {'identity': correct_identity, 'files': cache['files']})
        (folder / 'input.docx').write_bytes(b'tampered cache artifact')
        with self.assertRaisesRegex(ValueError, 'Cache artifact hash mismatch'):
            runner.evaluate(self.raw)


if __name__ == '__main__':
    unittest.main()

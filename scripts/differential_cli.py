"""Bounded private differential runner; original-program agreement is not compliance."""
import argparse
from argparse import Namespace
from collections import Counter
import hashlib
import json
import os
import platform
import locale
from importlib import metadata
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT.parent / 'private_trials'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_bytes())


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def source_identity():
    files = sorted({p for suffix in ('*.py', '*.json', '*.cs') for p in (ROOT / 'scripts').rglob(suffix)})
    return digest(json.dumps([(p.relative_to(ROOT).as_posix(), digest(p.read_bytes()))
                              for p in files], separators=(',', ':')).encode())


def compare_families(local, native, focus):
    from compare_native_trial import parse_diagnostics
    # Parse each complete numbered diagnostic independently; preserve unmapped text.
    mapped = []
    for row in native['diagnostics']:
        found = parse_diagnostics('1. ' + row['message'], 'docx')
        rule = found[0]['rule_id'] if len(found) == 1 else None
        # Auxiliary, literal-family labels only; these are not registered school rules.
        if rule is None:
            auxiliary = {'Native.MissingTitlePage': 'Отсутствует титульный лист',
                         'Native.StructureUnknown': 'Не определена структура документа',
                         'Native.TocPageNumbersMissing': 'В содержании отсутствуют номера страниц'}
            matches = [key for key, fragment in auxiliary.items() if fragment in row['message']]
            rule = matches[0] if len(matches) == 1 else None
        mapped.append({**row, 'rule_id': rule})
    native_counts = Counter(d['rule_id'] for d in mapped if d['rule_id'])
    local_counts = Counter(f['rule_id'] for f in local['findings'])
    pairs = [{'rule_id': rule, 'native_message_count': native_counts[rule],
              'local_finding_count': local_counts[rule],
              'different': native_counts[rule] != local_counts[rule]} for rule in sorted(set(focus))]
    differences = [p for p in pairs if p['different']]
    unmapped = [d for d in mapped if d['rule_id'] is None]
    return {'status': 'mapping_incomplete' if unmapped else 'family_difference' if differences else 'selected_families_equal',
            'pairs': pairs, 'differences': differences,
            'unmapped_native_diagnostics': unmapped,
            'limits': 'Message/finding group counts only; not affected-character, occurrence, semantic equivalence or school compliance. Unselected families are not assessed.'}


class Runner:
    def __init__(self, out, executable, mode, focus, max_native_runs=20):
        from native_reference_cli import IDENTITY
        self.out = Path(os.path.abspath(out)).resolve()
        if not self.out.is_relative_to(PRIVATE.resolve()):
            raise ValueError('Full inputs/reports must remain under private_trials')
        self.out.mkdir(parents=True, exist_ok=True)
        self.exe = Path(executable).resolve()
        if digest(self.exe.read_bytes()) != IDENTITY:
            raise ValueError('Unsupported executable')
        if mode not in {'master', 'phd'} or not focus or any(not isinstance(x, str) for x in focus):
            raise ValueError('Explicit supported mode and nonempty focus rules required')
        from compare_native_trial import PATTERNS
        manual = {'Graduate.RequiredHeadingsMissing', 'Graduate.AbstractTooShort', 'Graduate.TocEmpty',
                  'Graduate.TocSmall', 'Struct.EmptyStructuralElement', 'Struct.SmallStructuralElement',
                  'Graduate.ThesisSizeTooSmall'}
        if set(focus) - (set(PATTERNS) | manual):
            raise ValueError('Focus contains diagnostic families without a native mapping')
        self.mode, self.focus, self.limit = mode, sorted(set(focus)), max_native_runs
        from check_document import settings
        # Hash effective parser/checker settings, without publishing environment values.
        config = settings.model_dump(mode='json')
        packages = {}
        for package in ('python-docx', 'lxml', 'pydantic', 'pydantic-settings', 'PyMuPDF', 'Pillow'):
            try:
                packages[package] = metadata.version(package)
            except metadata.PackageNotFoundError:
                packages[package] = None
        self.identity = {'schema': 1, 'mode': mode, 'format': 'docx',
                         'executable_sha256': IDENTITY, 'sources_sha256': source_identity(),
                         'effective_settings_sha256': digest(json.dumps(config, sort_keys=True, default=str).encode()),
                         'python': sys.version, 'platform': platform.platform(),
                         'machine_sha256': digest(platform.node().encode()),
                         'locale': locale.getlocale(), 'dependencies': packages}
        # Keep JSON round-trip equality for cached identities (locale tuple -> list).
        self.identity = json.loads(json.dumps(self.identity))
        self.executed, self.cache_hits = 0, 0

    def evaluate(self, raw):
        from check_document import check_file
        from native_reference_cli import validate_native_run
        from differential_mutations import validate_docx
        validate_docx(raw)
        if source_identity() != self.identity['sources_sha256']:
            raise ValueError('Source changed during campaign; start a new campaign')
        identity = {**self.identity, 'input_sha256': digest(raw)}
        key = digest(json.dumps(identity, sort_keys=True).encode())
        folder = self.out / 'cache' / key
        cache_path = folder / 'cache.json'
        if cache_path.exists():
            cache = read_json(cache_path)
            if cache['identity'] != identity:
                raise ValueError('Cache identity mismatch')
            retained = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p != cache_path}
            required = {'input.docx', 'local.json', 'native/report.json',
                        'native/native/trace.json', 'native/native/native-result.txt'}
            if set(cache.get('files', {})) != retained or not required <= retained:
                raise ValueError('Incomplete cache artifact manifest')
            for name, wanted in cache['files'].items():
                path = (folder / name).resolve()
                if not path.is_relative_to(folder.resolve()) or digest(path.read_bytes()) != wanted:
                    raise ValueError('Cache artifact hash mismatch')
            native, local = read_json(folder / 'native/report.json'), read_json(folder / 'local.json')
            self.cache_hits += 1
        else:
            if self.executed >= self.limit:
                return {'status': 'budget_exhausted', 'input_sha256': identity['input_sha256']}
            if folder.exists():
                raise ValueError('Incomplete cache directory; inspect failure, do not silently reuse')
            folder.mkdir(parents=True)
            source = folder / 'input.docx'
            source.write_bytes(raw)
            self.executed += 1
            args = [sys.executable, '-X', 'utf8', str(ROOT / 'scripts/native_reference_cli.py'),
                    '--input', str(source), '--native-exe', str(self.exe), '--work-type', self.mode,
                    '--timeout', '25', '--out', str(folder / 'native')]
            result = subprocess.run(args, capture_output=True)
            (folder / 'stdout.log').write_bytes(result.stdout)
            (folder / 'stderr.log').write_bytes(result.stderr)
            if result.returncode:
                return {'status': 'native_execution_failed', 'input_sha256': identity['input_sha256'],
                        'evidence_directory': str(folder), 'exit_code': result.returncode}
            native = read_json(folder / 'native/report.json')
            options = Namespace(work_type=self.mode, native_build=232, document_kind='auto',
                                template_id=None, skip_structure=False, skip_pictures=False,
                                skip_word_format=False, skip_dictionary=False)
            try:
                local = check_file(source, options)
                if local['source_sha256'] != identity['input_sha256']:
                    raise ValueError('Local source changed')
                write_json(folder / 'local.json', local)
            except Exception as exc:
                return {'status': 'local_execution_failed', 'error': str(exc),
                        'evidence_directory': str(folder), 'input_sha256': identity['input_sha256']}
        native_dir = folder / 'native'
        trace = read_json(native_dir / 'native/trace.json')
        diagnostics = validate_native_run(trace, (native_dir / 'native/native-result.txt').read_bytes().decode('utf8'),
                                         self.mode, 'docx', identity['input_sha256'], True)
        if (native.get('source_sha256') != identity['input_sha256'] or native.get('diagnostics') != diagnostics
                or native.get('work_type') != self.mode or not native.get('source_unchanged')
                or local.get('source_sha256') != identity['input_sha256']
                or local.get('work_type') != self.mode or (folder / 'input.docx').read_bytes() != raw):
            raise ValueError('Native/local retained report identity mismatch')
        if not cache_path.exists():
            files = [p for p in folder.rglob('*') if p.is_file()]
            write_json(cache_path, {'identity': identity,
                                  'files': {p.relative_to(folder).as_posix(): digest(p.read_bytes()) for p in files}})
        comparison = compare_families(local, native, self.focus)
        return {**comparison, 'input_sha256': identity['input_sha256'], 'evidence_directory': str(folder),
                'native_trace_sha256': digest((native_dir / 'native/trace.json').read_bytes())}


def minimize(runner, raw, difference, max_evaluations):
    from differential_mutations import ddmin, paragraph_atoms, retain_paragraphs
    if not difference.get('differences'):
        raise ValueError('Minimization needs a completed selected-family difference')
    target = difference['differences']
    observed = []

    def persists(ids):
        try:
            result = runner.evaluate(retain_paragraphs(raw, ids))
        except Exception as exc:
            observed.append({'status': 'unresolved', 'error': str(exc)})
            return None
        observed.append(result)
        if result['status'] not in {'family_difference', 'selected_families_equal'}:
            return None
        return result['differences'] == target

    reduced = ddmin(paragraph_atoms(raw), persists, max_evaluations=max_evaluations)
    candidate = retain_paragraphs(raw, reduced['items'])
    path = runner.out / ('minimized-' + digest(raw)[:16] + '-' + digest(candidate)[:16] + '.docx')
    if path.exists() and path.read_bytes() != candidate:
        raise ValueError('Existing minimized artifact differs; use a fresh output directory')
    path.write_bytes(candidate)
    return {**reduced, 'document': str(path), 'sha256': digest(candidate),
            'target_difference': target, 'evaluations_detail': observed,
            'reduction_scope': 'word/document.xml paragraphs only; not globally minimal or property-minimal'}


def run(spec_path, out, executable, max_cases=8, max_native_runs=20, minimize_evaluations=0):
    from differential_mutations import mutate_docx
    spec_path = Path(spec_path).resolve()
    spec = read_json(spec_path)
    seed = Path(spec['seed'])
    seed = seed if seed.is_absolute() else spec_path.parent / seed
    raw = seed.read_bytes()
    if spec.get('seed_sha256') != digest(raw):
        raise ValueError('Specification must pin the seed SHA256')
    if not 1 <= max_cases <= 1000 or not 1 <= max_native_runs <= 5000 or not 0 <= minimize_evaluations <= 500:
        raise ValueError('Invalid bounded execution limits')
    runner = Runner(out, executable, spec['work_type'], spec['focus_rules'], max_native_runs)
    manifest = runner.out / 'campaign.json'
    campaign = {'spec_sha256': digest(spec_path.read_bytes()), 'seed_sha256': digest(raw),
                'identity': runner.identity, 'focus_rules': runner.focus}
    if manifest.exists() and read_json(manifest) != campaign:
        raise ValueError('Output belongs to another campaign/configuration')
    write_json(manifest, campaign)
    run_directory = runner.out / 'runs' / uuid.uuid4().hex
    run_directory.mkdir(parents=True)
    snapshots = run_directory / 'sources'
    snapshots.mkdir()
    for name in ('differential_cli.py', 'differential_mutations.py'):
        (snapshots / (name + '.txt')).write_bytes((ROOT / 'scripts' / name).read_bytes())
    results = []
    mutations = [None, *spec.get('mutations', [])]
    for index, mutation in enumerate(mutations[:max_cases]):
        candidate = raw if mutation is None else mutate_docx(raw, mutation)
        try:
            result = runner.evaluate(candidate)
        except Exception as exc:
            result = {'status': 'unresolved', 'error': str(exc), 'input_sha256': digest(candidate)}
        row = {'index': index, 'mutation': mutation, 'result': result}
        results.append(row)
        write_json(run_directory / 'results.private.json', results)
        write_json(runner.out / 'results.private.json', results)
        if result['status'] == 'family_difference' and minimize_evaluations and not any('minimization' in x for x in results[:-1]):
            row['minimization'] = minimize(runner, candidate, result, minimize_evaluations)
            write_json(run_directory / 'results.private.json', results)
            write_json(runner.out / 'results.private.json', results)
        if result['status'] == 'budget_exhausted':
            break
    if seed.read_bytes() != raw:
        raise ValueError('Seed changed during campaign')
    summary = {'status': 'bounded_campaign_finished', 'cases': len(results),
               'available_cases': len(mutations), 'case_limit_truncated': len(results) < len(mutations),
               'outcomes': dict(Counter(x['result']['status'] for x in results)),
               'fresh_native_runs': runner.executed, 'verified_cache_hits': runner.cache_hits,
               'seed_unchanged': True, 'repair_or_rule_promotion': False,
               'run_directory': str(run_directory),
               'limits': 'Selected family message counts only; failures unresolved; not school correctness, accuracy or branch coverage.'}
    write_json(runner.out / 'summary.json', summary)
    write_json(run_directory / 'summary.json', summary)
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--native-exe', type=Path, default=ROOT.parent / 'runtime/TestVkr232.exe')
    p.add_argument('--max-cases', type=int, default=8)
    p.add_argument('--max-native-runs', type=int, default=20)
    p.add_argument('--minimize-evaluations', type=int, default=0)
    a = p.parse_args()
    print(json.dumps(run(a.spec, a.out, a.native_exe, a.max_cases, a.max_native_runs, a.minimize_evaluations)))


if __name__ == '__main__':
    main()

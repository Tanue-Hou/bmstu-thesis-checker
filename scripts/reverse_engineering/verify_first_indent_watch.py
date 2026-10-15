"""Run/validate retained native first/left counter watches against manifest cases."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT.parent
MANIFEST = ROOT / 'evidence/business-map-232/first-indent-watch-inputs-r1/manifest.json'
CLI = ROOT / 'scripts/native_reference_cli.py'
DEFAULT_SEEDS = (
    PROJECT / 'private_trials/first-watch-calibration-r1',
    PROJECT / 'private_trials/first-watch-pdf-mp-r1',
)

sys.path.insert(0, str(ROOT / 'scripts'))
from native_reference_cli import IDENTITY, validate_counter_watch, validate_native_run
from reverse_engineering.verify_native_pixels import publish as publish_native_artifacts


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def within(root, path):
    path = Path(path).resolve()
    try:
        path.relative_to(Path(root).resolve())
    except ValueError as exc:
        raise ValueError(f'Path must remain under {root}: {path}') from exc
    return path


def project_path(value):
    path = Path(value)
    return within(PROJECT, path if path.is_absolute() else PROJECT / path)


def normalize_diagnostics(rows):
    return [re.sub(r'\s+', ' ', row['message']).strip() for row in rows]


def seed_artifacts(seed, row):
    seed = project_path(seed)
    source = seed / ('input.' + Path(row['input']).suffix.lower().lstrip('.'))
    report_path = seed / 'report.json'
    trace_path = seed / 'native/trace.json'
    text_path = seed / 'native/native-result.txt'
    if not all(p.is_file() for p in (source, report_path, trace_path, text_path)):
        return None
    report = json.loads(report_path.read_text(encoding='utf-8'))
    if report.get('source_sha256') != row['input_sha256'] or report.get('work_type') != row['mode']:
        return None
    return {
        'kind': 'seed', 'directory': seed, 'source': source,
        'report_path': report_path, 'trace_path': trace_path, 'text_path': text_path,
    }


def find_seed(seeds, row):
    found = [item for seed in seeds if (item := seed_artifacts(seed, row)) is not None]
    if len(found) > 1:
        raise ValueError(f'Multiple seeds match case {row["case"]}: {[str(x["directory"]) for x in found]}')
    return found[0] if found else None


def run_case(row, seeds, private_run_root, native_timeout, process_timeout):
    seed = find_seed(seeds, row)
    if seed is not None:
        return seed

    case_dir = within(PROJECT / 'private_trials', private_run_root / row['case'])
    source = within(ROOT, ROOT / row['input'])
    command = [
        sys.executable, str(CLI), '--input', str(source), '--watch-first-counter',
        '--work-type', row['mode'], '--timeout', str(native_timeout), '--out', str(case_dir),
    ]
    execution = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
                               timeout=process_timeout)
    if execution.returncode != 0:
        failure = {'status': 'failed_native_reference_cli', 'case': row['case'],
                   'returncode': execution.returncode,
                   'stdout': execution.stdout[-2000:], 'stderr': execution.stderr[-4000:]}
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / 'verification-failure.json').write_text(
            json.dumps(failure, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        raise RuntimeError(f'Native CLI failed for {row["case"]}; retained output at {case_dir}')
    artifacts = {
        'kind': 'fresh', 'directory': case_dir, 'source': case_dir / ('input.' + Path(row['input']).suffix.lower().lstrip('.')),
        'report_path': case_dir / 'report.json', 'trace_path': case_dir / 'native/trace.json',
        'text_path': case_dir / 'native/native-result.txt',
    }
    if not all(p.is_file() for p in (artifacts['source'], artifacts['report_path'], artifacts['trace_path'], artifacts['text_path'])):
        raise RuntimeError(f'CLI returned success but publish artifacts are incomplete for {row["case"]}: {case_dir}')
    return artifacts


def verify_reference_files(row):
    source = within(ROOT, ROOT / row['input'])
    if sha(source) != row['input_sha256']:
        raise ValueError(f'Input SHA mismatch for {row["case"]}')
    capture = within(ROOT, ROOT / row['capture'])
    resolved = {}
    for name in ('trace', 'report', 'matrix'):
        ref = row[name]
        path = within(ROOT, ROOT / ref['path'])
        if sha(path) != ref['sha256']:
            raise ValueError(f'Manifest {name} SHA mismatch for {row["case"]}')
        resolved[name] = path
    baseline_text = capture / 'native-result.txt'
    if not baseline_text.is_file():
        raise FileNotFoundError(baseline_text)
    baseline_report = json.loads(resolved['report'].read_text(encoding='utf-8'))
    actual = {
        'trace_sha256': sha(resolved['trace']),
        'native_text_sha256': sha(baseline_text),
        'source_sha256': sha(source),
    }
    for field, actual_hash in actual.items():
        if baseline_report.get(field) != actual_hash:
            raise ValueError(f'Baseline report {field} mismatch for {row["case"]}')
    if baseline_report.get('work_type') != row['mode']:
        raise ValueError(f'Baseline report mode mismatch for {row["case"]}')
    return source, capture, baseline_text, resolved['trace']


def verify_case(row, artifacts):
    source, capture, baseline_text_path, baseline_trace_path = verify_reference_files(row)
    own_source = artifacts['source']
    if sha(own_source) != row['input_sha256']:
        raise ValueError(f'Published source SHA mismatch for {row["case"]}')
    report = json.loads(artifacts['report_path'].read_text(encoding='utf-8'))
    trace = json.loads(artifacts['trace_path'].read_text(encoding='utf-8'))
    native_text = artifacts['text_path'].read_bytes().decode('utf-8')
    baseline_text = baseline_text_path.read_bytes().decode('utf-8')
    file_type = source.suffix.lower().lstrip('.')
    diagnostics = validate_native_run(trace, native_text, row['mode'], file_type,
                                      row['input_sha256'], True)
    watch_receipt = validate_counter_watch(trace)
    baseline_diagnostics = validate_native_run(
        json.loads(baseline_trace_path.read_text(encoding='utf-8')),
        baseline_text, row['mode'], file_type, row['input_sha256'], True)
    current_normalized = normalize_diagnostics(diagnostics)
    baseline_normalized = normalize_diagnostics(baseline_diagnostics)
    same_full_report = current_normalized == baseline_normalized

    if (report.get('status') != 'completed_instrumented_native_reference'
            or report.get('native_build') != 232
            or report.get('executable_sha256') != IDENTITY
            or report.get('source_sha256') != row['input_sha256']
            or report.get('work_type') != row['mode']
            or report.get('source_unchanged') is not True
            or report.get('trace_sha256') != sha(artifacts['trace_path'])
            or report.get('native_text_sha256') != sha(artifacts['text_path'])):
        raise ValueError(f'Published report identity mismatch for {row["case"]}')
    expected_counters = row.get('native_counters')
    final_values = watch_receipt['final_values']
    if expected_counters is not None:
        for field in ('first', 'left'):
            if final_values[field] != expected_counters[field]:
                raise ValueError(f'Watch final {field} value differs from retained native counter for {row["case"]}')

    return {
        'case': row['case'], 'format': file_type, 'mode': row['mode'],
        'source_sha256': row['input_sha256'], 'artifact_kind': artifacts['kind'],
        'artifact_directory': artifacts['directory'].relative_to(PROJECT).as_posix(),
        'report': artifacts['report_path'].relative_to(PROJECT).as_posix(),
        'report_sha256': sha(artifacts['report_path']),
        'trace': artifacts['trace_path'].relative_to(PROJECT).as_posix(),
        'trace_sha256': sha(artifacts['trace_path']),
        'source_copy': own_source.relative_to(PROJECT).as_posix(),
        'native_diagnostic_count': len(diagnostics),
        'baseline_diagnostic_count': len(baseline_diagnostics),
        'normalized_full_diagnostics_sha256': hashlib.sha256(
            json.dumps(current_normalized, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest(),
        'same_full_report': same_full_report,
        'watch': watch_receipt,
        'baseline_capture': capture.relative_to(PROJECT).as_posix(),
        'baseline_native_text_sha256': sha(baseline_text_path),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True,
                        help='Fresh public receipt directory within implementation/evidence.')
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument('--seed', type=Path, action='append', default=[],
                        help='Reusable native-reference private directory; may be repeated.')
    parser.add_argument('--native-timeout', type=int, default=30)
    parser.add_argument('--process-timeout', type=int, default=60)
    args = parser.parse_args()
    if not 5 <= args.native_timeout <= 30:
        raise ValueError('native-timeout must be between 5 and 30 seconds')

    out = within(ROOT / 'evidence', ROOT / args.out if not args.out.is_absolute() else args.out)
    out.mkdir(parents=True, exist_ok=False)
    private_run_root = PROJECT / 'private_trials' / out.name
    private_run_root.mkdir(parents=True, exist_ok=False)
    manifest_path = within(ROOT, args.manifest if args.manifest.is_absolute() else ROOT / args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('target_exe_sha256') != IDENTITY:
        raise ValueError('Manifest target executable identity differs from native_reference_cli')
    rows = manifest.get('docx_inputs', []) + manifest.get('pdf_inputs', [])
    expected = {
        ('noFirst', 'cf82372ebf5c530c081ef05df2d5dccc44f56ed8a044017b5ae913ee54101b84'),
        ('firstOneInch', '292b90ebf4877a382b7c10b4ccbae5c00e1754d533da1815ce1efa192da3be97'),
        ('negativeLeft_positive_writer_control', 'a8a6de4dd882d6924e5bc3e38c467e25ce8e880fc7dbc4119d5444756027226a'),
        ('pdf_one_page_pixel_boundary_baseline', 'd85f85d5a38268add142601ad453aae9100d59a61556dc39c1cb2bdd6a6a9892'),
        ('mp_clean_three_page_control', 'a0815ebc8b37789c8982d037b6b8bbce929730122cc66e324a36c9289b713205'),
        ('structure_clean_fourteen_page_control', '5272656dcc7a90fb2eb487851d67e7a9a0e347b84b9cf259647b58d8abbd26d6'),
    }
    if {(row.get('case'), row.get('input_sha256')) for row in rows} != expected:
        raise ValueError('Manifest cases differ from the six fixed synthetic watch inputs')
    if any(Path(row['input']).suffix.lower() not in ('.docx', '.pdf') for row in rows):
        raise ValueError('Manifest contains a non-DOCX/PDF input')

    seeds = []
    for seed in (*DEFAULT_SEEDS, *args.seed):
        path = project_path(seed)
        if path not in seeds:
            seeds.append(path)
    required_seed_hashes = {
        'a8a6de4dd882d6924e5bc3e38c467e25ce8e880fc7dbc4119d5444756027226a',
        'a0815ebc8b37789c8982d037b6b8bbce929730122cc66e324a36c9289b713205',
    }
    all_input_hashes = {row['input_sha256'] for row in rows}
    if not required_seed_hashes.issubset(all_input_hashes):
        raise ValueError('Manifest no longer includes both seed cases; refusing to proceed')
    for required_hash in required_seed_hashes:
        matching = [row for row in rows if row['input_sha256'] == required_hash]
        if len(matching) != 1 or find_seed(seeds, matching[0]) is None:
            raise ValueError(f'Required reusable seed for {required_hash} is unavailable; refusing to rerun that input')

    results = []
    current_case = None
    current_artifacts = None
    try:
        for row in rows:
            current_case = row['case']
            artifacts = run_case(row, seeds, private_run_root, args.native_timeout, args.process_timeout)
            current_artifacts = artifacts
            result = verify_case(row, artifacts)
            if not result['same_full_report']:
                raise ValueError(f'Normalized full diagnostics differ from retained capture for {row["case"]}')
            published_dir = within(out, out / row['case'])
            published = publish_native_artifacts(artifacts['directory'], published_dir)
            published_source = published_dir / ('input.' + Path(row['input']).suffix.lower().lstrip('.'))
            shutil.copyfile(artifacts['source'], published_source)
            result['published'] = {
                'directory': published_dir.relative_to(ROOT).as_posix(),
                'report': (published_dir / 'report.json').relative_to(ROOT).as_posix(),
                'report_sha256': sha(published_dir / 'report.json'),
                'trace': (published_dir / 'trace.json').relative_to(ROOT).as_posix(),
                'trace_sha256': sha(published_dir / 'trace.json'),
                'native_text': (published_dir / 'native-result.txt').relative_to(ROOT).as_posix(),
                'native_text_sha256': sha(published_dir / 'native-result.txt'),
                'source': published_source.relative_to(ROOT).as_posix(),
                'source_sha256': sha(published_source),
            }
            if published.get('source_sha256') != row['input_sha256']:
                raise ValueError(f'Published report source identity mismatch for {row["case"]}')
            results.append(result)
            (out / 'progress.json').write_text(json.dumps({
                'status': 'in_progress', 'completed_cases': len(results), 'cases': results,
            }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except Exception as exc:
        failure = {'status': 'failed_retained_watch_validation', 'completed_cases': len(results),
                   'current_case': current_case, 'error': str(exc), 'cases': results}
        if current_artifacts:
            failure['current_artifacts'] = {
                key: str(value.relative_to(PROJECT)) if isinstance(value, Path) and value.is_relative_to(PROJECT) else str(value)
                for key, value in current_artifacts.items()
            }
        (out / 'failure.json').write_text(json.dumps(failure, ensure_ascii=False, indent=2) + '\n',
                                          encoding='utf-8')
        raise

    receipt = {
        'status': 'passed_first_indent_counter_watch_revalidation',
        'target_exe_sha256': manifest['target_exe_sha256'],
        'manifest': manifest_path.relative_to(ROOT).as_posix(),
        'manifest_sha256': sha(manifest_path),
        'cases': results,
        'limits': 'Retained synthetic inputs only. The hardware watch is bound to the report interval/thread and validates writes; zero changes do not prove a rule is absent. Full diagnostic text is compared after whitespace normalization; no semantic equivalence or rule promotion is asserted.',
    }
    (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n',
                                      encoding='utf-8')
    (out / 'progress.json').unlink(missing_ok=True)
    print(json.dumps({'status': receipt['status'], 'cases': len(results),
                      'same_full_reports': sum(item['same_full_report'] for item in results),
                      'fresh_runs': sum(item['artifact_kind'] == 'fresh' for item in results),
                      'reused_seeds': sum(item['artifact_kind'] == 'seed' for item in results)}))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}, ensure_ascii=False))
        sys.exit(1)

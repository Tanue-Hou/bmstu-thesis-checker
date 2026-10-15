"""Publish only the fixed synthetic pilot's measurements and selected raw evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT.parent / 'private_trials'
OUT = ROOT / 'evidence/differential-platform-r1'
sys.path.insert(0, str(ROOT / 'scripts'))
from native_reference_cli import validate_native_run
from differential_mutations import paragraph_atoms


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def publish_run(folder, destination):
    folder = folder.resolve()
    assert folder.is_relative_to(PRIVATE.resolve())
    cache = read(folder / 'cache.json')
    for name, wanted in cache['files'].items():
        file = (folder / name).resolve()
        assert file.is_relative_to(folder) and sha(file) == wanted
    trace = read(folder / 'native/native/trace.json')
    report = read(folder / 'native/report.json')
    source = folder / 'input.docx'
    validate_native_run(trace, (folder / 'native/native/native-result.txt').read_bytes().decode('utf8'),
                        'master', 'docx', sha(source), True)
    assert report['source_sha256'] == sha(source)
    destination.mkdir(exist_ok=True)
    for name, path in [('input.docx', source), ('trace.json', folder / 'native/native/trace.json'),
                       ('native-result.txt', folder / 'native/native/native-result.txt'),
                       ('report.json', folder / 'native/report.json'), ('local.json', folder / 'local.json'),
                       ('tracer-source.py.txt', folder / 'native/native/tracer-source.py.txt'),
                       ('sender-source.cs.txt', folder / 'native/sender-source.cs.txt')]:
        shutil.copyfile(path, destination / name)
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in destination.iterdir() if p.is_file()}


def main():
    seed = ROOT / 'evidence/dynamic-master/baseline.docx'
    spec = read(OUT / 'spec.json')
    assert sha(seed) == spec['seed_sha256']
    initial = PRIVATE / 'differential-platform-r1'
    boundaries = PRIVATE / 'differential-platform-boundary-r1'
    final = PRIVATE / 'differential-platform-final-r1'
    # Explicitly synthetic, hash-pinned inputs; no arbitrary private case publishing.
    assert read(initial / 'campaign.json')['seed_sha256'] == sha(seed)
    assert read(boundaries / 'campaign.json')['seed_sha256'] == sha(seed)
    assert read(final / 'campaign.json')['seed_sha256'] == sha(OUT / 'reduction-seed.docx')
    runs = [(p, read(p / 'summary.json')) for p in (final / 'runs').iterdir()]
    fresh = [(p, s) for p, s in runs if s['fresh_native_runs'] > 0]
    replay = [(p, s) for p, s in runs if s['fresh_native_runs'] == 0 and s['verified_cache_hits'] == 5]
    assert len(fresh) == 1 and len(replay) == 1
    first_dir, final_summary = fresh[0]
    rows = read(first_dir / 'results.private.json')
    reduced = rows[0]['minimization']
    assert len(reduced['items']) == 1 and reduced['status'] == 'unresolved'
    verified = [r for r in reduced['evaluations_detail'] if r.get('input_sha256') == reduced['sha256']
                and r.get('status') == 'family_difference']
    assert verified
    selected = Path(verified[0]['evidence_directory'])
    published = publish_run(selected, OUT / 'one-paragraph-counterexample')
    for p in (first_dir / 'sources').iterdir():
        shutil.copyfile(p, OUT / ('final-' + p.name))
    for directory, name in [(initial, 'initial'), (boundaries, 'boundary')]:
        stats = read(directory / 'summary.json')
        # Source snippets and aggregate outcomes only, no case identities or text.
        (OUT / (name + '-summary.json')).write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    branches = read(OUT / 'section-boundaries-r2/receipt.json')
    assert len(branches['cases']) == 16 and branches['status'] == 'passed_section_distance_boundary_branches'
    receipt = {'status': 'passed_synthetic_differential_pilot',
               'initial_campaign': read(initial / 'summary.json'),
               'boundary_campaign': read(boundaries / 'summary.json'),
               'final_minimization_fresh_native_runs': final_summary['fresh_native_runs'],
               'final_replay_fresh_native_runs': replay[0][1]['fresh_native_runs'],
               'final_replay_verified_cache_hits': replay[0][1]['verified_cache_hits'],
               'original_paragraphs': len(paragraph_atoms(seed.read_bytes())),
               'intermediate_paragraphs': len(paragraph_atoms((OUT / 'reduction-seed.docx').read_bytes())),
               'final_paragraphs': len(reduced['items']), 'minimization_status': reduced['status'],
               'minimization_evaluations': reduced['evaluations'],
               'minimization_unresolved_evaluations': reduced['unresolved_evaluations'],
               'final_empty_candidate_status': reduced['evaluations_detail'][-1]['status'],
               'section_boundary_cases': len(branches['cases']), 'published_sha256': published,
               'repair_or_rule_promotion': False,
               'limits': 'Synthetic pilot, selected diagnostic-family counts only. One-paragraph difference preserved; deleting the final paragraph failed native execution, so not certified minimal. Not school correctness or population accuracy.'}
    (OUT / 'pilot-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'status': receipt['status'], 'final_paragraphs': receipt['final_paragraphs'],
                      'minimization_status': receipt['minimization_status'], 'boundary_cases': receipt['section_boundary_cases']}))


if __name__ == '__main__':
    main()

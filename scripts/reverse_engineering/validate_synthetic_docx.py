"""Read-only official SDK validation of an evidence manifest's synthetic inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT.parent / 'runtime/openxml-sdk-2.20.0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    out = args.out.resolve()
    evidence = ROOT / 'evidence'
    if not manifest_path.is_relative_to(evidence) or not out.is_relative_to(evidence):
        raise ValueError('Only public synthetic evidence paths are supported')
    if out.exists():
        raise FileExistsError('Do not overwrite retained schema evidence')
    manifest = json.loads(manifest_path.read_bytes())
    paths = []
    for row in manifest['cases']:
        path = (manifest_path.parent / row['path']).resolve()
        if not path.is_relative_to(evidence) or sha(path) != row['sha256']:
            raise ValueError('Input path/hash mismatch')
        paths.append(path)
    exe = RUNTIME / 'ValidateSyntheticDocx.exe'
    build = json.loads((RUNTIME / 'build-receipt.json').read_bytes())
    assert build['status'] == 'compiled'
    assert build['source_sha256'] == sha(ROOT / 'scripts/reverse_engineering/ValidateSyntheticDocx.cs')
    assert build['validator_binary_sha256'] == sha(exe)
    assert build['sdk_binary_sha256'] == sha(RUNTIME / 'DocumentFormat.OpenXml.dll')
    result = subprocess.run([str(exe), *map(str, paths)], capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError('SDK execution failed: ' + result.stderr.decode('utf8', errors='replace')[:500])
    data = json.loads(result.stdout.decode('utf-8-sig'))
    assert len(data['cases']) == len(paths) and data['read_only'] is True
    for index, (case, row, path) in enumerate(zip(data['cases'], manifest['cases'], paths)):
        assert Path(case['file']).resolve() == path and sha(path) == row['sha256']
        case['file'] = path.relative_to(ROOT).as_posix()
        case['source_sha256'] = row['sha256']
        case['case_id'] = row['case_id']
        assert case['error_count'] == len(case['errors'])
    data.update(manifest_sha256=sha(manifest_path),
                validator_source_sha256=sha(ROOT / 'scripts/reverse_engineering/ValidateSyntheticDocx.cs'),
                validator_binary_sha256=sha(exe), sdk_binary_sha256=sha(RUNTIME / 'DocumentFormat.OpenXml.dll'),
                nuget_package_sha256=sha(RUNTIME / 'package.nupkg'),
                package_source='https://api.nuget.org/v3-flatcontainer/documentformat.openxml/2.20.0/documentformat.openxml.2.20.0.nupkg',
                input_count=len(paths), valid_input_count=sum(case['error_count'] == 0 for case in data['cases']),
                source_unchanged=True)
    data['validator_build'] = build
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: data[k] for k in ['input_count', 'valid_input_count', 'source_unchanged', 'limits']}))


if __name__ == '__main__':
    main()

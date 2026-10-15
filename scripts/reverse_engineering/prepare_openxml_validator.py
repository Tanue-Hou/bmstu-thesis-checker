"""Build a local read-only validator from a hash-pinned official NuGet package."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT.parent / 'runtime/openxml-sdk-2.20.0'
PACKAGE_SHA256 = '053312e1a2a606dcc5bcfcff6cc9f37235a1f43b3745ac907283d3122ce9f768'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    package = OUT / 'package.nupkg'
    if sha(package) != PACKAGE_SHA256:
        raise ValueError('Expected official DocumentFormat.OpenXml 2.20.0 package identity')
    with ZipFile(package) as archive:
        (OUT / 'DocumentFormat.OpenXml.dll').write_bytes(archive.read('lib/net46/DocumentFormat.OpenXml.dll'))
    framework = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Microsoft.NET/Framework/v4.0.30319'
    compiler = framework / 'csc.exe'
    windows_base = framework / 'WPF/WindowsBase.dll'
    source = ROOT / 'scripts/reverse_engineering/ValidateSyntheticDocx.cs'
    exe = OUT / 'ValidateSyntheticDocx.exe'
    result = subprocess.run([str(compiler), '/nologo', '/r:' + str(OUT / 'DocumentFormat.OpenXml.dll'),
                             '/r:' + str(windows_base), '/r:System.Web.Extensions.dll',
                             '/out:' + str(exe), str(source)], capture_output=True)
    (OUT / 'compiler.log').write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError('Compile failed; inspect runtime compiler.log')
    receipt = {'status': 'compiled', 'source_sha256': sha(source), 'package_sha256': sha(package),
               'sdk_binary_sha256': sha(OUT / 'DocumentFormat.OpenXml.dll'),
               'validator_binary_sha256': sha(exe), 'compiler_sha256': sha(compiler),
               'windows_base_sha256': sha(windows_base), 'compiler_exit_code': result.returncode,
               'compiler_log_sha256': sha(OUT / 'compiler.log')}
    (OUT / 'build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()

"""Rebuild frozen r1 feature matrix with corrected r2 charts and SDK-found attribute fix."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from lxml import etree
import generate_complex_section_probes_r2 as builder

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'evidence/complex-section-r3-schema'
    if out.exists():
        raise FileExistsError('Do not overwrite retained inputs')
    source_manifest = ROOT / 'evidence/complex-section-r1/manifest.json'
    previous = json.loads(source_manifest.read_bytes())
    baseline = ROOT / previous['baseline']['path_from_implementation']
    assert sha(baseline) == previous['baseline']['sha256']
    with ZipFile(baseline) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
        infos = {info.filename: info for info in archive.infolist()}
    out.mkdir()
    (out / 'inputs').mkdir()
    cases = []
    for row in previous['cases']:
        section = row['section']
        generated = builder.mutate_package(parts, row['features'], section['header_twips'], section['footer_twips'])
        document = etree.fromstring(generated['word/document.xml'])
        repaired = 0
        for node in document.iter('{%s}graphicFrameLocks' % builder.A):
            qualified = '{%s}noChangeAspect' % builder.A
            if qualified in node.attrib:
                node.set('noChangeAspect', node.attrib.pop(qualified))
                repaired += 1
        generated['word/document.xml'] = builder.xml_bytes(document)
        path = out / row['path']
        builder.write_docx(path, generated, infos)
        builder.validate_docx(path, row['features'], section['header_twips'], section['footer_twips'])
        cases.append({**row, 'sha256': sha(path), 'bytes': path.stat().st_size,
                      'corrected_lock_attributes': repaired,
                      'input_validation': 'ZIP/XML/python-docx and local chart checks passed; official SDK results recorded separately.'})
    manifest = {'schema': 'native232-complex-section-probes-r3-schema', 'cases': cases,
                'case_count': len(cases), 'baseline': previous['baseline'],
                'matrix_source': {'path': source_manifest.relative_to(ROOT).as_posix(), 'sha256': sha(source_manifest)},
                'generator': {'path_from_implementation': Path(__file__).relative_to(ROOT).as_posix(),
                              'sha256': sha(Path(__file__))},
                'builder': {'path_from_implementation': Path(builder.__file__).relative_to(ROOT).as_posix(),
                            'sha256': sha(Path(builder.__file__))},
                'changes': ['r2 chart marker ordering and two axis IDs',
                            'graphicFrameLocks noChangeAspect attribute is unqualified'],
                'limits': 'Synthetic generation; schema/native validation stored separately. No rendering or repair claim.'}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'inputs': len(cases), 'baseline_unchanged': sha(baseline) == previous['baseline']['sha256']}))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Create deterministic, synthetic Native232 complex-section DOCX probes.

The baseline is read-only. The output directory is write-once so generated
inputs and their manifest remain an immutable evidence set.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import tempfile
import zlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from lxml import etree
from docx import Document


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'evidence' / 'dynamic-master' / 'baseline.docx'
DEFAULT_OUT = ROOT / 'evidence' / 'complex-section-r1'
SEED = 'native232-complex-section-probes-r1:baseline-sha-bound:20261016'

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG_REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PIC = 'http://schemas.openxmlformats.org/drawingml/2006/picture'
C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

REL_TYPES = {
    'header': R + '/header',
    'footer': R + '/footer',
    'image': R + '/image',
    'chart': R + '/chart',
}
CHART_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.drawingml.chart+xml'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def q(ns: str, name: str) -> str:
    return f'{{{ns}}}{name}'


def xml_bytes(root) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)


def new_element(parent, ns: str, name: str, attrs: dict[str, str] | None = None):
    element = etree.SubElement(parent, q(ns, name))
    for key, value in (attrs or {}).items():
        element.set(key, value)
    return element


def next_rid(rels_root) -> str:
    used = {item.get('Id') for item in rels_root}
    index = 1
    while f'rId{index}' in used:
        index += 1
    return f'rId{index}'


def png_1x1() -> bytes:
    """Produce a fixed 1x1 RGB PNG without image libraries or external data."""
    def chunk(kind: bytes, payload: bytes) -> bytes:
        body = kind + payload
        return struct.pack('>I', len(payload)) + body + struct.pack('>I', zlib.crc32(body) & 0xFFFFFFFF)

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b'\x00\x40\x80\xc0', level=9))
            + chunk(b'IEND', b''))


def field_story(root_name: str, field_label: str) -> bytes:
    root = etree.Element(q(W, root_name), nsmap={'w': W})
    p = new_element(root, W, 'p')
    r = new_element(p, W, 'r')
    t = new_element(r, W, 't')
    t.text = field_label + ' '
    r = new_element(p, W, 'r')
    new_element(r, W, 'fldChar', {q(W, 'fldCharType'): 'begin', q(W, 'dirty'): 'true'})
    r = new_element(p, W, 'r')
    instruction = new_element(r, W, 'instrText', {'{http://www.w3.org/XML/1998/namespace}space': 'preserve'})
    instruction.text = ' PAGE '
    r = new_element(p, W, 'r')
    new_element(r, W, 'fldChar', {q(W, 'fldCharType'): 'separate'})
    r = new_element(p, W, 'r')
    t = new_element(r, W, 't')
    t.text = '1'
    r = new_element(p, W, 'r')
    new_element(r, W, 'fldChar', {q(W, 'fldCharType'): 'end'})
    return xml_bytes(root)


def add_header_footer_parts(parts: dict[str, bytes], document_root, relationships_root, content_types_root):
    header_rid = next_rid(relationships_root)
    etree.SubElement(relationships_root, q(PKG_REL, 'Relationship'), {
        'Id': header_rid, 'Type': REL_TYPES['header'], 'Target': 'header1.xml'})
    footer_rid = next_rid(relationships_root)
    etree.SubElement(relationships_root, q(PKG_REL, 'Relationship'), {
        'Id': footer_rid, 'Type': REL_TYPES['footer'], 'Target': 'footer1.xml'})
    sect = document_root.find('.//' + q(W, 'sectPr'))
    if sect is None:
        raise ValueError('Baseline DOCX has no w:sectPr')
    header_ref = etree.Element(q(W, 'headerReference'), {q(W, 'type'): 'default', q(R, 'id'): header_rid})
    footer_ref = etree.Element(q(W, 'footerReference'), {q(W, 'type'): 'default', q(R, 'id'): footer_rid})
    sect.insert(0, header_ref)
    sect.insert(1, footer_ref)
    parts['word/header1.xml'] = field_story('hdr', 'Header page')
    parts['word/footer1.xml'] = field_story('ftr', 'Footer page')
    etree.SubElement(content_types_root, q(CT, 'Override'), {
        'PartName': '/word/header1.xml',
        'ContentType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml'})
    etree.SubElement(content_types_root, q(CT, 'Override'), {
        'PartName': '/word/footer1.xml',
        'ContentType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml'})


def append_table(body):
    table = etree.Element(q(W, 'tbl'))
    new_element(table, W, 'tblPr')
    grid = new_element(table, W, 'tblGrid')
    new_element(grid, W, 'gridCol', {q(W, 'w'): '3000'})
    new_element(grid, W, 'gridCol', {q(W, 'w'): '3000'})
    row = new_element(table, W, 'tr')
    for text in ('Table cell A', 'Table cell B'):
        cell = new_element(row, W, 'tc')
        new_element(cell, W, 'tcPr')
        p = new_element(cell, W, 'p')
        r = new_element(p, W, 'r')
        t = new_element(r, W, 't')
        t.text = text
    body.insert(len(body) - 1, table)


def append_equation(body):
    p = etree.Element(q(W, 'p'))
    equation = new_element(p, M, 'oMath')
    run = new_element(equation, M, 'r')
    props = new_element(run, M, 'rPr')
    new_element(props, M, 'sty', {q(M, 'val'): 'p'})
    text = new_element(run, M, 't')
    text.text = 'x'
    operator = new_element(equation, M, 'r')
    op_text = new_element(operator, M, 't')
    op_text.text = ' = 1'
    body.insert(len(body) - 1, p)


def image_drawing(rid: str):
    drawing = etree.Element(q(W, 'drawing'))
    inline = new_element(drawing, WP, 'inline', {
        'distT': '0', 'distB': '0', 'distL': '0', 'distR': '0'})
    new_element(inline, WP, 'extent', {'cx': '914400', 'cy': '914400'})
    new_element(inline, WP, 'effectExtent', {'l': '0', 't': '0', 'r': '0', 'b': '0'})
    new_element(inline, WP, 'docPr', {'id': '1', 'name': 'Synthetic inline PNG'})
    frame = new_element(inline, WP, 'cNvGraphicFramePr')
    new_element(frame, A, 'graphicFrameLocks', {q(A, 'noChangeAspect'): '1'})
    graphic = new_element(inline, A, 'graphic')
    data = new_element(graphic, A, 'graphicData', {'uri': PIC})
    pic = new_element(data, PIC, 'pic')
    nonvisual = new_element(pic, PIC, 'nvPicPr')
    new_element(nonvisual, PIC, 'cNvPr', {'id': '0', 'name': 'Synthetic image'})
    new_element(nonvisual, PIC, 'cNvPicPr')
    fill = new_element(pic, PIC, 'blipFill')
    new_element(fill, A, 'blip', {q(R, 'embed'): rid})
    stretch = new_element(fill, A, 'stretch')
    new_element(stretch, A, 'fillRect')
    shape = new_element(pic, PIC, 'spPr')
    transform = new_element(shape, A, 'xfrm')
    new_element(transform, A, 'off', {'x': '0', 'y': '0'})
    new_element(transform, A, 'ext', {'cx': '914400', 'cy': '914400'})
    geometry = new_element(shape, A, 'prstGeom', {'prst': 'rect'})
    new_element(geometry, A, 'avLst')
    return drawing


def chart_part() -> bytes:
    """Minimal line chart with literal cached series data and no workbook."""
    root = etree.Element(q(C, 'chartSpace'), nsmap={'c': C, 'a': A, 'r': R})
    new_element(root, C, 'lang', {'val': 'en-US'})
    chart = new_element(root, C, 'chart')
    new_element(chart, C, 'autoTitleDeleted', {'val': '1'})
    plot = new_element(chart, C, 'plotArea')
    new_element(plot, C, 'layout')
    line = new_element(plot, C, 'lineChart')
    new_element(line, C, 'grouping', {'val': 'standard'})
    new_element(line, C, 'varyColors', {'val': '0'})
    series = new_element(line, C, 'ser')
    new_element(series, C, 'idx', {'val': '0'})
    new_element(series, C, 'order', {'val': '0'})
    title = new_element(series, C, 'tx')
    new_element(title, C, 'v').text = 'Series 1'
    categories = new_element(series, C, 'cat')
    cat_lit = new_element(categories, C, 'strLit')
    cat_count = new_element(cat_lit, C, 'ptCount', {'val': '2'})
    for index, label in enumerate(('A', 'B')):
        point = new_element(cat_lit, C, 'pt', {'idx': str(index)})
        new_element(point, C, 'v').text = label
    values = new_element(series, C, 'val')
    num_lit = new_element(values, C, 'numLit')
    new_element(num_lit, C, 'formatCode').text = 'General'
    new_element(num_lit, C, 'ptCount', {'val': '2'})
    for index, value in enumerate(('1', '2')):
        point = new_element(num_lit, C, 'pt', {'idx': str(index)})
        new_element(point, C, 'v').text = value
    marker = new_element(series, C, 'marker')
    new_element(marker, C, 'symbol', {'val': 'circle'})
    new_element(line, C, 'smooth', {'val': '0'})
    cat_axis = new_element(plot, C, 'catAx')
    new_element(cat_axis, C, 'axId', {'val': '48650112'})
    scaling = new_element(cat_axis, C, 'scaling')
    new_element(scaling, C, 'orientation', {'val': 'minMax'})
    new_element(cat_axis, C, 'axPos', {'val': 'b'})
    new_element(cat_axis, C, 'tickLblPos', {'val': 'nextTo'})
    new_element(cat_axis, C, 'crossAx', {'val': '48672768'})
    new_element(cat_axis, C, 'crosses', {'val': 'autoZero'})
    new_element(cat_axis, C, 'auto', {'val': '1'})
    new_element(cat_axis, C, 'lblAlgn', {'val': 'ctr'})
    new_element(cat_axis, C, 'lblOffset', {'val': '100'})
    val_axis = new_element(plot, C, 'valAx')
    new_element(val_axis, C, 'axId', {'val': '48672768'})
    scaling = new_element(val_axis, C, 'scaling')
    new_element(scaling, C, 'orientation', {'val': 'minMax'})
    new_element(val_axis, C, 'axPos', {'val': 'l'})
    new_element(val_axis, C, 'majorGridlines')
    new_element(val_axis, C, 'numFmt', {'formatCode': 'General', 'sourceLinked': '1'})
    new_element(val_axis, C, 'tickLblPos', {'val': 'nextTo'})
    new_element(val_axis, C, 'crossAx', {'val': '48650112'})
    new_element(val_axis, C, 'crosses', {'val': 'autoZero'})
    new_element(val_axis, C, 'crossBetween', {'val': 'between'})
    legend = new_element(chart, C, 'legend')
    new_element(legend, C, 'legendPos', {'val': 'b'})
    new_element(legend, C, 'layout')
    new_element(chart, C, 'plotVisOnly', {'val': '1'})
    new_element(chart, C, 'dispBlanksAs', {'val': 'gap'})
    new_element(chart, C, 'showDLblsOverMax', {'val': '0'})
    return xml_bytes(root)


def chart_drawing(rid: str):
    drawing = etree.Element(q(W, 'drawing'))
    inline = new_element(drawing, WP, 'inline', {
        'distT': '0', 'distB': '0', 'distL': '0', 'distR': '0'})
    new_element(inline, WP, 'extent', {'cx': '3657600', 'cy': '2286000'})
    new_element(inline, WP, 'docPr', {'id': '2', 'name': 'Synthetic native chart'})
    frame = new_element(inline, WP, 'cNvGraphicFramePr')
    new_element(frame, A, 'graphicFrameLocks', {q(A, 'noChangeAspect'): '1'})
    graphic = new_element(inline, A, 'graphic')
    data = new_element(graphic, A, 'graphicData', {'uri': C})
    new_element(data, C, 'chart', {q(R, 'id'): rid})
    return drawing


def add_image(parts, document_root, relationships_root, content_types_root):
    rid = next_rid(relationships_root)
    etree.SubElement(relationships_root, q(PKG_REL, 'Relationship'), {
        'Id': rid, 'Type': REL_TYPES['image'], 'Target': 'media/complex-section-probe.png'})
    if not any(x.get('Extension') == 'png' for x in content_types_root):
        etree.SubElement(content_types_root, q(CT, 'Default'), {
            'Extension': 'png', 'ContentType': 'image/png'})
    parts['word/media/complex-section-probe.png'] = png_1x1()
    p = etree.Element(q(W, 'p'))
    r = new_element(p, W, 'r')
    r.append(image_drawing(rid))
    body = document_root.find('.//' + q(W, 'body'))
    body.insert(len(body) - 1, p)


def add_chart(parts, document_root, relationships_root, content_types_root):
    rid = next_rid(relationships_root)
    etree.SubElement(relationships_root, q(PKG_REL, 'Relationship'), {
        'Id': rid, 'Type': REL_TYPES['chart'], 'Target': 'charts/chart1.xml'})
    etree.SubElement(content_types_root, q(CT, 'Override'), {
        'PartName': '/word/charts/chart1.xml', 'ContentType': CHART_CONTENT_TYPE})
    parts['word/charts/chart1.xml'] = chart_part()
    p = etree.Element(q(W, 'p'))
    r = new_element(p, W, 'r')
    r.append(chart_drawing(rid))
    body = document_root.find('.//' + q(W, 'body'))
    body.insert(len(body) - 1, p)


def add_section_distances(document_root, header_twips: int, footer_twips: int):
    sect = document_root.find('.//' + q(W, 'sectPr'))
    margins = sect.find(q(W, 'pgMar')) if sect is not None else None
    if margins is None:
        raise ValueError('Baseline DOCX is missing w:sectPr/w:pgMar')
    margins.set(q(W, 'header'), str(header_twips))
    margins.set(q(W, 'footer'), str(footer_twips))


FAMILIES = (
    ('header_footer_story', {'stories': True}),
    ('single_ordinary_table', {'table': True}),
    ('omml_equation', {'omml': True}),
    ('inline_png', {'inline_png': True}),
    ('native_word_chart', {'chart_part': True}),
    ('combined_complex', {'stories': True, 'table': True, 'omml': True, 'inline_png': True, 'chart_part': True}),
)
HEADER_VALUES = (697, 698, 720, 721)


def mutate_package(source_parts: dict[str, bytes], features: dict[str, bool], header: int, footer: int):
    parts = dict(source_parts)
    doc_root = etree.fromstring(parts['word/document.xml'])
    rels_root = etree.fromstring(parts['word/_rels/document.xml.rels'])
    content_types_root = etree.fromstring(parts['[Content_Types].xml'])
    body = doc_root.find('.//' + q(W, 'body'))
    if features.get('stories'):
        add_header_footer_parts(parts, doc_root, rels_root, content_types_root)
    if features.get('table'):
        append_table(body)
    if features.get('omml'):
        append_equation(body)
    if features.get('inline_png'):
        add_image(parts, doc_root, rels_root, content_types_root)
    if features.get('chart_part'):
        add_chart(parts, doc_root, rels_root, content_types_root)
    add_section_distances(doc_root, header, footer)
    parts['word/document.xml'] = xml_bytes(doc_root)
    parts['word/_rels/document.xml.rels'] = xml_bytes(rels_root)
    parts['[Content_Types].xml'] = xml_bytes(content_types_root)
    return parts


def write_docx(path: Path, parts: dict[str, bytes], infos: dict[str, ZipInfo]):
    with ZipFile(path, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, payload in parts.items():
            info = infos.get(name)
            if info is None:
                info = ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o600 << 16
            archive.writestr(info, payload, compress_type=ZIP_DEFLATED, compresslevel=9)


def validate_docx(path: Path, features: dict[str, bool], header: int, footer: int):
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError(f'ZIP CRC failed for {path.name}')
        names = set(archive.namelist())
        document_root = etree.fromstring(archive.read('word/document.xml'))
        rels_root = etree.fromstring(archive.read('word/_rels/document.xml.rels'))
        content_types_root = etree.fromstring(archive.read('[Content_Types].xml'))
        sect = document_root.find('.//' + q(W, 'sectPr'))
        margins = sect.find(q(W, 'pgMar'))
        actual = (int(margins.get(q(W, 'header'))), int(margins.get(q(W, 'footer'))))
        if actual != (header, footer):
            raise ValueError(f'Section values do not match manifest in {path.name}')
        if features.get('stories'):
            if not {'word/header1.xml', 'word/footer1.xml'} <= names:
                raise ValueError('Header/footer story part missing')
            for part, root_name in (('word/header1.xml', 'hdr'), ('word/footer1.xml', 'ftr')):
                story = etree.fromstring(archive.read(part))
                if story.tag != q(W, root_name) or not story.xpath('.//w:instrText[contains(., "PAGE")]', namespaces={'w': W}):
                    raise ValueError(f'Expected PAGE field missing from {part}')
        if features.get('table') and not document_root.findall('.//' + q(W, 'tbl')):
            raise ValueError('Ordinary table missing')
        if features.get('omml') and not document_root.findall('.//' + q(M, 'oMath')):
            raise ValueError('OMML equation missing')
        if features.get('inline_png'):
            if 'word/media/complex-section-probe.png' not in names:
                raise ValueError('PNG part missing')
            if not document_root.findall('.//' + q(W, 'drawing')):
                raise ValueError('Inline drawing missing')
            defaults = [x for x in content_types_root if x.get('Extension') == 'png']
            if not defaults or defaults[0].get('ContentType') != 'image/png':
                raise ValueError('PNG content type missing')
        if features.get('chart_part'):
            if 'word/charts/chart1.xml' not in names:
                raise ValueError('Chart part missing')
            chart = etree.fromstring(archive.read('word/charts/chart1.xml'))
            if chart.tag != q(C, 'chartSpace') or not chart.findall('.//' + q(C, 'lineChart')):
                raise ValueError('Chart part does not contain chart-space/line-chart structure')
            overrides = [x for x in content_types_root if x.get('PartName') == '/word/charts/chart1.xml']
            if not overrides or overrides[0].get('ContentType') != CHART_CONTENT_TYPE:
                raise ValueError('Chart content type missing')
        # python-docx parsing is a structural sanity check only; it is not an Office schema validator.
        Document(str(path))


def build_manifest(out_root: Path, baseline_bytes: bytes, cases: list[dict]):
    return {
        'schema': 'native232-complex-section-probes-r1',
        'seed': SEED,
        'seed_sha256': sha256(SEED.encode('utf-8')),
        'baseline': {
            'path_from_implementation': 'evidence/dynamic-master/baseline.docx',
            'sha256': sha256(baseline_bytes),
            'bytes': len(baseline_bytes),
            'read_only_source': True,
        },
        'generator': {
            'path_from_implementation': 'scripts/reverse_engineering/generate_complex_section_probes.py',
            'sha256': sha256(Path(__file__).read_bytes()),
        },
        'output_directory': 'evidence/complex-section-r1/inputs',
        'case_count': len(cases),
        'cases': cases,
        'chart_part_validation': 'Package relationships, content type, chartSpace, lineChart and cached literal data are checked; no Open XML XSD or Microsoft Word validation is performed. Treat chart native behavior as unverified until actual capture.',
        'execution_policy': 'Synthetic DOCX generation only. This script does not start TestVkr, open Word, use network, or modify the baseline.',
    }


def generate(out_root: Path):
    baseline_bytes = BASELINE.read_bytes()
    base_hash = sha256(baseline_bytes)
    output_root = out_root.resolve()
    evidence_root = (ROOT / 'evidence').resolve()
    if evidence_root not in output_root.parents:
        raise ValueError('Output must be a new directory inside implementation/evidence')
    if output_root.exists():
        raise FileExistsError(f'Refusing to replace existing evidence directory: {output_root}')
    with ZipFile(BASELINE) as source:
        source_parts = {name: source.read(name) for name in source.namelist()}
        source_infos = {info.filename: info for info in source.infolist()}

    pending: list[tuple[str, str, dict[str, bool], int, int, dict[str, bytes]]] = []
    for family, features in FAMILIES:
        for header in HEADER_VALUES:
            pending.append((family, f'{family}-header-{header}', features, header, 709,
                            mutate_package(source_parts, features, header, 709)))
    story_features = dict(FAMILIES[0][1])
    for footer in HEADER_VALUES:
        pending.append(('header_footer_story', f'header-footer-story-footer-{footer}', story_features,
                        709, footer, mutate_package(source_parts, story_features, 709, footer)))

    records = []
    with tempfile.TemporaryDirectory(prefix='complex-section-validation-', dir=ROOT / 'scripts') as temp_dir:
        temp_root = Path(temp_dir)
        for family, case_id, features, header, footer, parts in pending:
            temp_path = temp_root / f'{case_id}.docx'
            write_docx(temp_path, parts, source_infos)
            validate_docx(temp_path, features, header, footer)
            data = temp_path.read_bytes()
            records.append({
                'case_id': case_id,
                'family': family,
                'path': f'inputs/{case_id}.docx',
                'sha256': sha256(data),
                'bytes': len(data),
                'features': {key: bool(value) for key, value in sorted(features.items())},
                'section': {'header_twips': header, 'footer_twips': footer},
                'input_validation': 'ZIP/XML parse and python-docx open succeeded; chart remains unverified against Office XSD/native behavior.' if features.get('chart_part') else 'ZIP/XML parse and python-docx open succeeded; synthetic input only.',
            })

    # Create the final evidence tree only after every in-memory variant validates.
    output_root.mkdir(parents=True, exist_ok=False)
    inputs_dir = output_root / 'inputs'
    inputs_dir.mkdir()
    for record, item in zip(records, pending):
        final_path = inputs_dir / (record['case_id'] + '.docx')
        # Rebuild deterministic bytes rather than retaining temp files; the manifest hashes assert identity.
        _, _, _, header, footer, parts = item
        write_docx(final_path, parts, source_infos)
        actual_hash = sha256(final_path.read_bytes())
        if actual_hash != record['sha256']:
            raise ValueError(f'Non-deterministic archive bytes for {final_path.name}')
    manifest = build_manifest(output_root, baseline_bytes, records)
    (output_root / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT,
                        help='New output directory under implementation/evidence (default: evidence/complex-section-r1)')
    args = parser.parse_args()
    result = generate(args.out)
    print(json.dumps({
        'status': 'generated',
        'output_directory': str(args.out.resolve()),
        'case_count': result['case_count'],
        'families': sorted({row['family'] for row in result['cases']}),
        'manifest_sha256': sha256((args.out.resolve() / 'manifest.json').read_bytes()),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()

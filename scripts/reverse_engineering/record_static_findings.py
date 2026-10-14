"""Derive findings from retained bytes/pseudocode and update evidence metadata."""
import hashlib
import json
import re
import struct
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('binary', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    evidence = root / 'evidence' / '2026-10-14'
    binary = args.binary.read_bytes()
    pe = struct.unpack_from('<I', binary, 60)[0]
    optsize = struct.unpack_from('<H', binary, pe + 20)[0]
    number = struct.unpack_from('<H', binary, pe + 6)[0]
    base = struct.unpack_from('<I', binary, pe + 52)[0]
    sections = [struct.unpack_from('<8sIIII', binary, pe + 24 + optsize + i * 40) for i in range(number)]
    defaults = {}
    for name, va in (('font_size_min_pt', 0x006ee118), ('font_size_max_pt', 0x006ee11c)):
        rva = va - base
        section = next(s for s in sections if s[2] <= rva < s[2] + s[3])
        offset = section[4] + rva - section[2]
        defaults[name] = {'va': hex(va), 'file_offset': hex(offset), 'value': struct.unpack_from('<i', binary, offset)[0]}
    code_path = evidence / 'decompilation' / 'recovered_pseudocode.c'
    code = code_path.read_text(encoding='utf-8')
    sites = []
    for match in re.finditer(r'if \((\d{7,}) < ([^\n]+\*[^\n]+)\)', code):
        header = list(re.finditer(r'/\* ENTRY ([0-9a-f]+) NAME ([^ ]+) \*/', code[:match.start()]))[-1]
        sites.append({'function_va': '0x' + header[1], 'constant': int(match[1]),
                      'expression': match[2], 'pseudocode_line': code[:match.start()].count('\n') + 1})
    main_path = evidence / 'decompilation' / 'focused' / '004af82c.annotated.c'
    main_code = main_path.read_text(encoding='utf-8')
    message_constant = re.search(r'FUN_0046fa84\(local_1d4,(\d+)\)', main_code)
    if message_constant is None:
        raise ValueError('Expected pixel-limit message builder is missing')
    area_limit = int(message_constant[1])
    sites = [s for s in sites if s['constant'] == area_limit]
    if not sites:
        raise ValueError('No decoding-area comparison matches the message constant')
    findings = {'target_sha256': hashlib.sha256(binary).hexdigest(),
                'evidence_type': 'static_file_bytes_and_recovered_control_flow',
                'font_defaults': defaults, 'image_pixel_area_limit': area_limit, 'image_comparison_sites': sites,
                'limits': ['No runtime register capture', 'Original dynamic formatting comparison pending',
                           'Shipped defaults may differ from runtime configuration',
                           'DOCX and PDF predicates have different context gates and tolerances'],
                'pseudocode_sha256': hashlib.sha256(code_path.read_bytes()).hexdigest()}
    findings_path = evidence / 'static-findings.json'
    findings_path.write_text(json.dumps(findings, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    path = root / 'scripts' / 'testvkr-service' / 'rules' / 'rules_verified.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    for rule in data['rules']:
        if rule['rule_id'] == 'Word.FontSizeTooSmall':
            rule['threshold'] = defaults['font_size_min_pt']['value']
            rule['source_va'] = defaults['font_size_min_pt']['va']
            rule['threshold_origin'] = 'static_shipped_default_with_font_predicate_references'
            rule['static_evidence_refs'] = ['evidence/2026-10-14/static-findings.json']
            rule['confidence'] = 'medium'
        if rule['rule_id'] == 'Pic.PixelSizeTooLarge':
            rule['threshold'] = area_limit
            rule['unit'] = 'pixels_total'
            rule['measurement'] = 'native_width_px * native_height_px'
            rule['enabled_by_default'] = True
            rule['threshold_origin'] = 'static_decoder_area_comparison_and_message_constant'
            rule['static_evidence_refs'] = ['evidence/2026-10-14/static-findings.json']
            rule['confidence'] = 'medium'
    if not any(r['rule_id'] == 'Word.FontSizeTooLarge' for r in data['rules']):
        data['rules'].append({'rule_id': 'Word.FontSizeTooLarge', 'threshold': defaults['font_size_max_pt']['value'],
                              'comparator': '>', 'confidence': 'medium', 'observed_message': None,
                              'source_va': defaults['font_size_max_pt']['va'],
                              'verification_status': 'pending_original_program_comparison',
                              'threshold_origin': 'static_shipped_default_with_font_predicate_references',
                              'static_evidence_refs': ['evidence/2026-10-14/static-findings.json'],
                              'evidence_refs': [], 'enabled_by_default': True})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    guidance_path = path.with_name('rule_guidance_zh.json')
    guidance = json.loads(guidance_path.read_text(encoding='utf-8-sig'))
    guidance['Word.FontSizeTooSmall'].update({
        'explanation_zh': '字符字号低于当前检查下限。程序的异常字号下限不等于学校要求的正文字号。',
        'fix_suggestion_zh': '先核对学校模板及文字用途，再处理异常小字；不要把全文统一改成检查下限。'})
    guidance['Pic.PixelSizeTooLarge'].update({
        'title_zh': '图片总像素数过大',
        'explanation_zh': '图片原始宽度乘以高度超过总像素数限制；与论文中显示的厘米宽度不同。',
        'trigger_reason_zh': '原始宽度乘以高度超过当前总像素数阈值；阈值来自静态代码，对照验证仍待完成。',
        'fix_suggestion_zh': '根据打印尺寸与清晰度需求重新导出或压缩原图；仅在 Word 中缩小显示尺寸不会降低原图像素数。'})
    guidance_path.write_text(json.dumps(guidance, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'font_defaults': {k: v['value'] for k, v in defaults.items()},
                      'image_pixel_area_limit': area_limit, 'image_comparison_sites': len(sites)}))


if __name__ == '__main__':
    main()

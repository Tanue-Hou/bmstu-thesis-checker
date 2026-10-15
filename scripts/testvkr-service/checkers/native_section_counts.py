"""Native232 finite explicit-section distance predicate; independent of school policy."""
import struct

TWIPS_TO_MM = struct.unpack('<f', bytes.fromhex('6e7f903c'))[0]
TOLERANCE_MM = struct.unpack('<f', bytes.fromhex('cdcc4c3e'))[0]
EXPECTED_MM = 12.5


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def count_section_distance_candidates(data):
    sections = []
    known_count = 0
    supported = bool(data.get('native232_section_distances_supported'))
    supported = supported and len(data.get('sections', [])) == 1
    for index, section in enumerate(data.get('sections', []), 1):
        fields = {}
        path = section.get('xml_path')
        for name in ('header', 'footer'):
            twips = section.get('native_distances_twips', {}).get(name)
            valid = isinstance(twips, int) and not isinstance(twips, bool) and 0 <= twips <= 1440
            supported = supported and valid
            actual = f32(twips * TWIPS_TO_MM) if valid else None
            mismatch = not (EXPECTED_MM - TOLERANCE_MM <= actual <= EXPECTED_MM + TOLERANCE_MM) if valid else None
            known_count += int(mismatch is True)
            fields[name] = {'twips': twips, 'actual_mm': actual, 'mismatch': mismatch,
                            'attribute_xml_path': path + '/w:pgMar/@w:' + name if path else None}
        sections.append({'section': index, 'xml_path': path, 'fields': fields})
    return {'supported': supported, 'count': known_count if supported else None,
            'known_mismatch_count': known_count, 'sections': sections,
            'expected_mm': EXPECTED_MM, 'tolerance_mm': TOLERANCE_MM,
            'limits': 'Native232 single explicit ordinary DOCX section, integer distances 0..1440 twips. Unsupported profiles are unassessed, not a pass. This is not school compliance or repair permission.'}

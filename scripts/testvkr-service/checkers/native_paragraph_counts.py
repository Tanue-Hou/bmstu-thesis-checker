"""Native232 paragraph buckets with explicit activation and property provenance."""
import math
import struct

FACTOR = struct.unpack('<f', bytes.fromhex('6e7f903c'))[0]
INVERSE = struct.unpack('<f', bytes.fromhex('8bc56242'))[0]
NEGATIVE_LIMIT = struct.unpack('<f', bytes.fromhex('cdccccbd'))[0]
ACTIVATORS = {'\u0440\u0435\u0444\u0435\u0440\u0430\u0442', '\u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u044f',
              '\u0432\u0432\u0435\u0434\u0435\u043d\u0438\u0435', '\u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435'}


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def count_paragraph_candidates(doc_data):
    active = False
    counters = {'left': 0, 'right': 0, 'line': 0}
    records = []
    supported = bool(doc_data.get('native232_paragraph_profile_supported'))
    for index, paragraph in enumerate(doc_data.get('native_paragraph_properties', [])):
        text = paragraph['text'].strip(' \t\r\n')
        active_before = active
        if text.lower() in ACTIVATORS or index + 1 > 60:
            active = True
        # A table before activation can change native list state; not inferred here.
        if paragraph['role'] == 'table' and not active_before:
            supported = False
        raw = paragraph['raw_twips']
        values = {key: f32(value * FACTOR) if value is not None else None for key, value in raw.items()}
        candidate = math.trunc(values['line'] * INVERSE + 0.5) if values['line'] is not None else None
        if active and text and any(v is None for v in raw.values()):
            supported = False
        matches = {'left': active and bool(text) and values['left'] is not None and values['left'] < NEGATIVE_LIMIT,
                   'right': active and bool(text) and values['right'] is not None and values['right'] < NEGATIVE_LIMIT,
                   'line': active and bool(text) and candidate is not None and candidate < 180}
        for key, matched in matches.items():
            counters[key] += int(matched)
        records.append({**paragraph, 'index': index, 'active': active, 'activation_ordinal': index + 1,
                        'resolved_float32': values, 'line_integer': candidate, 'matches': matches})
    return counters, records, supported

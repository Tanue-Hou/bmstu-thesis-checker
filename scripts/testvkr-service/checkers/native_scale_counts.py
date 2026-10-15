"""Native232 scale buckets; do not reuse the large-font textbox gate."""
from .native_font_counts import count_font_candidates


def count_scale_candidates(data):
    # Reuse the independently traced activation order and source ownership.
    _, font_records = count_font_candidates(data)
    runs = []
    for paragraph in data.get('paragraphs',[]):
        runs.extend(paragraph.get('runs',[]))
    for table in data.get('tables',[]):
        for row in table.get('rows',[]):
            for cell in row.get('cells',[]):
                for paragraph in cell.get('paragraphs',[]):
                    runs.extend(paragraph.get('runs',[]))
    for label in data.get('labels',[]):
        for paragraph in label.get('font_paragraphs',[]):
            runs.extend(paragraph.get('runs',[]))
    by_path = {r['xml_path']:r for r in runs if r.get('xml_path')}
    counts = {'small':0,'tiny':0,'large':0}
    records = []
    supported = bool(data.get('native232_scale_profile_supported')) and bool(data.get('native232_font_profile_supported'))
    for record in font_records:
        run = by_path.get(record['location'].get('run_xml_path'))
        value = run.get('native_scale_pct',run.get('scale_pct',100.0)) if run else None
        bucket = None
        if value is None or not float(value).is_integer() or not -2147483648<=value<=2147483647:
            supported = False
        elif record['native_font_enabled']:
            if 30<value<70:
                bucket = 'small'
            elif 1<value<=30:
                bucket = 'tiny'
            elif value>130:
                bucket = 'large'
        item = {**record,'bucket':bucket,'scale_pct':value,
                'property_source':run.get('native_scale_source') if run else None}
        records.append(item)
        if bucket:
            counts[bucket]+=item['utf16_units']
    data['native232_scale_profile_supported']=supported
    return counts,records

"""Native232 DOCX font counters, including unreported tiny-text observations."""
def units(text):return len(text.encode('utf-16le'))//2

def count_font_candidates(data,minimum=8,maximum=18):
    records=[];counts={'small':0,'tiny':0,'large':0,'table_small':0,'table_large':0}
    from .native_paragraph_counts import ACTIVATORS
    active=False;phase={}
    for ordinal,event in enumerate(data.get('native_font_activation_events',[]),1):
        if event.get('xml_path') is not None:phase[event['xml_path']]={'enabled':active,'ordinal':ordinal}
        if event['text'].strip(' \t\r\n').lower() in ACTIVATORS or ordinal>60:active=True
    def visit(paragraph,role,location,previous=0):
        state=phase.get(paragraph.get('xml_path'))
        enabled=state['enabled'] if state is not None else False
        if state is None:data['native232_font_profile_supported']=False
        for index,run in enumerate(paragraph.get('runs',[])):
            text=run.get('text','');number=units(text);size=run.get('native_font_size_pt',run.get('font_size_pt'));bucket=None
            if size is not None and not float(size*2).is_integer():data['native232_font_profile_supported']=False
            if enabled and size is not None and size>0:
                if size<=minimum/2:bucket='tiny'
                elif size<minimum:bucket='small'
                elif size>maximum and (role!='textbox' or previous>100):bucket='large'
            item={'index':len(records),'bucket':bucket,'text':text,'utf16_units':number,'font_size_pt':size,'role':role,'native_font_enabled':enabled,'native_activation_ordinal':state['ordinal'] if state else None,'previous_textbox_utf16_units':previous if role=='textbox' else None,'location':{**location,'run':index+1,'run_xml_path':run.get('xml_path')}};records.append(item)
            if bucket:
                counts[bucket]+=number
                if role=='table' and bucket in {'small','large'}:counts['table_'+bucket]+=number
            previous+=number
        return previous
    for p in data.get('paragraphs',[]):visit(p,'body',{'kind':'docx_run','paragraph':p['index']+1,'xml_path':p.get('xml_path'),'style':p.get('style_name')})
    seen=set()
    for ti,table in enumerate(data.get('tables',[])):
        for ri,row in enumerate(table.get('rows',[])):
            for ci,cell in enumerate(row.get('cells',[])):
                for pi,p in enumerate(cell.get('paragraphs',[])):
                    key=p.get('xml_path',(ti,ri,ci,pi))
                    if key in seen:continue
                    seen.add(key);visit(p,'table',{'kind':'docx_table_run','table':ti+1,'row':ri+1,'cell':ci+1,'paragraph':pi+1,'xml_path':p.get('xml_path')})
    for label in data.get('labels',[]):
        previous=0
        for p in label.get('font_paragraphs',[]):previous=visit(p,'textbox',{'kind':'docx_textbox_run','shape_id':label.get('shape_id'),'xml_path':p.get('xml_path')},previous)
    return counts,records

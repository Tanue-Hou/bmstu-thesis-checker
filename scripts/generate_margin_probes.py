import argparse,json
from docx import Document
from docx.shared import Mm,Twips
from generate_format_expansion import OUT,SOURCE,record
p=argparse.ArgumentParser();p.add_argument('--mm',nargs='*',type=float,default=[]);p.add_argument('--twips',nargs='*',type=int,default=[]);p.add_argument('--manifest',required=True);p.add_argument('--axis',choices=['left','right','top','bottom'],default='left')
if __name__=='__main__':
    args=p.parse_args();manifest=OUT/(args.manifest+'.json')
    if manifest.exists():raise SystemExit('Frozen manifest exists')
    records=[]
    for mode,values in [('mm',args.mm),('twips',args.twips)]:
        for value in values:
            name='margin_'+('' if args.axis=='left' else args.axis+'_')+(str(value).replace('.','_') if mode=='mm' else 'twips'+str(value))
            path=OUT/(name+'.docx')
            if path.exists():raise SystemExit('Frozen input exists: '+name)
            doc=Document(SOURCE);setattr(doc.sections[0],args.axis+'_margin',Mm(value) if mode=='mm' else Twips(value));doc.save(path)
            records.append(record(path,{'axis':args.axis,args.axis+'_margin_'+mode+'_requested':value,args.axis+'_margin_twips':getattr(doc.sections[0],args.axis+'_margin').twips},SOURCE))
    manifest.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

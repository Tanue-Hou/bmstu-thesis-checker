import json,zipfile
from io import BytesIO
from PIL import Image
import fitz
from generate_format_expansion import OUT,record
if __name__=='__main__':
    if (OUT/'complex-pdf-inputs.json').exists():raise SystemExit('Frozen manifest exists')
    with zipfile.ZipFile(OUT/'complex_clean.docx') as z:chart=z.read('word/media/image1.png')
    records=[]
    for name,size,large in [('pdf_complex_clean',14,False),('pdf_complex_table7',7,False),('pdf_complex_image_above',14,True)]:
        doc=fitz.open(OUT/'pdf_clean.pdf');page=doc[0]
        for row in range(3):
            for col in range(2):
                x,y=72+col*190,365+row*30;page.draw_rect(fitz.Rect(x,y,x+190,y+30),color=(0,0,0),width=0.5)
                page.insert_text((x+8,y+20),'Метод анализа данных',fontname='TNR',fontsize=size)
        stream=chart
        if large:
            buf=BytesIO();Image.new('RGB',(4001,4000),'white').save(buf,format='PNG');stream=buf.getvalue()
        page.insert_image(fitz.Rect(72,490,500,690),stream=stream)
        path=OUT/(name+'.pdf');doc.save(path,garbage=4,deflate=True);doc.close()
        records.append(record(path,{'table_font_pt':size,'image_dimensions':[4001,4000] if large else [1600,800],'embedded_font':'Windows Times New Roman'}))
    (OUT/'complex-pdf-inputs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    doc=fitz.open(OUT/'pdf_complex_clean.pdf');doc[0].get_pixmap().save(str(OUT/'pdf_complex_clean.render.png'));doc.close()

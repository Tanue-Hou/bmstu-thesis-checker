"""Render anonymous fixtures through a private Word COM instance; no UI input."""
import hashlib,json
from pathlib import Path
import win32com.client
import fitz
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    base=ROOT/'evidence/v028/complex-repair';out=base/'rendered';out.mkdir(exist_ok=False)
    app=win32com.client.DispatchEx('Word.Application');app.Visible=False;app.DisplayAlerts=0
    records=[]
    try:
        for name in ['C01B','C02B','C01A']:
            source=(base/(name+'.docx')).resolve();before=sha(source);pdf=out/(name+'.pdf')
            doc=app.Documents.Open(str(source),ConfirmConversions=False,ReadOnly=True,AddToRecentFiles=False,Visible=False)
            try:doc.ExportAsFixedFormat(str(pdf),17,OpenAfterExport=False)
            finally:doc.Close(SaveChanges=0)
            assert sha(source)==before
            pages=[]
            with fitz.open(pdf) as rendered:
                for i,page in enumerate(rendered):
                    png=out/(name+f'-page{i+1}.png');page.get_pixmap(matrix=fitz.Matrix(1,1)).save(png)
                    pages.append({'page':i+1,'image':png.name,'sha256':sha(png),'text_characters':len(page.get_text()),'image_count':len(page.get_images()),'width_pt':page.rect.width,'height_pt':page.rect.height})
            records.append({'id':name,'input_sha256':before,'pdf':pdf.name,'pdf_sha256':sha(pdf),'pages':pages,'source_unchanged':True})
            print(json.dumps({'rendered':name,'pages':len(pages)}),flush=True)
    finally:app.Quit(SaveChanges=0)
    (out/'render-receipt.json').write_text(json.dumps({'engine':'Installed Microsoft Word via separate COM instance, read-only open and no-save close','cases':records,'limits':'Actual Word PDF rendering; visual acceptance is recorded separately; no keyboard/mouse control'},indent=2),encoding='utf-8')
if __name__=='__main__':main()

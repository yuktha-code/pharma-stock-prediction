from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'deps'))
import fitz
from PIL import Image
pdf=R.parent/'Thesis_Final.pdf'
out=R/'final_qa';out.mkdir(exist_ok=True)
doc=fitz.open(pdf)
thumbs=[]
for i,p in enumerate(doc):
    pix=p.get_pixmap(matrix=fitz.Matrix(.55,.55),alpha=False)
    path=out/f'page_{i+1:03d}.png';pix.save(path)
    im=Image.open(path).convert('RGB');im.thumbnail((220,310));thumbs.append(im.copy())
cols=5;rows=(len(thumbs)+cols-1)//cols
sheet=Image.new('RGB',(cols*230,rows*325),'white')
for i,im in enumerate(thumbs):sheet.paste(im,((i%cols)*230,(i//cols)*325))
sheet.save(out/'contact_sheet.png')
fulltext='\n'.join(p.get_text() for p in doc)
checks={'pages':len(doc),'text_chars':len(fulltext),'has_title':'Predicting Next-Quarter' in fulltext,'has_all_models':all(x in fulltext for x in ['Logistic Regression','Random Forest','Naive Bayes','Gradient Boosting','SVM','Neural Network / MLP','KNN','Decision Tree']),'cfa_mentions':sum(w.lower()=='cfa' for w in fulltext.split()),'empty_pages':[i+1 for i,p in enumerate(doc) if len(p.get_text().strip())<30],'figures':fulltext.count('Figure '),'tables':fulltext.count('Table ')}
(R/'final_qa_report.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))

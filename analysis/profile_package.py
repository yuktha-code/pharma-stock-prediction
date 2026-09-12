from pathlib import Path
import pandas as pd,json,sys
R=Path(__file__).resolve().parent; P=R/'friend_package/research project'
sys.path.insert(0,str(R/'deps'))
sys.path.insert(0,str(P))
from pipeline.lib.companies import COMPANIES,REGION_DIR
ds=pd.read_csv(P/'pipeline/outputs/dataset.csv')
out={'saved_dataset_shape':list(ds.shape),'date_range':[ds.quarter_end.min(),ds.quarter_end.max()], 'companies':[]}
for c in COMPANIES:
 d=P/'YUKTHA_CLEAN_2026-09-07'/REGION_DIR[c['region']]/c['folder']; records=[]
 for f in sorted((d/'02_MARKET_DATA/Daily').glob('*.csv')):
  a=pd.read_csv(f); records.append({'path':str(f.relative_to(P)), 'rows':len(a),'columns':list(a),'first':a.head(1).to_dict('records'),'last':a.tail(1).to_dict('records')})
 out['companies'].append({'company':c['folder'],'market_sources':records,'dataset_rows':int((ds.company_folder==c['folder']).sum())})
(R/'package_profile.json').write_text(json.dumps(out,indent=2,default=str))
for x in out['companies']: print(x['company'],x['dataset_rows'],[(r['path'].split('/')[-1],r['rows'],r['columns']) for r in x['market_sources']])
print(out['date_range'])


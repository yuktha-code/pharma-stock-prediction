from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'deps'));sys.path.insert(0,str(R/'friend_package/research project'))
import numpy as np,pandas as pd
from sklearn.metrics import confusion_matrix,roc_auc_score,accuracy_score,precision_score,recall_score,f1_score
from pipeline.lib.features import market_features
def independent(y,p,s):
    tn,fp,fn,tp=confusion_matrix(y,p,labels=[0,1]).ravel()
    # Pairwise AUC independent of roc_auc_score, including 0.5 credit for ties.
    a=np.asarray(s)[np.asarray(y)==1];b=np.asarray(s)[np.asarray(y)==0]
    auc=float(((a[:,None]>b).sum()+.5*(a[:,None]==b).sum())/(len(a)*len(b)))
    return dict(tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp),accuracy=accuracy_score(y,p),precision=precision_score(y,p,zero_division=0),recall=recall_score(y,p,zero_division=0),specificity=tn/(tn+fp),f1=f1_score(y,p,zero_division=0),roc_auc=auc)
P=R/'friend_package/research project/pipeline/outputs';saved=json.loads((P/'metrics.json').read_text());checks={}
for f in sorted((P/'predictions').glob('*.csv')):
    a=pd.read_csv(f);m=independent(a.y_true,a.y_pred,a.y_proba)
    errors={k:float(m[k]-saved[f.stem][k]) for k in ['accuracy','precision','recall','specificity','f1','roc_auc'] if not np.isclose(m[k],saved[f.stem][k],atol=1e-12)}
    checks[f.stem]={'n':len(a),'recalculated':m,'saved_metric_discrepancies':errors}
(R/'archived_predictions_verification.json').write_text(json.dumps(checks,indent=2))
q=pd.Timestamp('2023-03-31');price=pd.DataFrame({'date':pd.date_range('2022-01-01','2023-04-03'),'close':np.linspace(10,20,458)})
old=market_features(price,q,'close');altered=price.copy();altered.loc[altered.date>q,'close']*=100
new=market_features(altered,q,'close')
changed=[k for k in old if old[k]!=new[k] and old[k] is not None]
corrected=market_features(price[price.date<=q],q,'close');corrected2=market_features(altered[altered.date<=q],q,'close')
bug={'archived_future_perturbation_changed_features':changed,'corrected_future_perturbation_invariant':all(corrected[k]==corrected2[k] for k in corrected)}
(R/'feature_timing_regression.json').write_text(json.dumps(bug,indent=2))
print('Archived files verified:',len(checks),'metric discrepancies:',sum(bool(c['saved_metric_discrepancies']) for c in checks.values()));print(bug)
O=R/'final_run'
if (O/'tables/metrics.csv').exists() and (O/'selected_model.json').exists():
    allmetrics=pd.read_csv(O/'tables/metrics.csv');panel=pd.read_csv(O/'data/panel.csv');report=[]
    for f in sorted((O/'predictions').glob('*.csv')):
        name,split=f.stem.rsplit('_',1); model='majority_baseline' if name=='baseline' else name
        p=pd.read_csv(f);key=['company_folder','quarter_end'];truth=panel[panel.split==split][key+['target']]
        merged=p.merge(truth,on=key,validate='one_to_one');assert len(merged)==len(truth)==len(p);assert (merged.y_true==merged.target).all()
        m=independent(p.y_true,p.y_pred,p.score);row=allmetrics[(allmetrics.model==model)&(allmetrics.split==split)].iloc[0]
        assert all(np.isclose(m[k],row[k],atol=1e-12) for k in m)
        if name!='baseline': assert p.y_proba.between(0,1).all()
        report.append({'model':model,'split':split,'rows':len(p),'metrics_match':True,'pairwise_auc':m['roc_auc'],'panel_keys_truth_match':True})
    (O/'independent_verification.json').write_text(json.dumps(report,indent=2))
    print('Final prediction tables verified:',len(report))


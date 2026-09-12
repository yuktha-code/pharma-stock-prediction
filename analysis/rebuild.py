"""Corrected reconstruction from the supplied friend's package. No source mutation."""
from pathlib import Path
import sys,os,json,hashlib,platform,importlib.metadata,warnings
R=Path(__file__).resolve().parent; P=R/'friend_package/research project'; O=R/'final_run'
sys.path.insert(0,str(R/'deps')); sys.path.insert(0,str(P))
os.environ['MPLCONFIGDIR']=str(R/'mplconfig')
import pandas as pd,numpy as np
from pipeline.lib.companies import COMPANIES,REGION_DIR
from pipeline import _01_load_raw as loader, _02_clean_stock as cleaner, _04_features_target as build
from pipeline.lib.features import MARKET_FEATURE_NAMES,FUNDAMENTAL_FEATURE_NAMES,market_features,fundamental_features
FEATURES=MARKET_FEATURE_NAMES+FUNDAMENTAL_FEATURE_NAMES
for folder in ['data','stock','predictions','models','tables','figures']: (O/folder).mkdir(parents=True,exist_ok=True)
def save(name,obj): (O/name).write_text(json.dumps(obj,indent=2,default=str),encoding='utf-8')

def financials():
    """Re-read statement CSVs; normalize monetary units BEFORE alias selection."""
    all_long=[]; unit_log=[]
    for company in COMPANIES:
        d=loader.CLEAN_ROOT/REGION_DIR[company['region']]/company['folder']
        for typ in ['quarterly','annual']:
            for df in loader.load_company_financial_csvs(d,typ):
                source=df.source_file.iloc[0]; df['company_folder']=company['folder']; df['period_type']=typ
                tidy=build._normalize_financial_long(df)
                if tidy.empty: continue
                if 'Unnamed: 0' in df and (df['Unnamed: 0']=='Period Ended').any():
                    marker=df.loc[df['Unnamed: 0']=='Period Ended'].iloc[0]
                    ur=df.loc[df['Unnamed: 0']=='Units']; cr=df.loc[df['Unnamed: 0']=='Currency']
                    lookup={}
                    for col in df.columns:
                        if not str(col).startswith('Unnamed: ') or col=='Unnamed: 0':continue
                        dt=build._parse_date_maybe(marker.get(col))
                        if dt is None: continue
                        unit=str(ur.iloc[0].get(col,'') if len(ur) else '').lower()
                        factor={'thousands':1e3,'millions':1e6,'billions':1e9,'actual':1,'units':1}.get(unit)
                        currency=str(cr.iloc[0].get(col,'') if len(cr) else '')
                        lookup[dt]=(factor,currency,unit)
                    tidy['factor']=tidy.period_end.map(lambda x:lookup.get(x,(None,'',''))[0])
                    tidy['currency']=tidy.period_end.map(lambda x:lookup.get(x,(None,'',''))[1])
                    unit_log.append({'company':company['folder'],'source':source,'format':'Capital IQ','units':sorted({x[2] for x in lookup.values()}),'unknown_unit_rows':int(tidy.factor.isna().sum())})
                elif 'period_end' in df and df.period_end.notna().any():
                    # Derived company extracts have per-row units. Preserve only known scales.
                    unit=str(df.get('units',pd.Series([''])).dropna().iloc[0] if df.get('units',pd.Series(dtype=str)).notna().any() else '').lower()
                    factor=1e6 if 'million' in unit else 1e3 if 'thousand' in unit else 1 if unit in ['eur','cny','inr','usd','units','actual'] else None
                    tidy['factor']=factor; tidy['currency']=str(df.get('currency',pd.Series(['unknown'])).iloc[0])
                    unit_log.append({'company':company['folder'],'source':source,'format':'derived','units':[unit],'unknown_unit_rows':len(tidy) if factor is None else 0})
                else:
                    # yfinance monetary statement values are base-currency amounts.
                    tidy['factor']=1.; tidy['currency']='source reporting currency'
                    unit_log.append({'company':company['folder'],'source':source,'format':'date-header supplement','units':['base currency'],'unknown_unit_rows':0})
                tidy['value']=tidy.value*tidy.factor
                all_long.append(tidy)
    long=pd.concat(all_long,ignore_index=True)
    long.to_csv(O/'data/financial_long.csv',index=False)
    save('financial_units.json',unit_log)
    # Stable source-order tie resolution, retain original alias priority.
    long=long.sort_values(['company_folder','source_file','period_end','line_item'],kind='stable')
    wide=build._pivot_fundamentals(long)
    wide['publication_date']=pd.NaT
    wide.to_csv(O/'data/fundamentals.csv',index=False)
    return wide

def stocks():
    result={}; log=[]
    for c in COMPANIES:
        d=loader.CLEAN_ROOT/REGION_DIR[c['region']]/c['folder']
        frames=loader.load_company_daily_csvs(d)
        if not frames:
            log.append({'company':c['folder'],'status':'excluded: no daily CSV in package loader path'});continue
        block=cleaner.select_canonical_block(c['folder'],frames,c['region'])
        block=cleaner._normalize_columns(block)
        col='adj_close' if 'adj_close' in block and block.adj_close.notna().any() else 'close'
        # Preserve local calendar dates; UTC conversion can move midnight backwards.
        block['date']=pd.to_datetime(block.date.astype(str).str[:10],errors='coerce')
        block['price']=pd.to_numeric(block[col],errors='coerce')
        invalid=block.date.isna()|~np.isfinite(block.price)|(block.price<=0)
        block=block.loc[~invalid].copy()
        block['volume']=pd.to_numeric(block.get('volume',np.nan),errors='coerce')
        # Prefer the longest valid source within the selected canonical price basis.
        coverage=block.groupby('source_file').date.nunique().to_dict()
        block['_coverage']=block.source_file.map(coverage)
        block=block.sort_values(['date','_coverage','source_file'],ascending=[True,False,True],kind='stable')
        conflicts=block.groupby('date').price.agg(['min','max'])
        conflicts=conflicts[~np.isclose(conflicts['min'],conflicts['max'],rtol=1e-5)]
        s=block.drop_duplicates('date')[['date','price','volume','source_file']].rename(columns={'price':'close'})
        s=s.sort_values('date').reset_index(drop=True)
        s.to_csv(O/'stock'/f"{c['folder']}.csv",index=False);result[c['folder']]=s
        log.append({'company':c['folder'],'region':c['region'],'status':'included','price_basis':col,'rows':len(s),'start':s.date.min(),'end':s.date.max(),'invalid_price_rows_removed':int(invalid.sum()),'conflicting_dates':len(conflicts),'source_coverage':coverage,'largest_absolute_daily_return':s.close.pct_change().abs().max()})
    save('stock_decisions.json',log); return result

def panel():
    fin=financials(); series=stocks(); rows=[]; exclusions=[]
    region={c['folder']:c['region'] for c in COMPANIES}
    for company,s in series.items():
        qends=pd.date_range(s.date.min(),s.date.max(),freq='QE')
        f=fin[fin.company_folder==company].copy()
        f['available_from']=f.period_end+pd.to_timedelta(f.period_type.map({'quarterly':61,'annual':121}),unit='D')
        for q,nq in zip(qends[:-1],qends[1:]):
            eligible=s[s.date<=q]; future=s[s.date<=nq]; a,b=eligible.iloc[-1],future.iloc[-1]
            if (q-a.date).days>10 or (nq-b.date).days>10:
                exclusions.append({'company':company,'quarter_end':q,'reason':'price endpoint more than 10 calendar days stale'});continue
            # Passing only past observations also neutralizes the archived q+1 price bug.
            feats=market_features(eligible,as_of=q,price_col='close')
            candidates=f[(f.available_from<=q)&((q-f.period_end).dt.days<=f.period_type.map({'quarterly':200,'annual':550}))]
            fr=None if candidates.empty else candidates.sort_values(['period_end','period_type'],kind='stable').iloc[-1]
            fund=fundamental_features(fr.to_dict()) if fr is not None else {c:np.nan for c in FUNDAMENTAL_FEATURE_NAMES}
            forward=float(b.close/a.close-1)
            split='train' if q<pd.Timestamp('2022-01-01') else 'validation' if q<pd.Timestamp('2024-01-01') else 'test'
            # Purge fitting/selection labels ending on or after the next partition boundary.
            if (split=='train' and nq>=pd.Timestamp('2022-01-01')) or (split=='validation' and nq>=pd.Timestamp('2024-01-01')):
                split='purged'
            row={'company_folder':company,'region':region[company],'quarter_end':q,'label_end':nq,'split':split,'price_t':a.close,'price_next':b.close,'price_date':a.date,'label_price_date':b.date,'next_return':forward,'target':int(forward>0),'financial_period':fr.period_end if fr is not None else pd.NaT,'available_from':fr.available_from if fr is not None else pd.NaT,'financial_frequency':fr.period_type if fr is not None else None,**feats,**fund}
            rows.append(row)
        print('Built',company,flush=True)
    ds=pd.DataFrame(rows).sort_values(['quarter_end','company_folder']).reset_index(drop=True)
    ds[FEATURES]=ds[FEATURES].replace([np.inf,-np.inf],np.nan)
    ds.to_csv(O/'data/panel.csv',index=False)
    pd.DataFrame(exclusions).to_csv(O/'data/excluded_rows.csv',index=False)
    return ds

def metrics(y,p,s):
    from sklearn.metrics import confusion_matrix,accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,balanced_accuracy_score
    tn,fp,fn,tp=confusion_matrix(y,p,labels=[0,1]).ravel()
    return {'n':len(y),'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp),'accuracy':accuracy_score(y,p),'precision':precision_score(y,p,zero_division=0),'recall':recall_score(y,p,zero_division=0),'specificity':tn/(tn+fp),'f1':f1_score(y,p,zero_division=0),'balanced_accuracy':balanced_accuracy_score(y,p),'roc_auc':roc_auc_score(y,s),'predicted_positive_rate':float(np.mean(p))}

def train(ds):
    from sklearn.base import clone
    from sklearn.preprocessing import StandardScaler
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import roc_curve
    from threadpoolctl import threadpool_limits
    import joblib
    from pipeline._05_split_train import MODELS
    parts={s:ds[ds.split==s].copy() for s in ['train','validation','test']}
    tr=parts['train']; active=[c for c in FEATURES if tr[c].notna().any()]
    drops={c:'all missing in training' for c in FEATURES if c not in active}
    # Exact duplicate definitions are removed using training data only.
    for c in active.copy():
        earlier=[x for x in active[:active.index(c)] if tr[c].equals(tr[x])]
        if earlier: active.remove(c);drops[c]='identical to '+earlier[0]
    med=tr[active].median(); low=tr[active].quantile(.01); high=tr[active].quantile(.99)
    X={s:p[active].fillna(med).clip(low,high,axis=1) for s,p in parts.items()}
    scaler=StandardScaler().fit(X['train'])
    scaled={s:pd.DataFrame(scaler.transform(x),columns=active,index=x.index) for s,x in X.items()}
    specs={}; results=[]; fitted={}; warning_log=[]
    save('preprocessing.json',{'active_features':active,'dropped':drops,'medians':med.to_dict(),'lower_01':low.to_dict(),'upper_99':high.to_dict(),'scaler_mean':dict(zip(active,scaler.mean_)),'scaler_scale':dict(zip(active,scaler.scale_)),'fit_split':'train','fit_rows':len(tr)})
    # No test-driven model/feature/threshold tuning. Fixed package estimator specifications.
    save('selection_protocol.json',{'parameters':'fixed from supplied pipeline._05_split_train.MODELS','selection':'highest validation balanced accuracy; then validation ROC-AUC; then model name','threshold':'native estimator predict; SVM decision threshold 0, others class argmax','refit':'none; all estimators fitted on train only','seed':42,'corrections':['past-only feature prices','local calendar dates','valid positive prices','retain volume','normalize financial units','staleness guards 200/550 days','purge boundary label quarters','drop exact duplicate features','training-only median, 1/99% clipping and standardization','training-majority baseline']})
    for name,base in MODELS.items():
        model=clone(base);specs[name]=model.get_params(deep=True)
        with warnings.catch_warnings(record=True) as caught,threadpool_limits(limits=2):
            warnings.simplefilter('always');model.fit(scaled['train'],tr.target)
        warning_log.extend([{'model':name,'warning':str(w.message)} for w in caught])
        assert list(model.classes_)==[0,1]
        for split in ['validation','test']:
            p=parts[split];xx=scaled[split]
            pred=model.predict(xx);proba=model.predict_proba(xx)[:,1]
            score=model.decision_function(xx) if name=='svm' else proba
            kind='decision_function_positive_class_1' if name=='svm' else 'probability_class_1'
            out=p[['company_folder','quarter_end','label_end','target']].rename(columns={'target':'y_true'}).copy()
            out['y_pred']=pred;out['y_proba']=proba;out['score']=score;out['score_kind']=kind
            out.to_csv(O/'predictions'/f'{name}_{split}.csv',index=False)
            results.append({'model':name,'split':split,**metrics(p.target,pred,score)})
            fpr,tpr,threshold=roc_curve(p.target,score)
            pd.DataFrame({'fpr':fpr,'tpr':tpr,'threshold':threshold}).to_csv(O/'tables'/f'roc_{name}_{split}.csv',index=False)
        joblib.dump({'estimator':model,'features':active,'median':med,'lower':low,'upper':high,'scaler':scaler},O/'models'/f'{name}.joblib')
        fitted[name]=model
        print('Fitted',name,flush=True)
        pd.DataFrame(results).to_csv(O/'tables/metrics.csv',index=False)
    val=pd.DataFrame(results).query("split=='validation'").sort_values(['balanced_accuracy','roc_auc','model'],ascending=[False,False,True])
    winner=val.iloc[0].model
    save('model_specs.json',specs);save('training_warnings.json',warning_log)
    save('selected_model.json',{'model':winner,'reason':'highest validation balanced accuracy, AUC tie-break','validation_ranking':val.to_dict('records')})
    majority=int(tr.target.mean()>.5)
    for split,p in parts.items():
        if split=='train':continue
        out=p[['company_folder','quarter_end','target']].rename(columns={'target':'y_true'}).copy()
        out['y_pred']=majority;out['score']=tr.target.mean();out.to_csv(O/'predictions'/f'baseline_{split}.csv',index=False)
        results.append({'model':'majority_baseline','split':split,**metrics(p.target,out.y_pred,out.score)})
    pd.DataFrame(results).to_csv(O/'tables/metrics.csv',index=False)
    pd.DataFrame([{'split':s,'rows':len(p),'positive':int(p.target.sum()),'negative':int((p.target==0).sum()),'start':p.quarter_end.min(),'end':p.quarter_end.max(),'companies':p.company_folder.nunique()} for s,p in parts.items()]).to_csv(O/'tables/split_summary.csv',index=False)
    missing=pd.DataFrame({s:p[FEATURES].isna().mean() for s,p in parts.items()});missing.to_csv(O/'tables/feature_missingness.csv',index_label='feature')
    pd.DataFrame({'feature':active,'coefficient':fitted['logistic_regression'].coef_[0]}).to_csv(O/'tables/logistic_coefficients.csv',index=False)
    for name in ['random_forest','gradient_boosting','decision_tree']:
        pd.DataFrame({'feature':active,'importance':fitted[name].feature_importances_}).to_csv(O/'tables'/f'{name}_importance.csv',index=False)
    with threadpool_limits(limits=2):
        imp=permutation_importance(fitted[winner],scaled['validation'],parts['validation'].target,scoring='balanced_accuracy',n_repeats=10,random_state=42,n_jobs=1)
    pd.DataFrame({'feature':active,'mean_decrease':imp.importances_mean,'std':imp.importances_std}).to_csv(O/'tables/selected_validation_permutation.csv',index=False)
    checks={'duplicate_company_quarters':int(ds.duplicated(['company_folder','quarter_end']).sum()),'future_price_feature_rows':int((ds.price_date>ds.quarter_end).sum()),'financial_availability_violations':int((ds.available_from>ds.quarter_end).sum()),'target_formula_mismatches':int((ds.target!=(ds.price_next/ds.price_t-1>0).astype(int)).sum()),'train_label_boundary_violations':int((tr.label_end>=pd.Timestamp('2022-01-01')).sum()),'validation_label_boundary_violations':int((parts['validation'].label_end>=pd.Timestamp('2024-01-01')).sum()),'purged_rows':int((ds.split=='purged').sum()),'post_preprocess_nonfinite':int(sum((~np.isfinite(x.values)).sum() for x in scaled.values())),'same_test_keys_all_models':True,'preprocessing_fit_split':'train','parameter_search_performed':False,'point_in_time_vintage_verified':False,'market_feature_future_perturbation_test':'pending separate test'}
    save('leakage_checks.json',checks)
    env={'python':sys.version,'platform':platform.platform(),'packages':{p:importlib.metadata.version(p) for p in ['pandas','numpy','scikit-learn','scipy','pyarrow','matplotlib','joblib','threadpoolctl']}}
    save('environment.json',env)
    (O/'requirements.txt').write_text('\n'.join(k+'=='+v for k,v in env['packages'].items())+'\n')

if __name__=='__main__':
    if '--train-only' in sys.argv:
        data=pd.read_csv(O/'data/panel.csv',parse_dates=['quarter_end','label_end','price_date','label_price_date','financial_period','available_from'])
    else:data=panel()
    train(data)
    print('COMPLETE',flush=True)


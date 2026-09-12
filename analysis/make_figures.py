from pathlib import Path
import sys,os,json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'deps'));os.environ['MPLCONFIGDIR']=str(R/'mplconfig')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,pandas as pd
O=R/'final_run';F=O/'figures';F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
names={'logistic_regression':'Logistic regression','random_forest':'Random forest','naive_bayes':'Naive Bayes','gradient_boosting':'Gradient boosting','svm':'SVM','neural_network':'Neural network / MLP','knn':'KNN','decision_tree':'Decision tree','majority_baseline':'Majority baseline'}
short=['LR','RF','NB','GB','SVM','MLP','KNN','DT'];models=list(names)[:-1]
m=pd.read_csv(O/'tables/metrics.csv');test=m[m.split=='test'].set_index('model').loc[models];val=m[m.split=='validation'].set_index('model').loc[models]
def save(fig,name):fig.savefig(F/(name+'.png'),bbox_inches='tight',facecolor='white');fig.savefig(F/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
for model in models:
    row=test.loc[model];cm=np.array([[row.tn,row.fp],[row.fn,row.tp]],int)
    fig,axs=plt.subplots(1,2,figsize=(6.4,2.45),gridspec_kw={'width_ratios':[1,1.18]})
    ax=axs[0];ax.imshow(cm,cmap='Blues',vmin=0,vmax=151)
    for i in range(2):
        for j in range(2):ax.text(j,i,f"{[['TN','FP'],['FN','TP']][i][j]}\n{cm[i,j]}",ha='center',va='center',color='white' if cm[i,j]>85 else '#18263b',fontsize=12)
    ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['Non-up','Up'],yticklabels=['Non-up','Up'],xlabel='Predicted class',ylabel='Actual class',title='Held-out confusion matrix')
    r=pd.read_csv(O/'tables'/f'roc_{model}_test.csv');ax=axs[1];ax.plot(r.fpr,r.tpr,color='#244f73',lw=1.7,label=f'AUC = {row.roc_auc:.3f}');ax.plot([0,1],[0,1],'--',color='0.65',lw=.8);ax.scatter([1-row.specificity],[row.recall],c='#ad6741',s=25,label='Saved decision rule');ax.set(xlim=(0,1),ylim=(0,1),xlabel='False-positive rate',ylabel='True-positive rate',title='ROC from continuous scores');ax.legend(fontsize=8,loc='lower right');fig.tight_layout(w_pad=2.2);save(fig,model)
fig,axs=plt.subplots(1,3,figsize=(6.5,2.9))
for ax,metric,title in zip(axs,['accuracy','balanced_accuracy','roc_auc'],['Accuracy','Balanced accuracy','ROC-AUC']):
    ax.barh(short,test[metric],color=['#9cabb8' if x!='SVM' else '#245876' for x in short]);base=.5785440613 if metric=='accuracy' else .5;ax.axvline(base,color='#9e5636',ls='--',lw=1);ax.set(xlim=(0,1),title=title);ax.invert_yaxis();ax.tick_params(axis='y',length=0)
fig.tight_layout();save(fig,'comparison')
fig,ax=plt.subplots(figsize=(6.4,3.4))
for model in models:
    r=pd.read_csv(O/'tables'/f'roc_{model}_test.csv');ax.plot(r.fpr,r.tpr,lw=1.6 if model=='svm' else 1,label=f"{names[model]} ({test.loc[model,'roc_auc']:.3f})")
ax.plot([0,1],[0,1],'--',c='0.65',lw=.8);ax.set(xlim=(0,1),ylim=(0,1),xlabel='False-positive rate',ylabel='True-positive rate');ax.legend(loc='center left',bbox_to_anchor=(1.01,.5),fontsize=8,frameon=False);save(fig,'roc_comparison')
fig,ax=plt.subplots(figsize=(6.4,2.9));x=np.arange(8);w=.26
for i,c in enumerate(['precision','recall','specificity']):ax.bar(x+(i-1)*w,test[c],w,label=c.capitalize(),color=['#345f7d','#82a7b0','#b98767'][i])
ax.set(xticks=x,xticklabels=short,ylim=(0,1),ylabel='Metric');ax.legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,1.18),frameon=False);fig.tight_layout();save(fig,'class_tradeoffs')
missing=pd.read_csv(O/'tables/feature_missingness.csv').set_index('feature');active=json.loads((O/'preprocessing.json').read_text())['active_features']
fig,ax=plt.subplots(figsize=(6.4,3.9));a=missing.loc[active];im=ax.imshow(a.values,aspect='auto',cmap='Blues',vmin=0,vmax=1);ax.set(xticks=range(3),xticklabels=['Train','Validation','Test'],yticks=range(len(a)),yticklabels=[x.replace('_',' ') for x in a.index]);ax.tick_params(length=0)
for i in range(len(a)):
    for j in range(3):ax.text(j,i,f'{a.iloc[i,j]:.0%}',ha='center',va='center',fontsize=8,color='white' if a.iloc[i,j]>.55 else '#18263b')
fig.colorbar(im,ax=ax,shrink=.8,label='Missing fraction');fig.tight_layout();save(fig,'missingness')
p=pd.read_csv(O/'tables/selected_validation_permutation.csv').sort_values('mean_decrease');fig,ax=plt.subplots(figsize=(6.4,3.8));ax.barh(p.feature.str.replace('_',' '),p.mean_decrease,xerr=p['std'],color='#587e91',error_kw={'elinewidth':.7,'capsize':2});ax.axvline(0,color='0.5',lw=.8);ax.set(xlabel='Decrease in validation balanced accuracy\n(mean ± SD over 10 permutations)');fig.tight_layout();save(fig,'selected_importance')
coef=pd.read_csv(O/'tables/logistic_coefficients.csv').sort_values('coefficient');fig,ax=plt.subplots(figsize=(6.4,3.6));ax.barh(coef.feature.str.replace('_',' '),coef.coefficient,color=['#a56b4a' if v<0 else '#42728b' for v in coef.coefficient]);ax.axvline(0,c='0.4',lw=.6);ax.set(xlabel='Log-odds coefficient per training standard deviation');fig.tight_layout();save(fig,'logistic_coefficients')
ds=pd.read_csv(O/'data/panel.csv');counts=ds[ds.split!='purged'].groupby(['quarter_end','region']).size().unstack(fill_value=0);fig,ax=plt.subplots(figsize=(6.4,2.6));dates=pd.to_datetime(counts.index);ax.stackplot(dates,counts.IN,counts.NON_IN,labels=['Indian','Non-Indian'],colors=['#446e86','#9cb3bc']);ax.axvline(pd.Timestamp('2022-01-01'),c='#a16d45',lw=1);ax.axvline(pd.Timestamp('2024-01-01'),c='#a16d45',lw=1);ax.set(ylabel='Company observations',ylim=(0,31));ax.legend(loc='upper left',frameon=False);fig.tight_layout();save(fig,'coverage')
print('Saved',len(list(F.glob('*.png'))),'figures')

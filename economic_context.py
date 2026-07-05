#!/usr/bin/env python3
"""Economic-context analysis: how the macro environment (rates, equity, vol, credit)
shaped (A) deal OCCURRENCE/timing and (B) deal STRUCTURE (size, public-vs-private,
completion). Neural net for the per-deal structure models, paired with permutation
importance + partial-dependence so the IMPACT is readable, with honest CV."""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import KFold, cross_val_predict, cross_val_score
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.inspection import permutation_importance

# ---------- macro monthly panel ----------
def load(id, how='mean'):
    s=pd.read_csv(f'macro_{id}.csv',parse_dates=['observation_date'],na_values='.')
    s=s.set_index('observation_date')[id].astype(float)
    return s.resample('MS').mean() if how=='mean' else s.resample('MS').last()
m=pd.DataFrame({
    'fedfunds':load('FEDFUNDS'),'dgs10':load('DGS10'),'vix':load('VIXCLS'),
    'baa_spread':load('BAA10Y'),'sp500':load('SP500','last')}).ffill()
m['yield_curve']=m['dgs10']-m['fedfunds']           # <0 = inverted (recession signal)
m['rate_chg_12m']=m['fedfunds'].diff(12)            # hiking(+)/cutting(-) regime
m['sp_ret_6m']=m['sp500'].pct_change(6)             # equity momentum / valuation tailwind
m['sp_ret_12m']=m['sp500'].pct_change(12)
MFEATS=['fedfunds','dgs10','vix','baa_spread','yield_curve','rate_chg_12m','sp_ret_6m','sp_ret_12m']

# ---------- deals ----------
d=pd.read_csv('jetfirm_all_deals_82.csv')
d['dateann']=pd.to_datetime(d['dateann'],errors='coerce')
d=d.dropna(subset=['dateann'])
d['month']=d['dateann'].dt.to_period('M').dt.to_timestamp()
d['dv']=pd.to_numeric(d['deal_value'],errors='coerce')
d=d[(d['month']>=m.index.min())&(d['month']<=m.index.max())]
d=d.join(m,on='month')
print(f"deals with macro context: {len(d)}  ({d['dateann'].min().date()} .. {d['dateann'].max().date()})")

# =================================================================
print("\n############ A. DEAL OCCURRENCE & TIMING vs MACRO ############")
mon=d.groupby('month').agg(n=('tgt','size'),val=('dv','sum'),
                           n_large=('dv',lambda x:(x>=1000).sum()),
                           n_public=('tpublic',lambda x:(x=='Public').sum())).reindex(m.index).fillna(0)
mon=mon.join(m)
print("\nAnnual deal flow vs rate/vol regime:")
yr=mon.groupby(mon.index.year).agg(deals=('n','sum'),val_B=('val',lambda x:x.sum()/1000),
        large=('n_large','sum'),avg_ffr=('fedfunds','mean'),avg_vix=('vix','mean'),sp_ret=('sp_ret_12m','mean'))
print(yr.round(1).to_string())

print("\nCorrelation of monthly deal COUNT with macro (Pearson r):")
for f in MFEATS:
    r=mon['n'].corr(mon[f]); print(f"  {f:14} r={r:+.2f}")
# regression (standardized) for partial impact
from numpy.linalg import lstsq
mon_c=mon.dropna(subset=MFEATS)
Xo=StandardScaler().fit_transform(mon_c[MFEATS].values); yo=mon_c['n'].values
Xo1=np.column_stack([np.ones(len(Xo)),Xo])
beta,_,_,_=lstsq(Xo1,yo,rcond=None)
pred=Xo1@beta; r2=1-((yo-pred)**2).sum()/((yo-yo.mean())**2).sum()
print(f"\nMulti-macro OLS on monthly deal count (standardized betas, R²={r2:.2f}):")
for f,b in sorted(zip(MFEATS,beta[1:]),key=lambda x:-abs(x[1])):
    print(f"  {f:14} beta={b:+.2f} deals/sd")

# =================================================================
print("\n############ B. DEAL STRUCTURE vs MACRO (neural net + importance) ############")
ds=d.dropna(subset=MFEATS).copy()
X=ds[MFEATS].values
sc=StandardScaler().fit(X); Xs=sc.transform(X)
cv=KFold(5,shuffle=True,random_state=7)

def nn_reg(y,name):
    yv=np.asarray(y,float); mask=~np.isnan(yv); Xx,yy=Xs[mask],yv[mask]
    mlp=MLPRegressor(hidden_layer_sizes=(16,8),alpha=1.0,max_iter=3000,early_stopping=True,random_state=7)
    lin=LinearRegression()
    r2_nn=cross_val_score(mlp,Xx,yy,cv=cv,scoring='r2').mean()
    r2_lin=cross_val_score(lin,Xx,yy,cv=cv,scoring='r2').mean()
    mlp.fit(Xx,yy)
    imp=permutation_importance(mlp,Xx,yy,n_repeats=20,random_state=7,scoring='r2')
    print(f"\n[{name}]  CV R²: NN={r2_nn:+.3f}  linear={r2_lin:+.3f}  (N={mask.sum()})")
    top=sorted(zip(MFEATS,imp.importances_mean),key=lambda x:-x[1])[:5]
    # direction via linear sign
    lin.fit(Xx,yy); signs=dict(zip(MFEATS,lin.coef_))
    for f,v in top:
        if v<=0: continue
        print(f"    {f:14} importance={v:.3f}  direction={'+' if signs[f]>0 else '-'} (sd→{signs[f]:+.2f})")

def nn_clf(y,name):
    yv=np.asarray(y,float); mask=~np.isnan(yv); Xx,yy=Xs[mask],yv[mask].astype(int)
    if len(np.unique(yy))<2: print(f"\n[{name}] degenerate"); return
    mlp=MLPClassifier(hidden_layer_sizes=(16,8),alpha=1.0,max_iter=3000,early_stopping=True,random_state=7)
    log=LogisticRegression(max_iter=1000,class_weight='balanced')
    auc_nn=cross_val_score(mlp,Xx,yy,cv=cv,scoring='roc_auc').mean()
    auc_log=cross_val_score(log,Xx,yy,cv=cv,scoring='roc_auc').mean()
    mlp.fit(Xx,yy)
    imp=permutation_importance(mlp,Xx,yy,n_repeats=20,random_state=7,scoring='roc_auc')
    log.fit(Xx,yy); signs=dict(zip(MFEATS,log.coef_[0]))
    print(f"\n[{name}]  CV ROC-AUC: NN={auc_nn:.3f}  logistic={auc_log:.3f}  base={yy.mean():.2f}  (N={len(yy)})")
    for f,v in sorted(zip(MFEATS,imp.importances_mean),key=lambda x:-x[1])[:5]:
        if v<=0: continue
        print(f"    {f:14} importance={v:.3f}  direction={'+' if signs[f]>0 else '-'} (logit→{signs[f]:+.2f})")

# (a) deal size
nn_reg(np.log10(ds['dv'].where(ds['dv']>0)), "DEAL SIZE  log10($M)")
# (b) public target
nn_clf((ds['tpublic']=='Public').astype(float), "PUBLIC TARGET  P(public)")
# (c) private target
nn_clf((ds['tpublic']=='Priv.').astype(float), "PRIVATE TARGET  P(private)")
# (d) withdrawal among resolved
res=ds[ds['statuscode'].isin(['C','W','DR'])].copy()
Xs_bak=Xs; Xs=sc.transform(res[MFEATS].values)
nn_clf((res['statuscode'].isin(['W','DR'])).astype(float).values, "WITHDRAWN | resolved")
Xs=Xs_bak

print("\n(Done. Structure models conditioned on the SAME macro context the deals were announced in.)")

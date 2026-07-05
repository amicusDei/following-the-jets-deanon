#!/usr/bin/env python3
"""Combined model: flight-pattern + economic-context features in ONE deal-vs-non-deal NN.
Ablation (flight-only / macro-only / combined) under grouped-by-firm CV, for two
negative schemes:
  (M) date-matched   negatives drawn from the deal-date pool  -> macro distributions
      identical across classes => isolates 'can macro help tell TARGET from non-target?'
  (U) calendar-uniform negatives drawn uniformly over coverage -> macro can signal the
      deal-prone ERA => shows the 'when' contribution of economic context.
"""
import csv, re, math, json, random
import numpy as np, pandas as pd
import airportsdata
from collections import defaultdict
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupShuffleSplit

random.seed(7); np.random.seed(7)
R_KM=100.0; DAY=86400.0
APT=airportsdata.load('ICAO')
def hav(a,b,c,d):
    r=6371.0;p1,p2=math.radians(a),math.radians(c);dp=math.radians(c-a);dl=math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(x))

# ---------- macro panel ----------
def load(id,how='mean'):
    s=pd.read_csv(f'macro_{id}.csv',parse_dates=['observation_date'],na_values='.').set_index('observation_date')[id].astype(float)
    return s.resample('MS').mean() if how=='mean' else s.resample('MS').last()
M=pd.DataFrame({'fedfunds':load('FEDFUNDS'),'dgs10':load('DGS10'),'vix':load('VIXCLS'),
                'baa_spread':load('BAA10Y'),'sp500':load('SP500','last')}).ffill()
M['yield_curve']=M['dgs10']-M['fedfunds']; M['rate_chg_12m']=M['fedfunds'].diff(12)
M['sp_ret_6m']=M['sp500'].pct_change(6); M['sp_ret_12m']=M['sp500'].pct_change(12)
MF=['fedfunds','dgs10','vix','baa_spread','yield_curve','rate_chg_12m','sp_ret_6m','sp_ret_12m']
Midx=M.index.values.astype('datetime64[s]').astype(float)
Mmat=M[MF].values
def macro_at(epoch):
    i=np.searchsorted(Midx,epoch,side='right')-1
    i=max(0,min(i,len(Mmat)-1)); v=Mmat[i]
    return [x if np.isfinite(x) else 0.0 for x in v]

# ---------- flights ----------
flights=defaultdict(list)
for r in csv.DictReader(open('dealmaker_flight_activity.csv')):
    a=APT.get(r['arr_airport']) if r['arr_airport'] else None
    if not a: continue
    try: t=float(r['lastseen'])
    except: continue
    flights[r['ticker']].append((t,a['lat'],a['lon']))
for tk in flights: flights[tk].sort()
firm_total={tk:len(v) for tk,v in flights.items()}
cov={tk:(v[0][0],v[-1][0]) for tk,v in flights.items() if v}

deals=json.load(open('nn_deals_anchored.json'))
for d in deals: d['ann_e']=datetime.strptime(d['ann'],'%Y-%m-%d').timestamp()
all_dates=[d['ann_e'] for d in deals]
LOCS={}
for d in deals: LOCS[(round(d['lat'],3),round(d['lon'],3))]=(d['lat'],d['lon'])
LOCS=list(LOCS.values())
loc_pop={}
for (la,lo) in LOCS:
    loc_pop[(round(la,3),round(lo,3))]=sum(1 for tk,v in flights.items() if any(hav(la,lo,fa,fo)<=R_KM for (_,fa,fo) in v))

def flight_feats(tk,lat,lon,ann_e):
    ev=flights.get(tk,[]); w90=ann_e-90*DAY;w180=ann_e-180*DAY;w30=ann_e-30*DAY
    v90=v180=v30=v_before=0; last=None; mind=1e9
    for (t,la,lo) in ev:
        near=hav(lat,lon,la,lo)<=R_KM
        if near:
            if t<ann_e: v_before+=1; last=t if last is None else max(last,t)
            if w90<=t<ann_e: v90+=1
            if w180<=t<ann_e: v180+=1
            if w30<=t<ann_e: v30+=1
        if t<ann_e: mind=min(mind,hav(lat,lon,la,lo))
    fw90=sum(1 for (t,_,_) in ev if w90<=t<ann_e); ftot=firm_total.get(tk,0)
    rec=(ann_e-last)/DAY if last else 1000.0
    return [v90,v180,v30,v_before,1.0 if v_before>0 else 0.0,min(mind,500.0),min(rec,1000.0),
            math.log1p(ftot),math.log1p(fw90),v90/(fw90+1),v_before/(ftot+1),
            loc_pop.get((round(lat,3),round(lon,3)),0)]

def build(scheme, neg_per_pos=3):
    X=[];y=[];grp=[]
    for d in deals:
        X.append(flight_feats(d['ticker'],d['lat'],d['lon'],d['ann_e'])+macro_at(d['ann_e']))
        y.append(1); grp.append(d['ticker'])
    for d in deals:
        tk=d['ticker']; made=0;tries=0
        while made<neg_per_pos and tries<60:
            tries+=1
            la,lo=random.choice(LOCS)
            if scheme=='M': ann=random.choice(all_dates)
            else:
                c0,c1=cov.get(tk,(all_dates[0],all_dates[-1])); ann=random.uniform(c0,c1)
            if round(la,3)==round(d['lat'],3) and abs(ann-d['ann_e'])<365*DAY: continue
            X.append(flight_feats(tk,la,lo,ann)+macro_at(ann)); y.append(0); grp.append(tk); made+=1
    return np.array(X,float),np.array(y),np.array(grp)

FL=slice(0,12); MA=slice(12,20)
def ablate(X,y,grp,cols,seeds=25):
    aucs_nn=[];aucs_lr=[]
    for s in range(seeds):
        tr,te=next(GroupShuffleSplit(1,test_size=1/3,random_state=s).split(X,y,groups=grp))
        sc=StandardScaler().fit(X[tr][:,cols])
        Xtr,Xte=sc.transform(X[tr][:,cols]),sc.transform(X[te][:,cols])
        if len(np.unique(y[te]))<2: continue
        nn=MLPClassifier(hidden_layer_sizes=(16,8),alpha=1.0,max_iter=2000,early_stopping=True,
                         n_iter_no_change=30,random_state=s).fit(Xtr,y[tr])
        lr=LogisticRegression(max_iter=1000,class_weight='balanced').fit(Xtr,y[tr])
        aucs_nn.append(roc_auc_score(y[te],nn.predict_proba(Xte)[:,1]))
        aucs_lr.append(roc_auc_score(y[te],lr.predict_proba(Xte)[:,1]))
    return np.mean(aucs_nn),np.std(aucs_nn),np.mean(aucs_lr)

for scheme,desc in [('M','date-MATCHED negatives (macro non-informative by design)'),
                    ('U','calendar-UNIFORM negatives (macro can signal deal-prone era)')]:
    X,y,grp=build(scheme)
    print(f"\n===== {desc} =====")
    print(f"  cells={len(y)} pos={int(y.sum())} firms={len(set(grp))}   grouped-by-firm CV, 25 seeds")
    print(f"  {'feature set':22} {'NN AUC':>14}   {'logistic AUC':>12}")
    for nm,cols in [('flight-only',list(range(0,12))),('macro-only',list(range(12,20))),
                    ('flight + macro',list(range(0,20)))]:
        mn,sd,lr=ablate(X,y,grp,cols)
        print(f"  {nm:22} {mn:.3f} +/- {sd:.3f}   {lr:.3f}")

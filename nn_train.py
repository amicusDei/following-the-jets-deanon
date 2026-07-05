#!/usr/bin/env python3
"""Deal-vs-non-deal flight-pattern classifier.

Cell = (firm, location, window-ending-at-date).
  Positive: a real trackable M&A deal (acquirer -> target HQ, ann date).
  Negative: sampled (firm, target-HQ-location, date) with NO deal linking them.
Features are SYMMETRIC (computable for both) -> no deal-level leakage.
Split: grouped by firm (no firm in train AND test), size-stratified, 2/3 / 1/3.
"""
import csv, re, math, json, random
import numpy as np
import airportsdata
from collections import defaultdict, Counter
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import GroupShuffleSplit

random.seed(7); np.random.seed(7)
R_KM=100.0; NEG_PER_POS=3

APT=airportsdata.load('ICAO')
def hav(a,b,c,d):
    r=6371.0;p1,p2=math.radians(a),math.radians(c)
    dp=math.radians(c-a);dl=math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(x))

# ---- deals (from builder) ----
deals=json.load(open('nn_deals_anchored.json'))
for d in deals: d['ann_e']=datetime.strptime(d['ann'],'%Y-%m-%d').timestamp()
all_dates=[d['ann_e'] for d in deals]

# distinct target locations (the negative-sampling location universe)
locs={}  # (round lat,lon) -> (lat,lon,name)
for d in deals: locs[(round(d['lat'],3),round(d['lon'],3))]=(d['lat'],d['lon'],d['tgt'])
LOCS=list(locs.values())

# ---- flights: per ticker sorted (epoch,lat,lon) landings ----
flights=defaultdict(list)
for r in csv.DictReader(open('dealmaker_flight_activity.csv')):
    arr=r['arr_airport']; a=APT.get(arr) if arr else None
    if not a: continue
    try: t=float(r['lastseen'])
    except: continue
    flights[r['ticker']].append((t,a['lat'],a['lon']))
for tk in flights: flights[tk].sort()
firm_total={tk:len(v) for tk,v in flights.items()}

# location popularity: distinct firms ever landing near L
loc_pop={}
for (la,lo,nm) in LOCS:
    loc_pop[(la,lo)]=sum(1 for tk,v in flights.items()
                         if any(hav(la,lo,fa,fo)<=R_KM for (_,fa,fo) in v))

def feats(tk, lat, lon, ann_e):
    ev=flights.get(tk,[])
    w90=ann_e-90*86400; w180=ann_e-180*86400; w30=ann_e-30*86400
    v90=v180=v30=v_ever=v_before=0
    last_before=None; mind=1e9
    for (t,la,lo) in ev:
        near=hav(lat,lon,la,lo)<=R_KM
        if near:
            v_ever+=1
            if t<ann_e:
                v_before+=1; last_before=t if last_before is None else max(last_before,t)
            if w90<=t<ann_e: v90+=1
            if w180<=t<ann_e: v180+=1
            if w30<=t<ann_e: v30+=1
        if t<ann_e:
            d=hav(lat,lon,la,lo); mind=min(mind,d)
    fw90=sum(1 for (t,_,_) in ev if w90<=t<ann_e)
    ftot=firm_total.get(tk,0)
    recency=(ann_e-last_before)/86400 if last_before else 1000.0
    return [
        v90, v180, v30, v_before,
        1.0 if v_before>0 else 0.0,
        min(mind,500.0),
        min(recency,1000.0),
        math.log1p(ftot),
        math.log1p(fw90),
        v90/(fw90+1),
        v_before/(ftot+1),
        loc_pop.get((round(lat,3),round(lon,3)),
                    sum(1 for tk2,v in flights.items()
                        if any(hav(lat,lon,fa,fo)<=R_KM for (_,fa,fo) in v))),
    ]
FEAT_NAMES=['v_win90','v_win180','v_win30','v_before','any_before','min_dist',
            'recency_d','log_firm_total','log_firm_win90','share_win','baseline_rate','loc_popularity']

# real (firm,loc) pairs to exclude from negatives (within 1yr)
real_pairs=defaultdict(list)
for d in deals: real_pairs[d['ticker']].append((round(d['lat'],3),round(d['lon'],3),d['ann_e']))

X=[];y=[];grp=[];sz=[]
def sizebucket(dv):
    if dv is None: return 'und'
    if dv>=10000: return 'XL'
    if dv>=1000: return 'L'
    if dv>=500: return 'M'
    return 'S'

for d in deals:
    X.append(feats(d['ticker'],d['lat'],d['lon'],d['ann_e']))
    y.append(1); grp.append(d['ticker']); sz.append(sizebucket(d['deal_value']))

firms=list({d['ticker'] for d in deals})
for d in deals:
    tk=d['ticker']
    made=0; tries=0
    while made<NEG_PER_POS and tries<50:
        tries+=1
        la,lo,nm=random.choice(LOCS)
        ann=random.choice(all_dates)
        key=(round(la,3),round(lo,3))
        bad=any(abs(ann-rt)<365*86400 and rk==key[0] and rkl==key[1]
                for (rk,rkl,rt) in real_pairs[tk])
        if bad: continue
        X.append(feats(tk,la,lo,ann)); y.append(0); grp.append(tk); sz.append('neg'); made+=1

X=np.array(X,float); y=np.array(y); grp=np.array(grp); sz=np.array(sz)
print(f"dataset: {len(y)} cells | positives {int(y.sum())} | negatives {int((y==0).sum())} | firms {len(set(grp))}")
print(f"positive base rate: {y.mean():.3f}")

def evaluate(seed, verbose=False):
    gss=GroupShuffleSplit(n_splits=1,test_size=1/3,random_state=seed)
    tr,te=next(gss.split(X,y,groups=grp))
    sc=StandardScaler().fit(X[tr])
    Xtr,Xte=sc.transform(X[tr]),sc.transform(X[te])
    mlp=MLPClassifier(hidden_layer_sizes=(16,8),alpha=1.0,max_iter=2000,
                      early_stopping=True,n_iter_no_change=30,random_state=seed)
    mlp.fit(Xtr,y[tr])
    lr=LogisticRegression(max_iter=1000,class_weight='balanced').fit(Xtr,y[tr])
    pm=mlp.predict_proba(Xte)[:,1]; pl=lr.predict_proba(Xte)[:,1]
    rule=(X[te][:,0]>0).astype(float)  # v_win90>0
    base=y[te].mean()
    out=dict(
        n_test=len(te), pos_test=int(y[te].sum()), base=base,
        mlp_roc=roc_auc_score(y[te],pm), mlp_pr=average_precision_score(y[te],pm),
        lr_roc=roc_auc_score(y[te],pl), lr_pr=average_precision_score(y[te],pl),
        rule_pr=average_precision_score(y[te],rule), rule_roc=roc_auc_score(y[te],rule),
        train_firms=sorted(set(grp[tr])), test_firms=sorted(set(grp[te])))
    if verbose:
        print(f"\n=== Headline 2/3-1/3 grouped split (seed={seed}) ===")
        print(f"test cells: {out['n_test']}  positives: {out['pos_test']}  base rate: {base:.3f}")
        print(f"  MLP (neural net): ROC-AUC {out['mlp_roc']:.3f} | PR-AUC {out['mlp_pr']:.3f}")
        print(f"  LogReg baseline : ROC-AUC {out['lr_roc']:.3f} | PR-AUC {out['lr_pr']:.3f}")
        print(f"  visit>0 rule    : ROC-AUC {out['rule_roc']:.3f} | PR-AUC {out['rule_pr']:.3f}")
        print(f"  chance PR-AUC ~ base rate = {base:.3f}")
        print(f"  test firms ({len(out['test_firms'])}): {', '.join(out['test_firms'])}")
        # feature importance via LR coefs
        lr_full=LogisticRegression(max_iter=1000,class_weight='balanced').fit(StandardScaler().fit_transform(X),y)
        imp=sorted(zip(FEAT_NAMES,lr_full.coef_[0]),key=lambda x:-abs(x[1]))
        print("  top features (|LR coef|):", ", ".join(f"{n}={c:+.2f}" for n,c in imp[:6]))
    return out

evaluate(7, verbose=True)

# multi-seed stability
rocs=[];prs=[];lrprs=[]
for s in range(30):
    try:
        o=evaluate(s)
        rocs.append(o['mlp_roc']);prs.append(o['mlp_pr']);lrprs.append(o['lr_pr'])
    except Exception: pass
import statistics as st
print(f"\n=== Stability over {len(rocs)} grouped splits ===")
print(f"MLP ROC-AUC: {st.mean(rocs):.3f} +/- {st.pstdev(rocs):.3f}   (min {min(rocs):.3f}, max {max(rocs):.3f})")
print(f"MLP PR-AUC : {st.mean(prs):.3f} +/- {st.pstdev(prs):.3f}")
print(f"LR  PR-AUC : {st.mean(lrprs):.3f} +/- {st.pstdev(lrprs):.3f}")
print(f"base rate (chance PR-AUC): {y.mean():.3f}")

# ---------- DIAGNOSTICS ----------
print("\n=== Diagnostic 1: raw feature separation (pos vs neg) ===")
for i,nm in enumerate(FEAT_NAMES):
    mp=X[y==1,i].mean(); mn=X[y==0,i].mean()
    print(f"  {nm:16} pos={mp:8.3f}  neg={mn:8.3f}  diff={mp-mn:+.3f}")

print("\n=== Diagnostic 2: grouped (no firm leak) vs random (firm leaks) split ===")
from sklearn.model_selection import StratifiedShuffleSplit
def run_split(splitter, groups, label):
    rocs=[]
    for s in range(30):
        if groups is not None:
            tr,te=next(GroupShuffleSplit(n_splits=1,test_size=1/3,random_state=s).split(X,y,groups))
        else:
            tr,te=next(StratifiedShuffleSplit(n_splits=1,test_size=1/3,random_state=s).split(X,y))
        sc=StandardScaler().fit(X[tr])
        mlp=MLPClassifier(hidden_layer_sizes=(16,8),alpha=1.0,max_iter=2000,
                          early_stopping=True,n_iter_no_change=30,random_state=s).fit(sc.transform(X[tr]),y[tr])
        rocs.append(roc_auc_score(y[te],mlp.predict_proba(sc.transform(X[te]))[:,1]))
    import statistics as st
    print(f"  {label:34} MLP ROC-AUC {st.mean(rocs):.3f} +/- {st.pstdev(rocs):.3f}")
run_split(None, grp, "GROUPED by firm (honest)")
run_split('random', None, "RANDOM split (firm leaks in)")

print("\n=== Diagnostic 3: train vs test AUC (overfitting check, grouped) ===")
tr,te=next(GroupShuffleSplit(n_splits=1,test_size=1/3,random_state=7).split(X,y,groups=grp))
sc=StandardScaler().fit(X[tr])
mlp=MLPClassifier(hidden_layer_sizes=(16,8),alpha=1.0,max_iter=2000,early_stopping=True,
                  n_iter_no_change=30,random_state=7).fit(sc.transform(X[tr]),y[tr])
print(f"  train ROC-AUC {roc_auc_score(y[tr],mlp.predict_proba(sc.transform(X[tr]))[:,1]):.3f}  "
      f"test ROC-AUC {roc_auc_score(y[te],mlp.predict_proba(sc.transform(X[te]))[:,1]):.3f}")

#!/usr/bin/env python3
"""ADVERSARIAL CRITIC of the deal-vs-non-deal NN: is the 'chance' result a true null,
or an artifact of a broken / under-powered network? Tests:
  1. POSITIVE CONTROL  - inject known signal; pipeline MUST recover it (else harness broken)
  2. CAN-IT-OVERFIT    - unregularized train AUC; if ~0.5, features carry zero label info
  3. CAPACITY SWEEP    - architectures x regularization; rule out under-powering
  4. NON-NN MODELS     - GBM/RF/kNN; rule out NN-specific failure
  5. CLASS BALANCE     - 1:1 vs 3:1 negatives
  6. FEATURE SANITY    - degenerate features + per-feature univariate AUC
"""
import csv, math, json, random
import numpy as np
import airportsdata
from collections import defaultdict
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupShuffleSplit

random.seed(7); np.random.seed(7)
R_KM=100.0; DAY=86400.0
APT=airportsdata.load('ICAO')
def hav(a,b,c,d):
    r=6371.0;p1,p2=math.radians(a),math.radians(c);dp=math.radians(c-a);dl=math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(x))
flights=defaultdict(list)
for r in csv.DictReader(open('dealmaker_flight_activity.csv')):
    a=APT.get(r['arr_airport']) if r['arr_airport'] else None
    if not a: continue
    try: t=float(r['lastseen'])
    except: continue
    flights[r['ticker']].append((t,a['lat'],a['lon']))
for tk in flights: flights[tk].sort()
firm_total={tk:len(v) for tk,v in flights.items()}
deals=json.load(open('nn_deals_anchored.json'))
for d in deals: d['ann_e']=datetime.strptime(d['ann'],'%Y-%m-%d').timestamp()
all_dates=[d['ann_e'] for d in deals]
LOCS=list({(round(d['lat'],3),round(d['lon'],3)):(d['lat'],d['lon']) for d in deals}.values())
loc_pop={(round(la,3),round(lo,3)):sum(1 for tk,v in flights.items() if any(hav(la,lo,fa,fo)<=R_KM for (_,fa,fo) in v)) for (la,lo) in LOCS}
def feats(tk,lat,lon,ann_e):
    ev=flights.get(tk,[]); w90=ann_e-90*DAY;w180=ann_e-180*DAY;w30=ann_e-30*DAY
    v90=v180=v30=v_before=0;last=None;mind=1e9
    for (t,la,lo) in ev:
        near=hav(lat,lon,la,lo)<=R_KM
        if near:
            if t<ann_e:v_before+=1;last=t if last is None else max(last,t)
            if w90<=t<ann_e:v90+=1
            if w180<=t<ann_e:v180+=1
            if w30<=t<ann_e:v30+=1
        if t<ann_e:mind=min(mind,hav(lat,lon,la,lo))
    fw90=sum(1 for (t,_,_) in ev if w90<=t<ann_e);ftot=firm_total.get(tk,0)
    rec=(ann_e-last)/DAY if last else 1000.0
    return [v90,v180,v30,v_before,1.0 if v_before>0 else 0.0,min(mind,500.0),min(rec,1000.0),
            math.log1p(ftot),math.log1p(fw90),v90/(fw90+1),v_before/(ftot+1),loc_pop.get((round(lat,3),round(lon,3)),0)]
FN=['v90','v180','v30','v_before','any_before','min_dist','recency','logFtot','logFw90','share','baserate','locpop']
def build(neg=3):
    X=[];y=[];g=[]
    for d in deals: X.append(feats(d['ticker'],d['lat'],d['lon'],d['ann_e']));y.append(1);g.append(d['ticker'])
    for d in deals:
        tk=d['ticker'];m=0;t=0
        while m<neg and t<60:
            t+=1;la,lo=random.choice(LOCS);ann=random.choice(all_dates)
            if round(la,3)==round(d['lat'],3) and abs(ann-d['ann_e'])<365*DAY:continue
            X.append(feats(tk,la,lo,ann));y.append(0);g.append(tk);m+=1
    return np.array(X,float),np.array(y),np.array(g)
X,y,grp=build()
print(f"dataset: {len(y)} cells, {int(y.sum())} pos, {len(set(grp))} firms")

def gcv(model_fn, Xin, yin, gin, seeds=15, standardize=True):
    a=[]
    for s in range(seeds):
        tr,te=next(GroupShuffleSplit(1,test_size=1/3,random_state=s).split(Xin,yin,groups=gin))
        if len(np.unique(yin[te]))<2: continue
        Xtr,Xte=Xin[tr],Xin[te]
        if standardize:
            sc=StandardScaler().fit(Xtr);Xtr,Xte=sc.transform(Xtr),sc.transform(Xte)
        m=model_fn().fit(Xtr,yin[tr])
        a.append(roc_auc_score(yin[te],m.predict_proba(Xte)[:,1]))
    return np.mean(a),np.std(a)

# ===== 1. POSITIVE CONTROL =====
print("\n===== 1. POSITIVE CONTROL (inject signal; harness MUST recover) =====")
mlp=lambda: MLPClassifier(hidden_layer_sizes=(16,8),alpha=1.0,max_iter=2000,early_stopping=True,n_iter_no_change=30,random_state=0)
for strength,lbl in [(0.0,'none (=real features only)'),(0.5,'weak'),(1.0,'moderate'),(3.0,'strong')]:
    rngc=np.random.default_rng(1)
    synth=(2*y-1)*strength + rngc.normal(0,1,len(y))
    Xa=np.column_stack([X,synth])
    mn,sd=gcv(mlp,Xa,y,grp)
    print(f"  signal={lbl:26} NN AUC={mn:.3f} +/- {sd:.3f}")
print("  (AUC must climb toward 1.0 as injected signal strengthens -> pipeline CAN learn)")

# ===== 2. CAN-IT-OVERFIT (train AUC, unregularized) =====
print("\n===== 2. CAN-IT-OVERFIT?  train-set AUC, no regularization =====")
sc=StandardScaler().fit(X);Xs=sc.transform(X)
for arch,al in [((16,8),1.0),((128,64),1e-5),((256,128,64),1e-6)]:
    m=MLPClassifier(hidden_layer_sizes=arch,alpha=al,max_iter=5000,random_state=0).fit(Xs,y)
    tr_auc=roc_auc_score(y,m.predict_proba(Xs)[:,1])
    print(f"  arch={str(arch):16} alpha={al:<7} TRAIN AUC={tr_auc:.3f}")
print("  (if even an unregularized net can't push TRAIN AUC >> 0.5, features hold ~no label info)")
# control: can it memorize a RANDOM label? (sanity that the net CAN fit noise if features had capacity)
yrand=np.random.default_rng(2).integers(0,2,len(y))
m=MLPClassifier(hidden_layer_sizes=(256,128,64),alpha=1e-6,max_iter=5000,random_state=0).fit(Xs,yrand)
print(f"  [capacity check] fit RANDOM labels: TRAIN AUC={roc_auc_score(yrand,m.predict_proba(Xs)[:,1]):.3f}  (high => net has capacity; low train AUC on REAL y => signal absent, not capacity-bound)")

# ===== 3. CAPACITY / HYPERPARAM SWEEP (grouped CV test AUC) =====
print("\n===== 3. CAPACITY SWEEP (grouped-CV test AUC; rule out under-powering) =====")
best=0
for arch in [(8,),(16,8),(32,),(64,32),(128,64,32)]:
    for al in [1e-3,1e-1,1.0]:
        fn=lambda arch=arch,al=al: MLPClassifier(hidden_layer_sizes=arch,alpha=al,max_iter=3000,early_stopping=True,n_iter_no_change=30,random_state=0)
        mn,sd=gcv(fn,X,y,grp,seeds=10)
        best=max(best,mn)
        print(f"  arch={str(arch):14} alpha={al:<6} AUC={mn:.3f} +/- {sd:.3f}")
print(f"  BEST config AUC over the whole sweep = {best:.3f}")

# ===== 4. NON-NN MODELS =====
print("\n===== 4. NON-NN MODELS (rule out NN-specific failure) =====")
for nm,fn in [('LogisticReg',lambda:LogisticRegression(max_iter=1000,class_weight='balanced')),
              ('GradBoost',lambda:GradientBoostingClassifier(random_state=0)),
              ('RandomForest',lambda:RandomForestClassifier(n_estimators=300,random_state=0)),
              ('kNN-15',lambda:KNeighborsClassifier(15))]:
    mn,sd=gcv(fn,X,y,grp)
    print(f"  {nm:14} AUC={mn:.3f} +/- {sd:.3f}")

# ===== 5. CLASS BALANCE =====
print("\n===== 5. CLASS BALANCE (1:1 vs 3:1 negatives) =====")
for neg in [1,3]:
    Xb,yb,gb=build(neg)
    mn,sd=gcv(mlp,Xb,yb,gb)
    print(f"  {neg}:1 negatives  pos-rate={yb.mean():.2f}  NN AUC={mn:.3f} +/- {sd:.3f}")

# ===== 6. FEATURE SANITY =====
print("\n===== 6. FEATURE SANITY =====")
print("  degenerate check: ", end='')
deg=[FN[i] for i in range(X.shape[1]) if np.std(X[:,i])==0 or np.isnan(X[:,i]).any()]
print("none" if not deg else f"PROBLEM: {deg}")
print("  per-feature univariate AUC (|signal| individually):")
for i,f in enumerate(FN):
    au=roc_auc_score(y,X[:,i]); au=max(au,1-au)
    print(f"    {f:12} {au:.3f}")

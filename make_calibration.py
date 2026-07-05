#!/usr/bin/env python3
"""Out-of-sample calibration curve for the deal-vs-non-deal model.
Firm-grouped CV (same split as the post) -> held-out predicted probabilities ->
calibration vs the ideal diagonal and the no-skill base-rate line."""
import csv, math, json, random
import numpy as np
import airportsdata
from collections import defaultdict
from datetime import datetime
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.calibration import calibration_curve

random.seed(7); np.random.seed(7)
R_KM=100.0; DAY=86400.0
ACCENT='#b23a48'; NAVY='#16243f'; GREY='#8b929e'; GREYD='#5b6472'

# ---------- data (flight features, date-matched negatives) ----------
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
X=[];y=[];grp=[]
for d in deals: X.append(feats(d['ticker'],d['lat'],d['lon'],d['ann_e']));y.append(1);grp.append(d['ticker'])
for d in deals:
    tk=d['ticker'];m=0;t=0
    while m<3 and t<60:
        t+=1;la,lo=random.choice(LOCS);ann=random.choice(all_dates)
        if round(la,3)==round(d['lat'],3) and abs(ann-d['ann_e'])<365*DAY:continue
        X.append(feats(tk,la,lo,ann));y.append(0);grp.append(tk);m+=1
X=np.array(X,float);y=np.array(y);grp=np.array(grp)
base=y.mean()

# ---------- out-of-sample predictions (firm-grouped CV) ----------
prob=cross_val_predict(GradientBoostingClassifier(random_state=0),X,y,
                       cv=GroupKFold(5),groups=grp,method='predict_proba')[:,1]
# manual quantile bins -> per-bin n, fraction, mean prediction, 95% Wilson CI
order=np.argsort(prob); nb=8
mean_pred=[];frac=[];lo_ci=[];hi_ci=[];ns=[]
for idx in np.array_split(order,nb):
    pr=prob[idx]; yy=y[idx]; n=len(idx); k=int(yy.sum()); p=k/n
    z=1.96; den=1+z*z/n; cen=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    mean_pred.append(float(pr.mean())); frac.append(p); ns.append(n)
    lo_ci.append(max(0.0,cen-half)); hi_ci.append(min(1.0,cen+half))
mean_pred=np.array(mean_pred); frac=np.array(frac)
yerr=np.vstack([frac-np.array(lo_ci), np.array(hi_ci)-frac])
print(f"base rate={base:.3f} | oos prob {prob.min():.2f}-{prob.max():.2f} | bin n={ns}")
print("mean_pred:",np.round(mean_pred,3)); print("frac_pos :",np.round(frac,3))

# ---------- plot (post style) ----------
plt.rcParams.update({'font.family':'DejaVu Sans','axes.edgecolor':'#9aa0aa','axes.linewidth':0.8})
fig,ax=plt.subplots(figsize=(7.6,5.8))
axhi=min(1.0,max(0.6,float(np.max(hi_ci)),float(mean_pred.max()),base)+0.06)
ax.plot([0,1],[0,1],ls='--',lw=1.4,color=GREY,zorder=1,label='perfectly calibrated (ideal)')
ax.axhline(base,ls=':',lw=1.6,color=GREYD,zorder=1,label=f'base rate / no-skill ({base:.2f})')
ax.errorbar(mean_pred,frac,yerr=yerr,fmt='-o',lw=2.4,ms=6,color=ACCENT,ecolor=ACCENT,
            elinewidth=1.2,capsize=3,zorder=3,label='my model (out-of-sample, 95% CI)')
ax.annotate('every point overlaps the base\nrate within its confidence band',
            xy=(mean_pred[-2],frac[-2]),xytext=(0.255,0.07),
            fontsize=9,color=GREYD,
            arrowprops=dict(arrowstyle='->',color=GREYD,lw=1.0))
ax.set_xlim(0,axhi); ax.set_ylim(0,axhi)
ax.set_xlabel('predicted probability a firm is an acquisition target',fontsize=10.5)
ax.set_ylabel('actual share that were targets',fontsize=10.5)
ax.set_title('No predictive skill: out-of-sample the model sits on\nthe base rate, not on the ideal diagonal',
             fontsize=12.5,color=NAVY,weight='bold',pad=12)
ax.legend(fontsize=9.2,frameon=False,loc='upper left')
ax.grid(alpha=0.16)
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.set_aspect('equal',adjustable='box')
fig.tight_layout(rect=[0,0.075,1,1])
fig.text(0.5,0.038,'Case-control design: the 0.25 base rate is by construction (3 matched non-targets per real '
         'target), far above the true takeover rate.',ha='center',fontsize=7.7,color=GREYD)
fig.text(0.5,0.012,'8 equal-count bins, 74 observations each; bars are 95% Wilson confidence intervals.',
         ha='center',fontsize=7.7,color=GREYD)
import os
for p in [f'{os.path.dirname(os.path.abspath(__file__))}/fig_calibration.png',
          os.path.expanduser('~/Documents/JetTracking-Calibration.png')]:
    fig.savefig(p,dpi=220,bbox_inches='tight')
    print('WROTE',p)
plt.close(fig)

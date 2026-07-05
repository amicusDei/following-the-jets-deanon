#!/usr/bin/env python3
"""Stress the 1.48x hump against the exact confounds that nulled predfkitweball's 1.50x:
  (1) ACTIVITY-matching  — normalize target-city visits by firm's TOTAL flights in-window
                           (predfkitweball: 1.50x -> 1.13x NULL once activity-matched)
  (2) FIRM-clustering    — 1-firm-1-vote sign test (theirs: NULL everywhere)
  (3) OUTLIER deals      — drop top-k high-visit deals; deal-as-unit binary
"""
import csv, math, json, bisect
import numpy as np
from datetime import datetime
from collections import defaultdict
import airportsdata

R_KM=100.0; DAY=86400.0; B=3000
rng=np.random.default_rng(7)
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
cov={tk:(v[0][0],v[-1][0]) for tk,v in flights.items() if v}
alltimes={tk:[t for (t,_,_) in v] for tk,v in flights.items()}  # all firm flight times

deals=json.load(open('nn_deals_anchored.json'))
for d in deals:
    d['ann_e']=datetime.strptime(d['ann'],'%Y-%m-%d').timestamp()
    d['near']=sorted(t for (t,la,lo) in flights.get(d['ticker'],[]) if hav(d['lat'],d['lon'],la,lo)<=R_KM)
    d['cov']=cov.get(d['ticker'],(d['ann_e'],d['ann_e']))

def wc(arr,t0,t1): return bisect.bisect_left(arr,t1)-bisect.bisect_left(arr,t0)
def valid(d,t,w0,w1):
    c0,c1=d['cov']; return (t+w0*DAY)>=c0 and (t+w1*DAY)<=c1
def offsets(d,w0,w1,n):
    out=[];tr=0
    while len(out)<n and tr<n*40:
        tr+=1; off=rng.uniform(365,1095)*(1 if rng.random()<0.5 else -1)
        if valid(d,d['ann_e']+off*DAY,w0,w1): out.append(off)
    return out

W0,W1=-300,-120   # the HUMP window
def subset(name,sub):
    use=[d for d in sub if valid(d,d['ann_e'],W0,W1) and offsets(d,W0,W1,1)]
    print(f"\n########## {name}  (N usable = {len(use)}) ##########")

    # ---------- (0) RAW count RR (reproduce headline) ----------
    realv=sum(wc(d['near'],d['ann_e']+W0*DAY,d['ann_e']+W1*DAY) for d in use)
    # precompute placebo offsets per deal
    POFF={id(d):offsets(d,W0,W1,B) for d in use}
    nullv=np.zeros(B)
    for d in use:
        o=POFF[id(d)]
        if not o: continue
        c=np.array([wc(d['near'],d['ann_e']+x*DAY+W0*DAY,d['ann_e']+x*DAY+W1*DAY) for x in o])
        nullv+=c[rng.integers(0,len(c),B)]
    rr_raw=realv/nullv.mean(); p_raw=2*min((np.sum(nullv>=realv)+1)/(B+1),(np.sum(nullv<=realv)+1)/(B+1))
    print(f"(0) RAW visit-count RR        = {rr_raw:.2f}  (real {realv} vs exp {nullv.mean():.0f})  p={p_raw:.3f}")

    # ---------- (1) ACTIVITY-matched: share of firm's total flights ----------
    rt=alltimes
    real_vis=sum(wc(d['near'],d['ann_e']+W0*DAY,d['ann_e']+W1*DAY) for d in use)
    real_tot=sum(wc(rt[d['ticker']],d['ann_e']+W0*DAY,d['ann_e']+W1*DAY) for d in use)
    real_share=real_vis/real_tot if real_tot else 0
    nshare=np.zeros(B)
    for j in range(B):
        sv=st=0
        for d in use:
            o=POFF[id(d)]
            if not o: continue
            x=o[rng.integers(0,len(o))]
            sv+=wc(d['near'],d['ann_e']+x*DAY+W0*DAY,d['ann_e']+x*DAY+W1*DAY)
            st+=wc(rt[d['ticker']],d['ann_e']+x*DAY+W0*DAY,d['ann_e']+x*DAY+W1*DAY)
        nshare[j]=sv/st if st else 0
    rr_act=real_share/nshare.mean() if nshare.mean() else float('inf')
    p_act=2*min((np.sum(nshare>=real_share)+1)/(B+1),(np.sum(nshare<=real_share)+1)/(B+1))
    print(f"(1) ACTIVITY-matched share RR = {rr_act:.2f}  (real {real_share:.4f} vs exp {nshare.mean():.4f})  p={p_act:.3f}   <-- the predfkitweball killer")

    # ---------- (2) FIRM-clustered 1-firm-1-vote sign test ----------
    byfirm=defaultdict(list)
    for d in use: byfirm[d['ticker']].append(d)
    wins=0;tot=0
    for tk,ds in byfirm.items():
        rv=sum(wc(d['near'],d['ann_e']+W0*DAY,d['ann_e']+W1*DAY) for d in ds)
        ev=np.mean([sum(wc(d['near'],d['ann_e']+x*DAY+W0*DAY,d['ann_e']+x*DAY+W1*DAY)
                        for d,x in zip(ds,[POFF[id(d)][rng.integers(0,len(POFF[id(d)]))] if POFF[id(d)] else 0 for d in ds]))
                    for _ in range(200)])
        if rv>ev: wins+=1
        if rv!=ev: tot+=1
    from math import comb
    p_sign=2*sum(comb(tot,k) for k in range(max(wins,tot-wins),tot+1))/2**tot if tot else 1.0
    print(f"(2) FIRM sign test           = {wins}/{tot} firms real>placebo  (binomial p={min(p_sign,1.0):.3f})")

    # ---------- (3) OUTLIER sensitivity: drop top-k deals ----------
    perdeal=sorted(((wc(d['near'],d['ann_e']+W0*DAY,d['ann_e']+W1*DAY),d) for d in use),key=lambda x:-x[0])
    top=[f"{d['tgt'][:20]}={c}" for c,d in perdeal[:5]]
    print(f"(3) top-5 deals by hump visits: {', '.join(top)}")
    for k in [0,2,5]:
        keep=[d for _,d in perdeal[k:]]
        rv=sum(wc(d['near'],d['ann_e']+W0*DAY,d['ann_e']+W1*DAY) for d in keep)
        nv=np.zeros(B)
        for d in keep:
            o=POFF[id(d)]
            if not o: continue
            c=np.array([wc(d['near'],d['ann_e']+x*DAY+W0*DAY,d['ann_e']+x*DAY+W1*DAY) for x in o])
            nv+=c[rng.integers(0,len(c),B)]
        rr=rv/nv.mean() if nv.mean() else float('inf')
        p=2*min((np.sum(nv>=rv)+1)/(B+1),(np.sum(nv<=rv)+1)/(B+1))
        print(f"    drop top-{k}: RR={rr:.2f}  p={p:.3f}  (N={len(keep)})")

    # ---------- (4) deal-as-unit binary (any visit in hump) ----------
    real_frac=np.mean([1.0 if wc(d['near'],d['ann_e']+W0*DAY,d['ann_e']+W1*DAY)>0 else 0 for d in use])
    nf=np.zeros(B)
    for j in range(B):
        c=0
        for d in use:
            o=POFF[id(d)]
            if not o: continue
            x=o[rng.integers(0,len(o))]
            if wc(d['near'],d['ann_e']+x*DAY+W0*DAY,d['ann_e']+x*DAY+W1*DAY)>0: c+=1
        nf[j]=c/len(use)
    p_bin=2*min((np.sum(nf>=real_frac)+1)/(B+1),(np.sum(nf<=real_frac)+1)/(B+1))
    print(f"(4) deal-binary any-visit    = real {real_frac:.3f} vs exp {nf.mean():.3f}  RR={real_frac/nf.mean():.2f}  p={p_bin:.3f}")

subset("ALL trackable deals", deals)
subset("Public >=$1B", [d for d in deals if d['tpublic']=='Public' and d['deal_value'] and d['deal_value']>=1000])

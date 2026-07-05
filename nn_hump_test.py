#!/usr/bin/env python3
"""Matched-control significance test for the pre-deal flight 'hump'.

Control = placebo announcement dates: same firm, same target city, date shifted
to nearby non-deal periods (+/-1..3 yr). Tests whether visitation around the REAL
announcement deviates from the firm-city baseline at matched timing.
Cross-check: Poisson rate-ratio vs each deal's own firm-city baseline rate.
"""
import csv, math, json, bisect
import numpy as np
from datetime import datetime
from collections import defaultdict
import airportsdata

R_KM=100.0; DAY=86400.0; B=4000
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

deals=json.load(open('nn_deals_anchored.json'))
for d in deals:
    d['ann_e']=datetime.strptime(d['ann'],'%Y-%m-%d').timestamp()
    # precompute sorted timestamps when firm was within R_KM of target city
    d['near']=sorted(t for (t,la,lo) in flights.get(d['ticker'],[]) if hav(d['lat'],d['lon'],la,lo)<=R_KM)
    d['cov']=cov.get(d['ticker'],(d['ann_e'],d['ann_e']))

def wcount(near,t0,t1):
    return bisect.bisect_left(near,t1)-bisect.bisect_left(near,t0)

def valid(d,t,w0,w1):
    c0,c1=d['cov']; return (t+w0*DAY)>=c0 and (t+w1*DAY)<=c1

def placebo_offsets(d,w0,w1,n):
    """draw n valid offsets (days) in +/-[365,1095] keeping window in coverage."""
    out=[]; tries=0
    while len(out)<n and tries<n*40:
        tries+=1
        off=rng.uniform(365,1095)*(1 if rng.random()<0.5 else -1)
        if valid(d,d['ann_e']+off*DAY,w0,w1): out.append(off)
    return out

def window_test(subset,w0,w1,name):
    # keep deals with valid real window AND placebo room
    use=[d for d in subset if valid(d,d['ann_e'],w0,w1) and len(placebo_offsets(d,w0,w1,1))>0]
    if not use: print(f"  {name:10} [{w0:+4d},{w1:+4d}]  no usable deals"); return
    real=sum(wcount(d['near'],d['ann_e']+w0*DAY,d['ann_e']+w1*DAY) for d in use)
    null=np.zeros(B)
    for d in use:
        offs=placebo_offsets(d,w0,w1,B)
        if not offs: continue
        offs=np.array(offs)
        cnts=np.array([wcount(d['near'],d['ann_e']+o*DAY+w0*DAY,d['ann_e']+o*DAY+w1*DAY) for o in offs])
        # pad to B by resampling
        idx=rng.integers(0,len(cnts),B)
        null+=cnts[idx]
    mu=null.mean(); sd=null.std() or 1e-9
    rr=real/mu if mu>0 else float('inf')
    p_hi=(np.sum(null>=real)+1)/(B+1); p_lo=(np.sum(null<=real)+1)/(B+1)
    p=2*min(p_hi,p_lo)
    z=(real-mu)/sd
    print(f"  {name:14} [{w0:+4d},{w1:+4d}]d  N={len(use):3}  real={real:4d}  exp={mu:7.1f}  "
          f"RR={rr:4.2f}  z={z:+5.2f}  p={p:.3f}")

WINDOWS=[(-300,-120,'HUMP'),(-360,-90,'pre-courtship'),(-90,0,'RUN-UP'),(0,90,'POST-close')]
for label,subset in [("ALL (148)",deals),
                     ("Public>=$1B (36)",[d for d in deals if d['tpublic']=='Public' and d['deal_value'] and d['deal_value']>=1000]),
                     (">=$10B mega (17)",[d for d in deals if d['deal_value'] and d['deal_value']>=10000])]:
    print(f"\n=== Placebo-date matched control — {label} ===")
    print("  window         range        N   real    expected  RR    z     p(2-sided)")
    for w0,w1,nm in WINDOWS: window_test(subset,w0,w1,nm)

# ---- per-30d-bin significance profile (ALL) ----
def bin_profile(subset,name):
    bins=list(range(-360,181,30))
    use=[d for d in subset if d['cov'][1]-d['cov'][0]>=(540+730)*DAY]
    real={b:0 for b in bins[:-1]}; nreal={b:0 for b in bins[:-1]}
    for d in use:
        for b0,b1 in zip(bins[:-1],bins[1:]):
            if valid(d,d['ann_e'],b0,b1):
                real[b0]+=wcount(d['near'],d['ann_e']+b0*DAY,d['ann_e']+b1*DAY); nreal[b0]+=1
    null={b:np.zeros(B) for b in bins[:-1]}
    for d in use:
        offs=placebo_offsets(d,-360,180,B)
        if not offs: continue
        offs=rng.choice(offs,B)
        for j,o in enumerate(offs):
            T=d['ann_e']+o*DAY
            for b0,b1 in zip(bins[:-1],bins[1:]):
                if valid(d,T,b0,b1):
                    null[b0][j]+=wcount(d['near'],T+b0*DAY,T+b1*DAY)
    print(f"\n=== Per-bin matched-control profile — {name} (N={len(use)}) ===")
    print("  bin            real/deal  exp/deal   z      p")
    for b0 in bins[:-1]:
        n=nreal[b0] or 1
        rd=real[b0]/n; mu=null[b0].mean()/n; sd=(null[b0].std() or 1e-9)/n
        z=(rd-mu)/sd
        p_hi=(np.sum(null[b0]>=real[b0])+1)/(B+1); p_lo=(np.sum(null[b0]<=real[b0])+1)/(B+1)
        p=2*min(p_hi,p_lo)
        star=' *' if p<0.05 else ''
        print(f"  {b0:+4d}..{b0+30:+4d}d   {rd:6.3f}    {mu:6.3f}   {z:+5.2f}  {p:.3f}{star}")

bin_profile(deals,"ALL trackable deals")
bin_profile([d for d in deals if d['tpublic']=='Public' and d['deal_value'] and d['deal_value']>=1000],"Public>=$1B")

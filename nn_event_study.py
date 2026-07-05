#!/usr/bin/env python3
"""Event study: acquirer-jet visits near target HQ, aligned on announcement day.
Finds the temporal shape of pre-deal flight activity and which firms drive it."""
import csv, math, json
from datetime import datetime
from collections import defaultdict
import airportsdata

R_KM=100.0
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

deals=json.load(open('nn_deals_anchored.json'))
for d in deals: d['ann_e']=datetime.strptime(d['ann'],'%Y-%m-%d').timestamp()
DAY=86400.0

def visits_near(tk,lat,lon,t0,t1):
    return [t for (t,la,lo) in flights.get(tk,[]) if t0<=t<t1 and hav(lat,lon,la,lo)<=R_KM]

# ---- event study: 30-day bins from -360 to +180 ----
bins=list(range(-360,181,30))
def event_profile(subset):
    counts={b:0 for b in bins[:-1]}
    for d in subset:
        for t in visits_near(d['ticker'],d['lat'],d['lon'],d['ann_e']-360*DAY,d['ann_e']+180*DAY):
            rel=(t-d['ann_e'])/DAY
            for b0,b1 in zip(bins[:-1],bins[1:]):
                if b0<=rel<b1: counts[b0]+=1;break
    n=len(subset)
    return {b:counts[b]/n for b in counts}, n

def show(name, subset):
    prof,n=event_profile(subset)
    print(f"\n=== {name}  (N={n} deals) — visits per deal per 30d bin ===")
    mx=max(prof.values()) or 1
    for b0 in bins[:-1]:
        v=prof[b0]; bar='#'*round(40*v/mx)
        mark=' <-- ANNOUNCE' if b0==-30 or b0==0 else ''
        seg='[ANN]' if b0==0 else f"{b0:+4d}d"
        print(f"  {seg:>6}..{b0+30:+4d}d  {v:5.3f} {bar}{mark}")
    pre=sum(prof[b] for b in bins[:-1] if -90<=b<0)
    base=sum(prof[b] for b in bins[:-1] if -360<=b<-180)/2  # avg 90d-equiv in far window
    post=sum(prof[b] for b in bins[:-1] if 0<=b<90)
    print(f"  pre-90d/deal={pre:.3f}  far-baseline(90d-equiv)={base:.3f}  ratio={pre/base if base else float('inf'):.2f}x  post-90d/deal={post:.3f}")

show("ALL trackable deals", deals)
show("Public & >=$1B (strategic)", [d for d in deals if d['tpublic']=='Public' and d['deal_value'] and d['deal_value']>=1000])
show(">=$10B mega-deals", [d for d in deals if d['deal_value'] and d['deal_value']>=10000])

# ---- lead time: first deal-window visit relative to announcement ----
print("\n=== Lead time of FIRST pre-announcement visit (anchored deals, within 365d) ===")
leads=[]
for d in deals:
    vs=visits_near(d['ticker'],d['lat'],d['lon'],d['ann_e']-365*DAY,d['ann_e'])
    if vs:
        lead=(d['ann_e']-min(vs))/DAY
        leads.append(lead)
leads.sort()
if leads:
    import statistics as st
    print(f"  anchored(365d): {len(leads)}/{len(deals)} deals")
    print(f"  first-visit lead: median {st.median(leads):.0f}d  mean {st.mean(leads):.0f}d  "
          f"p25 {leads[len(leads)//4]:.0f}d  p75 {leads[3*len(leads)//4]:.0f}d")

# ---- novelty: was target city already routine for the firm? ----
print("\n=== Novel vs routine destination (pre-90d-anchored deals) ===")
novel=routine=0
for d in deals:
    pre=visits_near(d['ticker'],d['lat'],d['lon'],d['ann_e']-90*DAY,d['ann_e'])
    if not pre: continue
    prior=visits_near(d['ticker'],d['lat'],d['lon'],d['ann_e']-2*365*DAY,d['ann_e']-90*DAY)
    if len(prior)<=1: novel+=1
    else: routine+=1
print(f"  novel (<=1 prior visit in [-2yr,-90d]): {novel}   routine (firm already flew there): {routine}")

# ---- per-firm: who drives the pattern ----
print("\n=== Per-firm pre-90d anchoring (firms with >=1 anchored deal) ===")
byfirm=defaultdict(lambda:[0,0,[]])  # tk -> [anchored, total, examples]
for d in deals:
    pre=visits_near(d['ticker'],d['lat'],d['lon'],d['ann_e']-90*DAY,d['ann_e'])
    byfirm[d['ticker']][1]+=1
    if pre:
        byfirm[d['ticker']][0]+=1
        lead=(d['ann_e']-min(pre))/DAY
        byfirm[d['ticker']][2].append(f"{d['tgt'][:24]}({len(pre)}v,{lead:.0f}d)")
rows=sorted(byfirm.items(),key=lambda x:(-x[1][0],-x[1][1]))
for tk,(a,tot,ex) in rows:
    if a==0: continue
    print(f"  {tk:6} {a}/{tot} anchored | "+"; ".join(ex[:4]))
print(f"\n  firms with >=1 anchored deal: {sum(1 for _,(a,_,_) in byfirm.items() if a>0)}/{len(byfirm)}")

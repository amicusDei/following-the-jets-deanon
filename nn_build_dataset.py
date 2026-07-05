#!/usr/bin/env python3
"""Build the deal-vs-non-deal dataset for the flight-pattern NN.

Positives  = trackable deals (acquirer jet-firm + geocoded target HQ).
Label question per (firm, location, window): did flights there mark an M&A target?
This script's first job: measure how many of the 148 deals are *flight-anchored*
(acquirer jet actually visits near target HQ), which sets the real positive count.
"""
import csv, re, math, json
import airportsdata

R_KM = 100.0          # "near HQ" radius (matches home-base verification threshold)
WIN_DAYS = 90         # pre-announcement window

# ---------- airports ----------
APT = airportsdata.load('ICAO')
def apt_ll(icao):
    a = APT.get(icao)
    return (a['lat'], a['lon']) if a else None

def hav(lat1, lon1, lat2, lon2):
    r=6371.0
    p1,p2=math.radians(lat1),math.radians(lat2)
    dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))

# ---------- name -> ticker ----------
def norm(s):
    s=s.upper(); s=re.sub(r'[^A-Z0-9 &]',' ',s)
    for w in ['INCORPORATED','CORPORATION','COMPANY','GROUP','HOLDINGS','HOLDING','INC','CORP',
              'CO','PLC','LTD','LP','THE','CLASS','SA','NV','AG','LLC','INTL','INTERNATIONAL']:
        s=re.sub(r'\b'+w+r'\b',' ',s)
    return re.sub(r'\s+',' ',s).strip()

roster={}
for r in csv.DictReader(open('dealmaker_jets.csv')):
    roster.setdefault(norm(r['name']), r['ticker'])
for r in csv.DictReader(open('dealmaker_flight_activity.csv')):
    if r['name'].strip(): roster.setdefault(norm(r['name']), r['ticker'])

PATCH={'Amer Intl Grp Inc':'AIG','Blackstone Group Inc':'BX','Blackstone Inc':'BX',
       'Cabot Oil & Gas Corp':'CTRA','IBM':'IBM','Visa Inc':'V'}

def acq_ticker(acq):
    if acq in PATCH: return PATCH[acq]
    na=norm(acq); tk=roster.get(na)
    if tk: return tk
    toks=set(na.split()); best=None;bs=0
    for rn,rt in roster.items():
        rt2=set(rn.split())
        if not rt2: continue
        j=len(toks&rt2)/len(toks|rt2)
        if j>bs: bs=j;best=rt
    return best if bs>=0.5 else None

# ---------- target HQ coords ----------
def fnum(x):
    try:
        v=float(x); return v if not math.isnan(v) else None
    except: return None
tgt_ll={}
for r in csv.DictReader(open('target_hq_research.csv')):
    lat,lon=fnum(r['lat']),fnum(r['lon'])
    if lat is not None and lon is not None: tgt_ll[norm(r['target'])]=(lat,lon)
for r in csv.DictReader(open('newfirm_deals_geocoded.csv')):
    lat,lon=fnum(r['lat']),fnum(r['lon'])
    if lat is not None and lon is not None: tgt_ll.setdefault(norm(r['tgt']),(lat,lon))

# ---------- deals ----------
from datetime import datetime
def ts(d):
    try: return datetime.strptime(d,'%Y-%m-%d')
    except: return None
deals=[]
for r in csv.DictReader(open('jetfirm_all_deals_82.csv')):
    ll=tgt_ll.get(norm(r['tgt']))
    if ll is None: continue            # not trackable (no target HQ)
    tk=acq_ticker(r['acq']); d=ts(r['dateann'])
    if tk is None or d is None: continue
    try: dv=float(r['deal_value'])
    except: dv=None
    deals.append(dict(acq=r['acq'],ticker=tk,tgt=r['tgt'],lat=ll[0],lon=ll[1],
                      ann=d,deal_value=dv,tpublic=r['tpublic'],status=r['statuscode']))
print(f"trackable deals joined: {len(deals)} | distinct acquirers: {len({d['ticker'] for d in deals})}")

# ---------- flights per ticker: (epoch, lat, lon) landing events ----------
from collections import defaultdict
flights=defaultdict(list)
miss=0
for r in csv.DictReader(open('dealmaker_flight_activity.csv')):
    arr=r['arr_airport']
    if not arr: continue
    ll=apt_ll(arr)
    if ll is None: miss+=1; continue
    try: t=float(r['lastseen'])
    except: continue
    flights[r['ticker']].append((t, ll[0], ll[1]))
for tk in flights: flights[tk].sort()
print(f"flight landing events indexed for {len(flights)} tickers (dropped {miss} unresolved airports)")

# ---------- measure flight-anchoring ----------
def visits_near(tk, lat, lon, t0=None, t1=None):
    n=0
    for (t,la,lo) in flights.get(tk,[]):
        if t0 and t<t0: continue
        if t1 and t>=t1: continue
        if hav(lat,lon,la,lo)<=R_KM: n+=1
    return n

anchored_ever=anchored_win=0
for d in deals:
    ann_e=d['ann'].timestamp()
    win0=ann_e-WIN_DAYS*86400
    ve=visits_near(d['ticker'],d['lat'],d['lon'])
    vw=visits_near(d['ticker'],d['lat'],d['lon'],win0,ann_e)
    d['visits_ever']=ve; d['visits_win']=vw
    if ve>0: anchored_ever+=1
    if vw>0: anchored_win+=1

print(f"\n=== FLIGHT-ANCHORING (R={R_KM:.0f}km) ===")
print(f"deals with >=1 acquirer-jet visit near target HQ EVER:     {anchored_ever}/{len(deals)}")
print(f"deals with >=1 visit in {WIN_DAYS}d pre-announcement window: {anchored_win}/{len(deals)}")
# distribution of pre-window visits
import collections
dist=collections.Counter(min(d['visits_win'],5) for d in deals)
print("pre-window visit counts (capped@5):", dict(sorted(dist.items())))

json.dump([{**d,'ann':d['ann'].strftime('%Y-%m-%d')} for d in deals],
          open('nn_deals_anchored.json','w'), indent=0)
print("\nwrote nn_deals_anchored.json")

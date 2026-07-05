import sqlite3, pandas as pd
from pyopensky.trino import Trino
nj=pd.read_csv('sec_newly_identified_jets.csv'); nj['icao24']=nj.icao24.str.lower()
hexes=sorted(nj.icao24.unique()); inlist=",".join(f"'{h}'" for h in hexes)
print('confirming home base for',len(hexes),'newly-identified jets...',flush=True)
df=Trino().query(f"""SELECT icao24, estdepartureairport dep, estarrivalairport arr
  FROM flights_data4 WHERE day>=1514764800 AND day<=1782172800 AND icao24 IN ({inlist})""")
print('flight rows:',len(df),flush=True)
# airport coords from widened DB
con=sqlite3.connect('~/dev/predfkitweball/data/processed/backtest_wide.db')
ap=pd.read_sql("select icao,lat,lon from airports",con).dropna().set_index('icao')
# firm HQ coords (the 9 firms)
HQ={'BMY':(40.30,-74.66,'Princeton NJ'),'BX':(40.758,-73.971,'NYC'),'V':(37.55,-122.27,'Foster City CA'),
    'CAH':(40.10,-83.13,'Dublin OH'),'BDX':(41.01,-74.21,'Franklin Lakes NJ'),'AIG':(40.71,-74.01,'NYC'),
    'BAC':(35.227,-80.843,'Charlotte NC'),'AEP':(39.96,-82.99,'Columbus OH'),'LH':(36.10,-79.44,'Burlington NC')}
import math
def hv(a,b,c,d):
    R=6371;p=math.radians
    return 2*R*math.asin(math.sqrt(math.sin(p(c-a)/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2))
rows=[]
for _,r in nj.iterrows():
    sub=df[df.icao24==r['icao24']]; aps=pd.concat([sub.dep.dropna(),sub.arr.dropna()])
    aps=aps[aps.astype(str).str.strip().ne('')]
    if len(aps)<5: rows.append((r['ticker'],r['tail'],r['icao24'],r.owner,len(sub),None,None,'insufficient')); continue
    base=aps.value_counts().idxmax()
    la,lo,_=HQ[r['ticker']]
    km=None; v='airport_uncoded'
    if base in ap.index:
        km=round(hv(la,lo,ap.loc[base].lat,ap.loc[base].lon),0); v='CONFIRMED' if km<=80 else 'rejected_far'
    rows.append((r['ticker'],r['tail'],r['icao24'],str(r.owner)[:26],len(sub),base,km,v))
res=pd.DataFrame(rows,columns=['ticker','tail','icao24','owner','n_flights','home_base','km_to_hq','verdict'])
res=res.sort_values(['verdict','ticker'])
res.to_csv('homebase_confirmed_17.csv',index=False)
print(res.to_string(index=False))
ok=res[res.verdict=='CONFIRMED']
print(f'\nCONFIRMED at firm HQ airport: {len(ok)}/{len(res)} jets, {ok.ticker.nunique()} firms')

import pandas as pd, sqlite3, math
from pyopensky.trino import Trino
HQ={'PFE':(40.74,-73.97),'ABBV':(42.32,-87.84),'NFLX':(37.23,-121.96),'CRM':(37.79,-122.40),
'FIS':(30.33,-81.66),'PLD':(37.79,-122.40),'KMB':(32.87,-96.96),'TMO':(42.39,-71.24),
'GOOGL':(37.42,-122.08),'ADBE':(37.33,-121.89),'SCHW':(32.99,-97.19),'ICE':(33.75,-84.39),
'MS':(40.76,-73.98),'MGM':(36.11,-115.17),'VZ':(40.70,-74.42),'PNC':(40.44,-79.99),
'JPM':(41.07,-73.71),'CARR':(26.82,-80.13),'CNC':(38.63,-90.44),'MO':(37.54,-77.43),
'GIS':(44.97,-93.36),'BEN':(37.56,-122.32),'GS':(40.71,-74.01),'PSX':(29.76,-95.37),
'MMM':(44.95,-93.09),'WYNN':(36.13,-115.17),'STZ':(42.98,-77.40),'GM':(42.33,-83.05),
'PRU':(40.74,-74.17),'F':(42.32,-83.18),'DINO':(32.78,-96.80),'CTVA':(39.77,-86.16),
'AEP':(39.96,-82.99),'DGX':(40.79,-74.06),'CVX':(29.62,-95.66),'BMY':(40.30,-74.66),
'BAX':(42.17,-87.92),'ECL':(44.95,-93.09),'UNH':(44.92,-93.50),'VFC':(39.74,-104.99),
'KDP':(33.15,-96.82),'AMGN':(34.19,-118.87),'CMCSA':(39.95,-75.17)}
m=pd.read_csv('webresearch_jets_faa.csv'); m['icao24']=m.icao24.str.lower()
hexes=sorted(m.icao24.unique()); inlist=",".join(f"'{h}'" for h in hexes)
print('verifying',len(hexes),'jets via home base...')
df=Trino().query(f"""SELECT icao24, estdepartureairport dep, estarrivalairport arr
 FROM flights_data4 WHERE day>=1514764800 AND day<=1782172800 AND icao24 IN ({inlist})""")
con=sqlite3.connect('~/dev/predfkitweball/data/processed/backtest_wide.db')
ap=pd.read_sql("select icao,lat,lon from airports",con).dropna().set_index('icao')
def hv(a,b,c,d):
 R=6371;p=math.radians;return 2*R*math.asin(math.sqrt(math.sin(p(c-a)/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2))
rows=[]
for r in m.itertuples():
    sub=df[df.icao24==r.icao24]; aps=pd.concat([sub.dep.dropna(),sub.arr.dropna()]); aps=aps[aps.astype(str).str.strip().ne('')]
    if len(aps)<5: rows.append((r.ticker,r.tail,r.icao24,str(r.owner)[:22],len(aps),None,None,'insufficient')); continue
    base=aps.value_counts().idxmax(); la,lo=HQ.get(r.ticker,(None,None)); km=None;v='no_hq'
    if la and base in ap.index: km=round(hv(la,lo,ap.loc[base].lat,ap.loc[base].lon),0); v='CONFIRMED' if km<=100 else 'rejected_far'
    rows.append((r.ticker,r.tail,r.icao24,str(r.owner)[:22],len(aps),base,km,v))
res=pd.DataFrame(rows,columns=['ticker','tail','icao24','owner','n_flights','home_base','km_to_hq','verdict'])
res.to_csv('webresearch_jets_verified.csv',index=False)
ok=res[res.verdict=='CONFIRMED']
print('CONFIRMED:',len(ok),'jets /',ok.ticker.nunique(),'firms | rejected/insuff:',(res.verdict!='CONFIRMED').sum())
print(ok.sort_values('ticker')[['ticker','tail','owner','home_base','km_to_hq']].to_string(index=False))

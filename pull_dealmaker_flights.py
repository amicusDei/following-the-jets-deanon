import sqlite3, pandas as pd
from pyopensky.trino import Trino
# dealmaker jets from widened DB
c=sqlite3.connect('~/dev/predfkitweball/data/processed/backtest_wide.db')
firms=pd.read_sql("select firm_id,ticker,name from firms",c); firms['ticker']=firms.ticker.str.upper().str.strip()
biz=pd.read_sql("select icao24,firm_id,tail,faa_model from jets where aircraft_class='business'",c)
dm=pd.read_csv('sp500_dealmaker_jet_coverage.csv'); dm['ticker']=dm.ticker.str.upper().str.strip()
dm_fids=set(firms[firms.ticker.isin(set(dm.ticker))].firm_id)
jet=biz[biz.firm_id.isin(dm_fids)].merge(firms[['firm_id','ticker','name']],on='firm_id',how='left')
jet['icao24']=jet.icao24.str.lower(); jet['source']='widened'
# add probable Broadcom N901MM (deanon STRONG, this session)
jet=pd.concat([jet,pd.DataFrame([dict(icao24='ac7402',firm_id=-1,tail='N901MM',faa_model='FALCON 900EX',
                ticker='AVGO',name='BROADCOM INC (probable)',source='deanon_session')])],ignore_index=True)
jet=jet.drop_duplicates('icao24')
jet.to_csv('dealmaker_jets.csv',index=False)
hexes=sorted(jet.icao24.unique()); inlist=",".join(f"'{h}'" for h in hexes)
print('pulling flights for', len(hexes),'dealmaker jets, 2018-01-01 -> present')
sql=f"""
  SELECT icao24, callsign, firstseen, lastseen, day,
         estdepartureairport AS dep_airport, estarrivalairport AS arr_airport
  FROM flights_data4
  WHERE day >= 1514764800 AND day <= 1782172800
    AND icao24 IN ({inlist})
"""
df=Trino().query(sql)
print('flight rows returned:', len(df))
df=df.merge(jet[['icao24','firm_id','ticker','name']],on='icao24',how='left')
df=df.sort_values(['ticker','icao24','firstseen'])
df.to_csv('dealmaker_flight_activity.csv',index=False)
print('saved dealmaker_flight_activity.csv')
print('firms:',df.ticker.nunique(),'| jets w/ flights:',df.icao24.nunique(),'/',len(hexes))
print('per-year:'); 
df['yr']=pd.to_datetime(df.firstseen,unit='s',errors='coerce').dt.year
print(df.yr.value_counts().sort_index().to_string())

import json, time, urllib.request, urllib.parse, pandas as pd
UA={'User-Agent':'predfkitweball research your-email@example.com'}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30)
# ticker -> CIK
ct=json.load(get('https://www.sec.gov/files/company_tickers.json'))
t2c={v['ticker'].upper():str(v['cik_str']).zfill(10) for v in ct.values()}
jl=pd.read_csv('/tmp/jetless_302.csv'); jl['ticker']=jl.ticker.str.upper()
jl['cik']=jl.ticker.map(t2c)
print('jetless firms:',len(jl),'| mapped to CIK:',jl.cik.notna().sum())
FTS='https://efts.sec.gov/LATEST/search-index'
def q(phrase,cik,forms=None):
    p={'q':phrase,'ciks':cik}
    if forms: p['forms']=forms
    try:
        r=json.load(get(FTS+'?'+urllib.parse.urlencode(p)))
        return r.get('hits',{}).get('total',{}).get('value',0), r.get('hits',{}).get('hits',[])
    except Exception as e:
        return -1,[]
rows=[]
for i,row in enumerate(jl[jl.cik.notna()].itertuples()):
    cik=row.cik
    perq,_=q('"personal use of company aircraft" OR "personal use of corporate aircraft" OR "personal use of our aircraft"',cik,'DEF 14A')
    time.sleep(0.2)
    ts,hits=q('"aircraft time sharing agreement" OR "aircraft dry lease"',cik)
    time.sleep(0.2)
    ex21,_=q('"Aviation, LLC" OR "Air, LLC" OR "Aviation, Inc."',cik,'10-K')
    time.sleep(0.2)
    rows.append(dict(ticker=row.ticker,sp_name=row.sp_name,total_musd=row.total_musd,cik=cik,
                     perq_def14a=perq, timeshare=ts, ex21_avi=ex21,
                     jet_disclosed=(perq>0 or ts>0 or ex21>0), entity_namable=(ts>0 or ex21>0)))
    if i%40==0: print(f'  {i}/{len(jl)} done')
r=pd.DataFrame(rows)
r.to_csv('sec_aircraft_signals_302.csv',index=False)
print('\n=== SEC EDGAR aircraft-signal pass on jetless dealmakers ===')
print('firms queried:',len(r))
print('jet DISCLOSED in SEC filings (perq/timeshare/ex21):', int(r.jet_disclosed.sum()),'({:.0%})'.format(r.jet_disclosed.mean()))
print('  via DEF14A perquisite           :', int((r.perq_def14a>0).sum()))
print('  via time-sharing/dry-lease exh. :', int((r.timeshare>0).sum()),'(names the entity)')
print('  via Exhibit-21 aviation subsid. :', int((r.ex21_avi>0).sum()),'(names the entity)')
print('ENTITY-NAMABLE (timeshare or ex21):', int(r.entity_namable.sum()),'({:.0%})'.format(r.entity_namable.mean()))
print('NO aircraft signal at all         :', int((~r.jet_disclosed).sum()),'(likely NetJets/charter/no-jet)')
print('\nsaved sec_aircraft_signals_302.csv')
print('\nTop disclosed-jet firms now newly addressable:')
print(r[r.entity_namable].sort_values('total_musd',ascending=False).head(15)[['ticker','sp_name','perq_def14a','timeshare','ex21_avi']].to_string(index=False))

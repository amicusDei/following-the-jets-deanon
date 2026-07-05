import json,re,time,urllib.request,urllib.parse,pandas as pd
UA={'User-Agent':'predfkitweball research your-email@example.com'}
def get(u,tries=5):
    for i in range(tries):
        try:
            d=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=35).read()
            if d: return d
        except Exception: pass
        time.sleep(1.5*(i+1))
    return b''
S=0.7
FTS='https://efts.sec.gov/LATEST/search-index'
sl=pd.read_csv('sec_entity_namable_shortlist.csv')
TAIL=re.compile(r'\bN[1-9]\d{1,4}[A-Z]{0,2}\b')
ENT=re.compile(r"([A-Z][A-Za-z0-9&\.'\- ]{2,38}?(?:Aviation|Aircraft|Wings|Flight Operations)[,]?\s+(?:LLC|L\.L\.C\.|Inc\.?|Corp\.?|LP))")
def urls(cik10,phrase):
    raw=get(FTS+'?'+urllib.parse.urlencode({'q':phrase,'ciks':cik10})); time.sleep(S)
    try: hits=json.loads(raw)['hits']['hits']
    except: return []
    return [f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{h['_id'].split(':')[0].replace('-','')}/{h['_id'].split(':')[1]}" for h in hits[:8]]
rows=[]
for f in sl.itertuples():
    cik10=str(int(f.cik)).zfill(10)            # FIX: zero-pad CIK for EDGAR FTS
    tails=set(); ents=set()
    for u in urls(cik10,'"aircraft time sharing agreement" OR "aircraft dry lease"'):
        txt=re.sub(r'<[^>]+>',' ',get(u).decode('utf-8','ignore')); time.sleep(S)
        for t in TAIL.findall(txt):
            if not re.match(r'N\d{1,2}$',t): tails.add(t)
        for e in ENT.findall(txt): ents.add(re.sub(r'\s+',' ',e).strip()[:44])
        if len(tails)>=3: break
    rows.append(dict(ticker=f.ticker,sp_name=f.sp_name,cik=cik10,tails=';'.join(sorted(tails)),entities=' | '.join(sorted(ents)[:6]),n_tails=len(tails)))
    print(f'{f.ticker:6} tails={len(tails)} {sorted(tails)[:8]}',flush=True)
r=pd.DataFrame(rows); r.to_csv('sec_extracted_aircraft.csv',index=False)
print('firms w/ tail:',int((r.n_tails>0).sum()),'/',len(r),'| total tails:',int(r.n_tails.sum()),flush=True)
biz=pd.read_parquet('/tmp/faa_bizjets.parquet'); biz['Nn']=biz.N.str.upper().str.lstrip('N')
b=biz.drop_duplicates('Nn').set_index('Nn'); recs=[]
for f in r.itertuples():
    for t in (f.tails.split(';') if f.tails else []):
        k=t.upper().lstrip('N')
        if k in b.index:
            row=b.loc[k]; recs.append(dict(ticker=f.ticker,sp_name=f.sp_name,tail=t,icao24=row.hex,owner=row.NAME,mfr=row.MFR,model=row.MODEL,state=row.STATE))
nj=pd.DataFrame(recs)
if len(nj): nj=nj.drop_duplicates(['ticker','icao24'])
nj.to_csv('sec_newly_identified_jets.csv',index=False)
print('=== newly identified business jets:',len(nj),'across',(nj.ticker.nunique() if len(nj) else 0),'firms ===',flush=True)
if len(nj): print(nj[['ticker','tail','icao24','owner','mfr','model']].to_string(index=False))

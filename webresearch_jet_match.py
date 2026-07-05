import pandas as pd
T={
'BMY':['N404M','N410M'],'CVX':['N1895T','N1901G','N443M','N5092','N884GL'],'CMCSA':['N63XF'],
'PFE':['N3CP','N4CP','N5CP','N6CP'],'ABBV':['N551AV','N552AV'],'NFLX':['N512GV','N533GV','N535GA'],
'CRM':['N650HA'],'FIS':['N206FS','N209FB'],'PLD':['N550FX','N622FX'],'KMB':['N506HG','N427HG','N641GA'],
'TMO':['N688CB'],'GOOGL':['N10XG','N904G'],'ADBE':['N82123'],'SCHW':['N113CS','N488CH','N910CS'],
'AMGN':['N552GA'],'ICE':['N201CE','N231CE','N703RK','N107CE','N106CE','N218GJ','N828SK','N905MT'],
'MS':['N727TE','N605JM','N810ET','N128GV','N168NJ','N456GA'],'MGM':['N721MM','N781MM','N782MM'],
'VZ':['N202VZ','N917VZ','N76VZ'],'PNC':['N513DL'],'JPM':['N601CH','N602CH','N661CH','N662CH'],
'CARR':['N1902C'],'CNC':['N848CC','N838CC','N858CC','N868CC','N898CC'],'MO':['N802AG','N803AG','N804AG'],
'PEP':['N500PC','N502PC','N503PC'],'GIS':['N750GM','N751GM'],'BAX':['N1BX','N9BX','N8BX'],
'BEN':['N988F','N123FT'],'ECL':['N899NC'],'GS':['N650WS','N280WS'],'UNH':['N954GA','N5UH','N57UH'],
'PSX':['N667P','N660P'],'MMM':['N83M','N93M'],'WYNN':['N88WR','N188WR'],'STZ':['N137SF','N870CM','N147SF'],
'GM':['N283PH','N284PH','N285PH'],'PRU':['N1875A','N82A'],'VFC':['N5VF','N4VF'],'KDP':['N234DP'],
'F':['N326K','N328K','N330K'],'DINO':['N31CA'],'CTVA':['N616CA'],'AEP':['N892AE','N893AE','N894AE'],
'APD':['N344AP'],'DGX':['N197DX'],'LH':['N475LH'],
}
rows=[(tk,t) for tk,ts in T.items() for t in ts]
df=pd.DataFrame(rows,columns=['ticker','tail'])
print('candidate tails from web research:',len(df),'across',df['ticker'].nunique(),'firms')
biz=pd.read_parquet('/tmp/faa_bizjets.parquet'); biz['Nn']=biz.N.str.upper().str.lstrip('N')
b=biz.drop_duplicates('Nn').set_index('Nn')
df['k']=df['tail'].str.upper().str.lstrip('N')
df['in_faa']=df['k'].isin(b.index)
m=df[df.in_faa].copy()
m['icao24']=m['k'].map(lambda x:b.loc[x].hex); m['owner']=m['k'].map(lambda x:b.loc[x].NAME)
m['mfr']=m['k'].map(lambda x:b.loc[x].MFR); m['model']=m['k'].map(lambda x:b.loc[x].MODEL); m['state']=m['k'].map(lambda x:b.loc[x].STATE)
print('matched to ACTIVE business jet in FAA:',len(m),'tails /',m['ticker'].nunique(),'firms')
print('  (dropped',len(df)-len(m),'= historical/sold/turboprop/deregistered)')
m[['ticker','tail','icao24','owner','mfr','model','state']].to_csv('webresearch_jets_faa.csv',index=False)
print(m[['ticker','tail','icao24','owner','model']].to_string(index=False))

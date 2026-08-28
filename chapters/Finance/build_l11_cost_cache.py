"""Cache for L11 · Transaction Costs.  Writes assets/data/l11_costs.parquet.
Everything uses the same rolling-product momentum construction L10 teaches."""
import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
B="assets/data/"
p=pd.read_parquet(B+"panel_backbone_1980_2000.parquet")
p=p[p.shrcd.isin([10,11])&p.exchcd.isin([1,2,3])].sort_values(['permno','date']).copy()
p['1+ret']=p['ret']+1
p=p.merge(pd.read_parquet(B+"signals/DolVol.parquet"),on=['permno','date'],how='left')
p['dvol']=np.exp(-p['DolVol'])                      # signal files are sign-flipped
p=p.merge(pd.read_parquet(B+"signals/BM.parquet"),on=['permno','date'],how='left')
p['cumret']=(p.groupby('permno')['1+ret'].rolling(11,min_periods=11)
              .apply(np.prod,raw=True).reset_index(level=0,drop=True))
p['mom']=p.groupby('permno')['cumret'].shift(1)
p['sd']=p.groupby('permno')['ret'].transform(lambda s:s.rolling(36,min_periods=12).std())

def build(sig='mom',wcol='me',minvol=None):
    d=p.dropna(subset=[sig,'ret_fwd','me','dvol','sd']).copy()
    if minvol is not None:
        d=d[d.groupby('date')['dvol'].transform(lambda s:s.rank(pct=True))>=minvol]
    def dec(x):
        e=np.unique(np.quantile(x.loc[x.exchcd==1,sig],np.linspace(0,1,11))); e[0],e[-1]=-np.inf,np.inf
        return pd.cut(x[sig],e,labels=False,duplicates='drop')
    d['g']=d.groupby('date',group_keys=False).apply(dec)
    d=d[d.g.isin([0,9])].copy(); d['side']=np.where(d.g==9,1.,-1.)
    d['w']=d.groupby(['date','g'])[wcol].transform(lambda s:s/s.sum())*d['side']
    return d
def rets(d):
    r=d.groupby('date').apply(lambda x:(x.w*x.ret_fwd).sum()); r.index=r.index+pd.offsets.MonthEnd(1); return r
def trades(d):
    W=d.pivot_table(index='date',columns='permno',values='w').fillna(0)
    R=d.pivot_table(index='date',columns='permno',values='ret_fwd').reindex_like(W).fillna(0)
    dts=W.index; TR={}; drift=[]; naive=[]
    for i in range(1,len(dts)):
        prev,r=W.iloc[i-1],R.iloc[i-1]; dr=prev*(1+r)
        for leg in (1,-1):
            m=np.sign(prev)==leg; s=np.abs(dr[m]).sum()
            if s>0: dr[m]=dr[m]/s*np.abs(prev[m]).sum()
        t=W.iloc[i]-dr; TR[dts[i]]=t[t!=0]
        drift.append(t.abs().sum()/2); naive.append((W.iloc[i]-prev).abs().sum()/2)
    return TR, pd.Series(drift,index=dts[1:]), pd.Series(naive,index=dts[1:])
# Cost model, calibrated to Frazzini-Israel-Moskowitz "Trading Costs of Asset
# Pricing Anomalies" (their Fig. p.46 fits c(bp) ~ 9 + 144*sqrt(participation)).
#   c_i = spread/2  +  KAPPA * sigma_daily_i * sqrt(Q_i / V_i)
# sigma must be measured over the EXECUTION horizon.  A month's trade spread over
# ~21 days makes that daily volatility, so sigma_monthly / sqrt(21).
KAPPA  = 0.55        # implied by FIM's slope at typical volatility
SPREAD = 0.0020      # 20bp half-spread; wide-ish for 2004-13, thin for 1980-2000
def costs(d,TR,AUM,K=KAPPA,spread=SPREAD):
    info=d.set_index(['date','permno'])[['dvol','sd']]; o={}
    for dt,tr in TR.items():
        j=info.loc[dt].reindex(tr.index).dropna()
        if not len(j): continue
        Q=tr.reindex(j.index).abs()*AUM
        sd_daily=j['sd']/np.sqrt(21)
        c=spread + K*sd_daily*np.sqrt(Q/j['dvol'])
        o[dt+pd.offsets.MonthEnd(1)]=(Q*c).sum()/AUM
    return pd.Series(o)

AUMS=[100,250,500,1000,2500,5000,10000,25000,50000,100000]
out={}
wish=build(); TRw,dw,nw = trades(wish)
out['mom_gross']=rets(wish); out['turn_mom']=dw; out['turn_mom_naive']=nw
for A in AUMS: out[f'cost_{A}']=costs(wish,TRw,A)
scr=build(minvol=0.4); TRs,_,_ = trades(scr)
out['scr_gross']=rets(scr)
for A in AUMS: out[f'scrcost_{A}']=costs(scr,TRs,A)
vw=build(wcol='dvol'); TRv,dv_,_ = trades(vw)
out['vw_gross']=rets(vw); out['turn_vw']=dv_
for A in [250,1000]: out[f'vwcost_{A}']=costs(vw,TRv,A)
bm=build(sig='BM'); TRb,db,nb = trades(bm)
out['bm_gross']=rets(bm); out['turn_bm']=db; out['turn_bm_naive']=nb
D=pd.DataFrame(out)
D.index.name='date'; D.to_parquet(B+"l11_costs.parquet")
print(f"l11_costs.parquet  {D.shape}  {D.index.min():%Y-%m}..{D.index.max():%Y-%m}")

# used-volume distribution for the wish portfolio at $10bn, all months pooled
info=wish.set_index(['date','permno'])['dvol']; rows=[]
for dt,tr in TRw.items():
    j=info.loc[dt].reindex(tr.index).dropna()
    if len(j): rows.append(pd.Series((tr.reindex(j.index).abs()*10000)/j))
UV=pd.concat(rows)
pd.DataFrame({'used_volume':UV.values}).to_parquet(B+"l11_usedvolume.parquet",index=False)
print(f"l11_usedvolume.parquet  {len(UV):,} stock-months  median {UV.median():.1%}  "
      f"p95 {UV.quantile(.95):.0%}  max {UV.max():.0%}")

# signal decay
dec={}
for name,sig in [('momentum','mom'),('value','BM')]:
    d=build(sig=sig)
    W=d.pivot_table(index='date',columns='permno',values='w').fillna(0)
    R=p.pivot_table(index='date',columns='permno',values='ret_fwd').reindex(index=W.index,columns=W.columns).fillna(0)
    dec[name]={f'lag{L}':(W.shift(L)*R).sum(axis=1).iloc[12:] for L in [0,1,2,3,6,12]}
DEC=pd.DataFrame({f'{k}_{kk}':vv for k,v in dec.items() for kk,vv in v.items()})
DEC.to_parquet(B+"l11_decay.parquet"); print(f"l11_decay.parquet  {DEC.shape}")

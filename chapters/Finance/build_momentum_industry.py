"""Four industry treatments of momentum, on the labelled (~950-stock) universe.
Uses the SAME rolling-product construction the L10 notebook teaches."""
import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
p=pd.read_parquet("assets/data/panel_backbone_1980_2000.parquet")
p=p[p.shrcd.isin([10,11])&p.exchcd.isin([1,2,3])].sort_values(['permno','date']).copy()
p['1+ret']=p['ret']+1
p['cumret']=(p.groupby('permno')['1+ret'].rolling(11,min_periods=11).apply(np.prod,raw=True)
              .reset_index(level=0,drop=True))
p['mom']=p.groupby('permno')['cumret'].shift(1)
lab=pd.read_parquet("assets/data/industry_labels.parquet")
m=p.merge(lab,on=['permno','date'],how='inner').dropna(subset=['mom','ret_fwd','me'])
m['mom_ia']=m['mom']-m.groupby(['date','ind'])['mom'].transform('mean')
sh=lambda x:x.mean()/x.std()*np.sqrt(12)
def sp(df,signal,vw,ngroups=10):
    d=df.dropna(subset=[signal]).copy()
    def b(x):
        e=np.unique(np.quantile(x.loc[x.exchcd==1,signal],np.linspace(0,1,ngroups+1)))
        e[0],e[-1]=-np.inf,np.inf
        return pd.cut(x[signal],e,labels=False,duplicates='drop')
    d['g']=d.groupby('date',group_keys=False).apply(b)
    w=(lambda x:np.average(x.ret_fwd,weights=x.me)) if vw else (lambda x:x.ret_fwd.mean())
    dec=d.groupby(['date','g']).apply(w).unstack()
    s=(dec[ngroups-1]-dec[0]).dropna(); s.index=s.index+pd.offsets.MonthEnd(1); return s
res={}
for vw,tag in [(True,'VW'),(False,'EW')]:
    f=(lambda x:np.average(x.ret_fwd,weights=x.me)) if vw else (lambda x:x.ret_fwd.mean())
    res[f'plain_{tag}']=sp(m,'mom',vw); res[f'neutral_{tag}']=sp(m,'mom_ia',vw)
    m['pct']=m.groupby(['date','ind'])['mom'].rank(pct=True)
    big=m[m.groupby(['date','ind'])['permno'].transform('size')>=6]
    hi=big[big.pct>=2/3].groupby(['date','ind']).apply(f); lo=big[big.pct<=1/3].groupby(['date','ind']).apply(f)
    w_=(hi.groupby('date').mean()-lo.groupby('date').mean()).dropna(); w_.index=w_.index+pd.offsets.MonthEnd(1)
    res[f'within_{tag}']=w_
    iw=m.groupby(['date','ind']).apply(f).unstack(); isig=m.groupby(['date','ind'])['mom'].mean().unstack()
    rk=isig.rank(axis=1,ascending=False)
    ac=(iw.where(rk<=8).mean(axis=1)-iw.where(rk>=rk.max(axis=1).values[:,None]-7).mean(axis=1)).dropna()
    ac.index=ac.index+pd.offsets.MonthEnd(1); res[f'across_{tag}']=ac
D=pd.DataFrame(res).dropna(); D.to_parquet("assets/data/momentum_industry.parquet")
print(f"momentum_industry.parquet {D.shape}  {D.index[0]:%Y-%m}..{D.index[-1]:%Y-%m}\n")
print(f"{'':10s}{'VW mean':>10s}{'VW SR':>8s}{'EW mean':>10s}{'EW SR':>8s}")
for k in ['plain','neutral','within','across']:
    v,e=D[f'{k}_VW'],D[f'{k}_EW']
    print(f"  {k:8s}{v.mean()*12:>9.1%}{sh(v):>8.2f}{e.mean()*12:>9.1%}{sh(e):>8.2f}")
import statsmodels.api as sm
print("\nEW ladders:")
for y,x in [('neutral_EW','across_EW'),('across_EW','neutral_EW'),('plain_EW','neutral_EW')]:
    r=sm.OLS(D[y],sm.add_constant(D[x])).fit()
    print(f"  {y:11s} on {x:11s} alpha {r.params.iloc[0]*12:+7.1%}/yr  t {r.tvalues.iloc[0]:+.2f}")
print(f"corr(neutral_EW, across_EW) = {D[['neutral_EW','across_EW']].corr().iloc[0,1]:.2f}")

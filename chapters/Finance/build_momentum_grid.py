import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
p=pd.read_parquet("assets/data/panel_backbone_1980_2000.parquet")
p=p[p.shrcd.isin([10,11])&p.exchcd.isin([1,2,3])].sort_values(['permno','date']).copy()
p['lr']=np.log1p(p['ret'].clip(lower=-0.9999))
g=p.groupby('permno')['lr']
sh=lambda x:x.mean()/x.std()*np.sqrt(12)

def signal(J,skip):
    return np.expm1(g.transform(lambda s:s.rolling(J).sum().shift(skip)))

def longshort(sig,nq=10,vw=True,nyse=True):
    d=p.assign(s=sig).dropna(subset=['s','ret_fwd','me'])
    def cut(x):
        ref=x.loc[x.exchcd==1,'s']
        ref=ref if len(ref)>20 else x['s']
        e=np.unique(np.quantile(ref if nyse else x['s'],np.linspace(0,1,nq+1)))
        e[0],e[-1]=-np.inf,np.inf
        return pd.cut(x['s'],e,labels=False,duplicates='drop')
    d=d.assign(q=d.groupby('date',group_keys=False).apply(cut))
    f=(lambda x:np.average(x.ret_fwd,weights=x.me)) if vw else (lambda x:x.ret_fwd.mean())
    r=d.groupby(['date','q']).apply(f).unstack()
    s=(r[nq-1]-r[0]).dropna()
    s.index=s.index+pd.offsets.MonthEnd(1)      # date by the month EARNED
    return s

out={}
print("── A. lookback J, skip=1 ──")
for J in [1,3,6,9,11,17,23,35,47,59]:
    s=longshort(signal(J,1)); out[f'J{J}_s1']=s
    print(f"  J={J:2d} skip=1   mean {s.mean()*12:+7.1%}  Sharpe {sh(s):+.2f}")
print("── B. skip, J=11 ──")
for k in [0,1,2,3,6]:
    s=longshort(signal(11,k)); out[f'J11_s{k}']=s
    print(f"  skip={k}        mean {s.mean()*12:+7.1%}  Sharpe {sh(s):+.2f}")
print("── C. weighting / breakpoints / quantiles, J=11 skip=1 ──")
base=signal(11,1)
for lab,kw in [("VW, NYSE bp, deciles",dict()),("EW, NYSE bp, deciles",dict(vw=False)),
               ("VW, ALL-stock bp, deciles",dict(nyse=False)),("EW, ALL-stock bp, deciles",dict(vw=False,nyse=False)),
               ("VW, NYSE bp, quintiles",dict(nq=5)),("VW, NYSE bp, 20 groups",dict(nq=20)),
               ("VW, NYSE bp, terciles",dict(nq=3))]:
    s=longshort(base,**kw); out[lab]=s
    print(f"  {lab:28s} mean {s.mean()*12:+7.1%}  Sharpe {sh(s):+.2f}  vol {s.std()*np.sqrt(12):5.1%}")
pd.DataFrame(out).to_parquet("/private/tmp/claude-502/-Users-am16634-Documents-GitHub-UG54/b8283dbc-8732-4f04-bc8c-6fee0b7bd44a/scratchpad/momgrid.parquet")
print("\nsaved", len(out), "series")

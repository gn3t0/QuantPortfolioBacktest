version = 1.0

import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import time
import sys

def my_arange(a, b, dr, decimals=6):
    res = [a]
    k = 1
    while res[-1] < b:
        tmp = round(a + k*dr,decimals)
        if tmp >= b:
            break   
        res.append(tmp)
        k+=1

    return np.asarray(res)

#--------------------------------------------------------------------------

def atr(df, period):

    c = len(df)
    tr = np.zeros(c)

    tr[0]=df.High[0]-df.Low[0]

    close = df.Close[0]
    i=1
    for row in df[1:].itertuples():
        tr1 = row.High -row.Low
        tr2 = abs(row.High-close)
        tr3 = abs(row.Low-close)
        tr[i] = max(max(tr1, tr2), tr3)
        close = row.Close
        i+=1

    tr = pd.Series(tr)
    atr=tr.ewm(adjust=False, alpha =1/period).mean()

    return {'TR':tr.to_numpy(),
            'ATR': atr.to_numpy()}

#--------------------------------------------------------------------------

def dmi(df, period_dmi):

    c = len(df)
    dm_plus = np.ones(c)
    dm_minus = np.ones(c)
    tr = np.ones(c)

    high = df.High[0]
    low = df.Low[0]
    close = df.Close[0]
  
    tr[0]=df.High[0]-df.Low[0]
    
    i=1
    for row in df[1:].itertuples():
        dm_plus[i] = max(row.High-high,0)
        dm_minus[i] = max(low-row.Low,0)
        
        if dm_plus[i]==dm_minus[i]:
            dm_plus[i]=0
            dm_minus[i]=0
        elif dm_plus[i]<dm_minus[i]: dm_plus[i]=0
        else: dm_minus[i]=0
        
        high = row.High
        low = row.Low
        tr1 = row.High -row.Low
        tr2 = abs(row.High-close)
        tr3 = abs(row.Low-close)
        tr[i] = max(max(tr1, tr2), tr3)
        close = row.Close
        i+=1

    tr = pd.Series(tr)
    ATR=tr.ewm(adjust=False, alpha =1/period_dmi).mean()

    dm_plus = pd.Series(dm_plus)
    plus_D = dm_plus.ewm(adjust=False, alpha =1/period_dmi).mean()
    plus_D = plus_D.div(ATR)
    plus_D = plus_D.multiply(other=100)

    dm_minus = pd.Series(dm_minus)
    minus_D = dm_minus.ewm(adjust=False, alpha =1/period_dmi).mean()
    minus_D = minus_D.div(ATR)
    minus_D = minus_D.multiply(other=100)

    return plus_D.to_numpy(), minus_D.to_numpy()

#--------------------------------------------------------------------------

def rolling_window(a, window):
    
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    if shape[0]<=0: return([])
    frames = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    
    return frames

#--------------------------------------------------------------------------

def rolling_stddev(period, series):

    if len(series.values) < period: 
        nan = np.empty(len(series.values))
        nan[:]=np.NaN
        return(nan)

    rw=rolling_window(series.values,period)
    nan = np.empty(period-1)
    nan[:]=np.NaN
    std = np.concatenate((nan,np.std(rw,axis=1,ddof=1)))

    return(std)

#--------------------------------------------------------------------------

def ema(period, series):

    pd_series = pd.Series(series)
    pd_ema = pd_series.ewm(span=period, adjust=False).mean()

    return (pd_ema.to_numpy())
    
#--------------------------------------------------------------------------

def linreg(period, series):

    c = len(series)
    lr = np.zeros(c)

    x = np.array(range(period)).reshape((-1, 1))

    for i in range(period-1,c,1):
        y = series[i-period+1:i+1].values
        model = LinearRegression().fit(x, y)
        lr[i]=model.coef_

    return(lr)

#--------------------------------------------------------------------------

def rolling_osc(series, period):

    c = len(series)
    osc = np.zeros(c)

    for i in range(period-1,c,1):
        sub=series[slice(i-period+1,i+1)]
        h=max(sub)
        l=min(sub)
        if h==l: 
            osc[i] = 0       
        else: 
            osc[i] = (series[i]-l)/(h-l)
     
    return(osc)

#--------------------------------------------------------------------------

def tukey_filter(trades_trt, option):

    # 0(OFF); 1(1-99); 2(1-99/exclude tickers)
    
    trade_res = [v[0] for v in trades_trt]
    q1, q3 = np.percentile(trade_res, [1, 99])
    iqr = q3 - q1
    fator = 1.5
    #lowpass = q1 - (iqr * fator)
    highpass_p = q3 + (iqr * fator)

    trade_res = [v[3] for v in trades_trt]
    q1, q3 = np.percentile(trade_res, [1, 99])
    iqr = q3 - q1
    fator = 1.5
    #lowpass = q1 - (iqr * fator)
    highpass_r = q3 + (iqr * fator)

    if option==1:
        texto = [v[1] for v in trades_trt if v[0]<highpass_p and v[3]<highpass_r]

    elif option==2: # exclude tickers
        
        tickers_x = [v[2] for v in trades_trt if v[0]>=highpass_p] # retirar somente tickers ou outliers de delta percentual
        tickers_x = list(dict.fromkeys(tickers_x))
        print("excluidos por tukey_filter:")
        print(tickers_x)
        texto = [v[1] for v in trades_trt if v[2] not in tickers_x]

    return texto

#--------------------------------------------------------------------------

def rolling_highest(series, period):

    c = len(series)
    osc = np.zeros(c)

    for i in range(period-1,c,1):
        sub=series[slice(i-period+1,i+1)]
        osc[i]=max(sub)
     
    return(osc)

#--------------------------------------------------------------------------

def rolling_lowest(series, period):

    c = len(series)
    osc = np.zeros(c)

    for i in range(period-1,c,1):
        sub=series[slice(i-period+1,i+1)]
        osc[i]=min(sub)
     
    return(osc)

#--------------------------------------------------------------------------


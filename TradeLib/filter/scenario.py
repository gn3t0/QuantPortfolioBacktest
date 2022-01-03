version = 1.0

MIN_BARS = 130

from TradeLib import calclib as calc
import pandas as pd 

def filter(O, H, L, C, df, i, number):
     
    if number==0: return False
    if number==1: return True
    
    switcher={

    2: C[4]>df.HH_M[i-1],
    3: C[4]<df.LL_M[i-1],
    4: C[4]>df.HH_L[i-1],
    5: C[4]<df.LL_L[i-1],

    6: C[4]>df.EMA_M[i] and C[4]>df.EMA_L[i], 
    7: C[4]<df.EMA_M[i] and C[4]<df.EMA_L[i], 

    8: C[4]>df.EMA_M[i] + 2.0*df.ATR[i], 
    9: C[4]<df.EMA_M[i] - 2.0*df.ATR[i],   
 
    10: df.EMA_XS[i-1]>df.EMA_S[i-1] and df.EMA_S[i-1]>df.EMA_M[i-1],
    11: df.EMA_XS[i-1]<df.EMA_S[i-1] and df.EMA_S[i-1]<df.EMA_M[i-1],
    12: df.EMA_S[i-1]>df.EMA_M[i-1] and df.EMA_M[i-1]>df.EMA_L[i-1],
    13: df.EMA_S[i-1]<df.EMA_M[i-1] and df.EMA_M[i-1]<df.EMA_L[i-1],

    14: df.plus_D[i]>df.minus_D[i],
    15: df.plus_D[i]<df.minus_D[i],

    16: df.STDDEV_OSC[i]>=1,
    17: df.STDDEV_OSC[i]<=0,

    18: df.plus_D_ibov[i]>df.minus_D_ibov[i],
    19: df.plus_D_ibov[i]<df.minus_D_ibov[i],

    20: df.ATR_ibov[i]>df.EMA_S_ATR_ibov[i],
    21: df.ATR_ibov[i]<df.EMA_S_ATR_ibov[i],
   
    }

    ret  =  switcher.get(abs(number),None)

    if number<0 : ret = not ret

    return ret

#--------------------------------------------------------------------------

def filter_calc(df, df_ibov, filter_scenario=[], large_period=125, medium_period=50, small_period=21, xsmall_period=9):

        
    df_ibov['ATR'] = calc.atr(df_ibov,14)['ATR']
    df_ibov['EMA_S_ATR'] = calc.ema(period=small_period,series=df_ibov['ATR'])  
    df_ibov['plus_D'], df_ibov['minus_D'] = calc.dmi(df_ibov,14)
    df_ibov = pd.merge(df_ibov,df[[]], left_index=True, right_index=True)
    df['ATR_ibov']=df_ibov['ATR']
    df['EMA_S_ATR_ibov']=df_ibov['EMA_S_ATR']
    df['plus_D_ibov']=df_ibov['plus_D']
    df['minus_D_ibov']= df_ibov['minus_D']

    stddev = calc.rolling_stddev(period=20, series=df['Close'])
    df['STDDEV_OSC'] = calc.rolling_osc(series=stddev, period=20)

    if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
    df['EMA_XS']=calc.ema(period=xsmall_period,series=df['Close'])        
    df['EMA_S']=calc.ema(period=small_period,series=df['Close'])        
    df['EMA_M']=calc.ema(period=medium_period,series=df['Close'])        
    df['EMA_L']=calc.ema(period=large_period,series=df['Close'])        

    df['HH_L'] = calc.rolling_highest(series=df['High'],period=large_period)
    df['HH_M'] = calc.rolling_highest(series=df['High'],period=medium_period)
    df['LL_L'] = calc.rolling_lowest(series=df['Low'],period=large_period)
    df['LL_M'] = calc.rolling_lowest(series=df['Low'],period=medium_period)

    df['plus_D'], df['minus_D'] = calc.dmi(df,14)

#--------------------------------------------------------------------------
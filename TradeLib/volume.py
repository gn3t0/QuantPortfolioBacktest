version = 1.0

MIN_BARS = 20

from TradeLib import calclib as calc
import pandas as pd
import numpy as np
import time

def filter_qtde(df, i, number):
    
    if number==0:return(True)
    return (df.EMA_Volume[i] >= number*1000)

#--------------------------------------------------------------------------

def filter_neg(df, i, number):
     
    if number==0:return(True)
    return (df.EMA_Neg[i] >= number*1000)

#--------------------------------------------------------------------------

def filter_fin(df, i, number):
     
    if number==0:return(True)
    return (df.EMA_Fin[i] >= number*1000)

#--------------------------------------------------------------------------

def filter_ranking(df, bar, filter, filter_rank):

    if filter_rank==0: return(True)

    rank = df.iloc[bar][filter]

    if filter_rank > 0: 
        return(rank < filter_rank)#/100)
    else:
        return(rank > -filter_rank)#/100)
       

#--------------------------------------------------------------------------

# def hampel_filter_old(input_series, window_size, n_sigmas=3):
    
#     n = len(input_series)
#     new_series = input_series.copy()
#     k = 1.4826 # gaussian scale factor
    
#     for i in range(window_size,n):
#         x0 = np.nanmedian(input_series[(i - window_size):i])
#         S0 = k * np.nanmedian(np.abs(input_series[(i - window_size):i] - x0))
#         if (np.abs(input_series[i] - x0) > n_sigmas * S0):
#             new_series[i] = x0
#     return new_series

def hampel_filter(input_series, window_size, n_sigmas=3):
    
    n = len(input_series)
    if n < window_size+1 : return(input_series)
    new_series = input_series.copy()
    k = 1.4826 # gaussian scale factor
    
    rw = calc.rolling_window(input_series,window_size)
    x0= np.nanmedian(rw,axis=1)
    x0_reshape = x0.reshape(len(x0),1)
    x0_tile = np.tile(x0_reshape,(1,window_size))
    d=rw-x0_tile
    abs_d =np.abs(d)
    nm_abs_d = np.nanmedian(abs_d,axis=1)
    S0 = k*nm_abs_d
    d1= input_series - np.concatenate((np.zeros(window_size),x0[0:-1]))
    abs_d1 = np.abs(d1)

    for i in range(window_size,n):
        rw_i = i-window_size
        if abs_d1[i] > n_sigmas * S0[rw_i]:
            new_series[i] = x0[rw_i]
    return new_series

#--------------------------------------------------------------------------

def calc_fin(O,H,L,C,V,Fin): 
    if Fin==0:
        return (O*2+H+L+C*2)/6*V
    else:
        return Fin

def filter_calc(df, filter_volume_qtde, filter_volume_neg, filter_volume_fin):

    if filter_volume_qtde > 0:
        volume = hampel_filter(df['Volume'].values, 20)
        df['EMA_Volume']=calc.ema(period=20,series=volume)

    if filter_volume_neg > 0:
        neg = hampel_filter(df['Neg'].values, 20)
        df['EMA_Neg']=calc.ema(period=20,series=neg)

    df["Fin"]=df.apply(lambda row: calc_fin(row["Open"],row["High"],row["Low"],row["Close"],row["Volume"],row["Fin"]),axis=1)
    fin = hampel_filter(df['Fin'].values, 20)
    df['EMA_Fin']=calc.ema(period=20,series=fin)
    
#--------------------------------------------------------------------------

def rank_calc(df, ticker, txt, filter_volume_qtde_ranking, filter_volume_neg_ranking, filter_volume_fin_ranking):

    if filter_volume_qtde_ranking !=0:
        df_rank_qtde=pd.DataFrame()
        df_rank_qtde = pd.read_csv(txt.replace(ticker+".txt","ranking_qtde.csv"),index_col="Date")
        df_rank_qtde.Ticker= df_rank_qtde.Ticker.apply(lambda x: list(x.split(",")))   
        # df_rank_qtde['count']= df_rank_qtde['Ticker'].map(len)
        df_rank_qtde = df_rank_qtde[df_rank_qtde.apply(lambda df: ticker in df.Ticker, axis=1)]
        df_rank_qtde.Ticker = df_rank_qtde.Ticker.apply(lambda x: x.index(ticker))   
        df['volume_rank']=df_rank_qtde.Ticker
        # df['volume_rank']=df_rank_qtde.Ticker/df_rank_qtde['count']*100
    
    if filter_volume_neg_ranking !=0: 
        df_rank_neg=pd.DataFrame()
        df_rank_neg = pd.read_csv(txt.replace(ticker+".txt","ranking_neg.csv"),index_col="Date")
        df_rank_neg.Ticker= df_rank_neg.Ticker.apply(lambda x: list(x.split(",")))   
        # df_rank_neg['count']= df_rank_neg['Ticker'].map(len)
        df_rank_neg = df_rank_neg[df_rank_neg.apply(lambda df: ticker in df.Ticker, axis=1)]
        df_rank_neg.Ticker = df_rank_neg.Ticker.apply(lambda x: x.index(ticker))   
        df['neg_rank']=df_rank_neg.Ticker
        # df['neg_rank']=df_rank_neg.Ticker/df_rank_neg['count']*100

    if filter_volume_fin_ranking !=0: 
        df_rank_fin=pd.DataFrame()
        df_rank_fin = pd.read_csv(txt.replace(ticker+".txt","ranking_fin.csv"),index_col="Date")
        df_rank_fin.Ticker= df_rank_fin.Ticker.apply(lambda x: list(x.split(",")))   
        # df_rank_fin['count']= df_rank_fin['Ticker'].map(len)
        df_rank_fin = df_rank_fin[df_rank_fin.apply(lambda df: ticker in df.Ticker, axis=1)]
        df_rank_fin.Ticker = df_rank_fin.Ticker.apply(lambda x: x.index(ticker))   
        df['fin_rank']=df_rank_fin.Ticker
        # df['fin_rank']=df_rank_fin.Ticker/df_rank_fin['count']*100

#--------------------------------------------------------------------------

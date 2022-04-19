version = 1.01

MIN_BARS = 21

import numpy as np
from TradeLib import calclib as calc
from TradeLib.filter import scenario
from TradeLib.filter import ohlc


def trail_stop (df, size, multiple_unit, reference_calc='Close', reference_reset='Low', side = 'L'):

    c = len(df)
    trail= np.zeros(c)

    if size>0:

        list_index = list(df)
        multiple_unit_index = list_index.index(multiple_unit)+1
        reference_calc_index = list_index.index(reference_calc)+1
        reference_reset_index = list_index.index(reference_reset)+1
        
        t = df[reference_calc][0]-size*df[multiple_unit][0] 
        trail[0]=t
        
        i=1
        for row in df[1:].itertuples():
            t = row[reference_calc_index] - size * row[multiple_unit_index]
            if row[reference_reset_index] < trail[i-1]:
                trail[i]=t
            else:
                trail[i]=max(t, trail[i-1])
            i+=1
    
    return(trail)

#--------------------------------------------------------------------------

def breakeven_calc(entry_price, breakeven_level, initial_stop, side='L'):

    if breakeven_level>0 and breakeven_level <=10:
        return(entry_price + breakeven_level * (entry_price-initial_stop))
    else: # percentual
        return( entry_price*(((breakeven_level-10)/100)+1) )

#--------------------------------------------------------------------------

def stoploss_level_calc(entry_price, stoploss_level, initial_stop, side='L'):

    if stoploss_level>0 and stoploss_level <=10:
        return(entry_price + stoploss_level * (entry_price-initial_stop))
    else: # percentual
        return( entry_price*(((stoploss_level-10)/100)+1) )

#--------------------------------------------------------------------------

def stoploss_calc(df, stop_loss_1, stop_loss_2, stop_loss_3, side='L'):


    if stop_loss_1 > 0 and stop_loss_1 < 10:
        if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
        df['stop_loss_1']= trail_stop(df, stop_loss_1, 'ATR', reference_calc='Close', reference_reset='Low')

    if stop_loss_2 > 0 and stop_loss_2 < 10:
        if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
        df['stop_loss_2']= trail_stop(df, stop_loss_2, 'ATR', reference_calc='Close', reference_reset='Low')

    if stop_loss_3 > 0 and stop_loss_3 < 10:
        if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
        df['stop_loss_3']= trail_stop(df, stop_loss_3, 'ATR', reference_calc='Close', reference_reset='Low')

#--------------------------------------------------------------------------

def initial_stop_calc(df, initial_stop, side='L'):

    if initial_stop >0 and initial_stop <=10:
        if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
        df['initial_stop']=df['Low']-initial_stop*df['ATR']
        return

    if initial_stop >10 and initial_stop <=20:
        if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
        df['initial_stop']=df['entry_order_price']-(initial_stop-10)*df['ATR']
        return

    if initial_stop >20 and initial_stop <=30:
        if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
        df['initial_stop']=df['High']-(initial_stop-20)*df['ATR']
        return

    if initial_stop >30 and initial_stop <=40:
        if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
        df['initial_stop']= trail_stop(df, initial_stop-30, 'ATR', reference_calc='Close', reference_reset='Low')
        return

    if initial_stop >40 and initial_stop <=50:
        if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
        df['initial_stop']= trail_stop(df, initial_stop-40, 'ATR', reference_calc='Low', reference_reset='Low')
        return

    df['initial_stop']=0

#--------------------------------------------------------------------------

def gain_calc(df, gain, side='L'):

    if gain >0 and gain <=10:
        if not 'ATR' in df: df['ATR']=calc.atr(df,14)['ATR']
        df['gain']=df['entry_order_price']+gain*df['ATR']
        return

    df['gain']=0

#--------------------------------------------------------------------------

def gain_move(trade, df, bar, gain, side='L'):

    pass

#--------------------------------------------------------------------------

def percent (df, series='Close', name='PERCENT'):
    
    df[name] = df[series] * 0.01

#--------------------------------------------------------------------------

def stoploss_move (trade, df, bar, breakeven_level, stoploss_1, stoploss_2, stoploss_3, side='L'):

    level=0
    if trade.state[:1]=='T':
        level = int(trade.state[-1:])

    if stoploss_1>0 and level<1 and df.Low[bar]>trade.stoploss_level_1_price:
        trade.state='TS1'
    if stoploss_2>0 and level<2 and df.Low[bar]>trade.stoploss_level_2_price:
        trade.state='TS2'
    if stoploss_3>0 and level<3 and df.Low[bar]>trade.stoploss_level_3_price:
        trade.state='TS3'

    if level>0:
        if level==1:
            if df.stop_loss_1[bar]>trade.stop_price: 
                trade.stop_price=df.stop_loss_1[bar]
        elif level==2:
            if df.stop_loss_2[bar]>trade.stop_price: 
                trade.stop_price=df.stop_loss_2[bar]
        elif level==3:
            if df.stop_loss_3[bar]>trade.stop_price: 
                trade.stop_price=df.stop_loss_3[bar]

    if breakeven_level>0 and trade.stop_price < trade.entry_price:
        if df.Low[bar]>trade.breakeven_level_price: 
            trade.stop_price=trade.entry_price

#--------------------------------------------------------------------------

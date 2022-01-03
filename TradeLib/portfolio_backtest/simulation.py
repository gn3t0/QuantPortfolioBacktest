version = 1.01

import pandas as pd
import numpy as np
import datetime
import time
import multiprocessing
import sys
import random
import xlsxwriter
import argparse
import random
import os
from itertools import takewhile
import ntpath

version_txt='\n' + os.path.basename(__file__) + ' = ' + str(version)

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def run(version_txt, lock, simulation_list, monte_carlo_iterations, filename, folder_history_data, base_trades_1, base_trades_2, base_trades_3, 
                date_start, date_end, initial_capital, position_size_model, position_size_model_desc, portfolio_heat, risk_round, 
                trade_risk_1, trade_risk_2, trade_risk_3, trade_size_limit_1, trade_size_limit_2, trade_size_limit_3, 
                trans_cost_fixed, trans_cost_percent, trans_slippage, max_open_trades, 
                pyramid_profit, pyramid_trades, trans_volume_max, daily_update,
                filename_args, folder_backtest,folder_base_trades, cdi, benchmark):

    trt = pd.DataFrame()

    if base_trades_1!='':
        with open(base_trades_1+".trt", 'r') as fobj:
            list(takewhile(lambda s: not s.startswith("##"), fobj))
            comments_1=list(takewhile(lambda s: s.startswith("##"), fobj))
        fobj.close()
        trt_i1 = pd.read_csv(base_trades_1+".trt", delimiter=' ', comment='#',
            names = ["Ticker","Trade_Position","Entry_Date","Exit_Date","Initial_Stop","Entry_Price","Exit_Price","Low_Entry_Price","High_Entry_Price","Low_Exit_Price","High_Exit_Price","Traded_Volume","Trade_Rank","Point_Value","Initial_Margin"],
            parse_dates = ['Entry_Date','Exit_Date'])
        trt_i1['trade_risk']=np.full(len(trt_i1),trade_risk_1)
        trt_i1['trade_size_limit']=np.full(len(trt_i1),trade_size_limit_1) 
        trt_i1['base_trades_1']=path_leaf(base_trades_1)
        trt = pd.concat([trt,trt_i1], ignore_index=True)

    if base_trades_2!='':
        with open(base_trades_2+".trt", 'r') as fobj:
            list(takewhile(lambda s: not s.startswith("##"), fobj))
            comments_2 = list(takewhile(lambda s: s.startswith('##'), fobj))
        fobj.close()
        trt_i2 = pd.read_csv(base_trades_2+".trt", delimiter=' ', comment='#',
            names = ["Ticker","Trade_Position","Entry_Date","Exit_Date","Initial_Stop","Entry_Price","Exit_Price","Low_Entry_Price","High_Entry_Price","Low_Exit_Price","High_Exit_Price","Traded_Volume","Trade_Rank","Point_Value","Initial_Margin"],
            parse_dates = ['Entry_Date','Exit_Date'])
        trt_i2['trade_risk']=np.full(len(trt_i2),trade_risk_2)
        trt_i2['trade_size_limit']=np.full(len(trt_i2),trade_size_limit_2) 
        trt_i2['base_trades_2']=path_leaf(base_trades_2)
        trt = pd.concat([trt,trt_i2], ignore_index=True)

    if base_trades_3!='':
        with open(base_trades_3+".trt", 'r') as fobj:
            list(takewhile(lambda s: not s.startswith("##"), fobj))
            comments_3 = list(takewhile(lambda s: s.startswith('##'), fobj))
        fobj.close()
        trt_i3 = pd.read_csv(base_trades_3+".trt", delimiter=' ', comment='#',
            names = ["Ticker","Trade_Position","Entry_Date","Exit_Date","Initial_Stop","Entry_Price","Exit_Price","Low_Entry_Price","High_Entry_Price","Low_Exit_Price","High_Exit_Price","Traded_Volume","Trade_Rank","Point_Value","Initial_Margin"],
            parse_dates = ['Entry_Date','Exit_Date'])
        trt_i3['trade_risk']=np.full(len(trt_i3),trade_risk_3)
        trt_i3['trade_size_limit']=np.full(len(trt_i3),trade_size_limit_3) 
        trt_i3['base_trades_3']=path_leaf(base_trades_3)
        trt = pd.concat([trt,trt_i3], ignore_index=True)
    
    trt = trt.drop_duplicates()

    if date_start and date_end:
        trt = trt.loc[(trt.Entry_Date>=date_start) & (trt.Entry_Date<=date_end)] #'2016-07-29']
    elif date_start:
        trt = trt.loc[trt.Entry_Date>=date_start]
    elif date_end:
        trt = trt.loc[trt.Entry_Date<=date_end]

    trt = trt.reset_index(drop=True).reset_index()
    trt_np = trt.values
    
    # Simulation

    start = trt_np[:,3].min() 
    trt_entry_dates = set(trt_np[:,3])
    trt_exit_dates = set(trt_np[:,4])

    if monte_carlo_iterations==1:
        if date_start:
            start = date_start
        end = trt_np[:,4].max() 
        date_line = pd.date_range(start=start, end =end)
    else:
        date_line = sorted(trt_entry_dates|trt_exit_dates) 

    # df_np
    # 'date'0, 'trade_i'1, 'symbol'2, 'position'3, 'transaction'4, 'initial_stop'5, 'price'6, 'p_size'7, 'cost'8, 'slippage'9, 'capital'10, 
    # 'equity_trades'11, 'equity'12, 'risk'13, 'portfolio_heat'14, 'peak'15, 'under_water'16, 'under_water_%'17, 'open_trades'18, 'profit_loss'19, 'base_trades_i'20, 
    # 'equity_daily'21, 'peak_daily'22, 'under_water_daily'23, 'under_water_%_daily'24

    if daily_update==True:
        df_np =np.array([[start, '', '', '', '', '', '', '', '', '', '', 0, initial_capital, '', 0, initial_capital, 0, 0, 0, 0,'', initial_capital, initial_capital, 0, 0]])
    else:
        df_np =np.array([[start, '', '', '', '', '', '', '', '', '', '', 0, initial_capital, '', 0, initial_capital, 0, 0, 0, 0,'', 0, 0, 0, 0]])

    dfx_np = np.empty([0,25]) 

    open_trades=np.empty([0,3]) 

    trade_tickers = list(dict.fromkeys(trt_np[:,1]))
    len_trade_tickers = len(trade_tickers)

    for d in date_line:

        if d.weekday()<5:

            # ENTRIES
            if d in trt_entry_dates:

                shape_df=df_np.shape[0]                   
                equity = df_np[shape_df-1][12] 
                if pyramid_profit==False:
                    equity = min(initial_capital,equity)

                if position_size_model==2 or df_np.item(df_np.shape[0]-1,14) < portfolio_heat*equity: # there are possible entries for current date

                    #  trt_np
                    # 'Index'0, 'Ticker'1, 'Trade_Position'2, 'Entry_Date'3, 'Exit_Date'4, 'Initial_Stop'5, 'Entry_Price'6, 'Exit_Price'7, 
                    # 'Low_Entry_Price'8, 'High_Entry_Price'9, 'Low_Exit_Price'10, 'High_Exit_Price'11, 'Traded_Volume'12, 'Trade_Rank'13, 
                    # 'Point_Value'14, 'Initial_Margin'15, 'trade_risk'16, 'trade_size_limit'17, 'base_trades_i'18

                    trt_trades = trt_np[np.in1d(trt_np[:,3],[d])] 
                    
                    shape_trt=trt_trades.shape[0]
                    rand_list = random.sample(range(shape_trt),shape_trt)
                    # rand_list = list(range(0,shape_trt,1)) # original order

                    for k in rand_list:

                        if max_open_trades>0:
                            if len(open_trades) >= max_open_trades: break

                        trade = trt_trades[k]

                        if pyramid_trades==False:
                            if trade[1] in list(open_trades[:,1]): continue #0.01s

                        shape_df=df_np.shape[0]
                        
                        equity = df_np[shape_df-1][12] 
                        if pyramid_profit==False:
                            equity = min(initial_capital,equity)

                        equity_trades = df_np[shape_df-1][11] 

                        ph=df_np[shape_df-1][14]
                        
                        if position_size_model==1:
                            position_size = np.floor((equity/100*trade[16])/(trade[6]-trade[5]))*100          
                        else:
                            position_size = np.floor((equity/100*trade[17])/(trade[6]))*100 

                        if risk_round==True:
                            position_risk = trade[16]*equity
                            if position_size_model==1:
                                if (ph+position_risk) > (portfolio_heat*equity): continue
                        else:
                            position_risk = (trade[6]-trade[5])*position_size                    
                        
                        if position_size_model==1:  # Trade size limit                                           
                            if (position_size*trade[6]) > (trade[17]*equity): 
                                position_size = np.floor(((trade[17]*equity)/100)/(trade[6]))*100 
                                position_risk = (trade[6]-trade[5])*position_size        
                            if (ph+position_risk) > (portfolio_heat*equity): continue
                        
                        if position_size<=0 or position_risk<=0 : continue                       
                        position_entry_capital = position_size*trade[6]
                        position_entry_cost = position_entry_capital*trans_cost_percent+trans_cost_fixed
                        position_entry_slippage = position_entry_capital*trans_slippage
                        position_entry_total = position_entry_capital+position_entry_cost+position_entry_slippage

                        if (equity_trades+position_entry_total) > equity:                           
                            if len_trade_tickers==1:
                                position_size = np.floor(((equity-equity_trades)/100)/(trade[6]))*100 
                                position_risk = (trade[6]-trade[5])*position_size                       
                                if position_size<=0 or position_risk<=0 : continue  
                                position_entry_capital = position_size*trade[6]
                                position_entry_cost = position_entry_capital*trans_cost_percent+trans_cost_fixed
                                position_entry_slippage = position_entry_capital*trans_slippage
                            else: continue

                        if trans_volume_max > 0 :
                            if position_entry_capital>trans_volume_max*trade[12]: continue

                        #  trt_np
                        # 'Index'0, 'Ticker'1, 'Trade_Position'2, 'Entry_Date'3, 'Exit_Date'4, 'Initial_Stop'5, 'Entry_Price'6, 'Exit_Price'7, 
                        # 'Low_Entry_Price'8, 'High_Entry_Price'9, 'Low_Exit_Price'10, 'High_Exit_Price'11, 'Traded_Volume'12, 'Trade_Rank'13, 
                        # 'Point_Value'14, 'Initial_Margin'15, 'trade_risk'16, 'trade_size_limit'17, 'base_trades_i'18

                        # df_np
                        # 'date'0, 'trade_i'1, 'symbol'2, 'position'3, 'transaction'4, 'initial_stop'5, 'price'6, 'p_size'7, 'cost'8, 'slippage'9, 'capital'10, 
                        # 'equity_trades'11, 'equity'12, 'risk'13, 'portfolio_heat'14, 'peak'15, 'under_water'16, 'under_water_%'17, 'open_trades'18, 'profit_loss'19, 'base_trades_i'20, 
                        # 'equity_daily'21, 'peak_daily'22, 'under_water_daily'23, 'under_water_%_daily'24

                        new_entry = [[d, # 0
                                    trade[0], # 1
                                    trade[1], # 2
                                    trade[2], # 3
                                    'Entry', # 4
                                    trade[5], # 5
                                    trade[6], # 6
                                    position_size, # 7
                                    position_entry_cost, # 8
                                    position_entry_slippage, # 9
                                    position_entry_capital, # 10
                                    (equity_trades+position_entry_capital), # 11
                                    df_np[shape_df-1][12]-position_entry_cost-position_entry_slippage, # 12
                                    position_risk, # 13
                                    round(ph+position_risk,5), # 14
                                    df_np[shape_df-1][15], # 15
                                    df_np[shape_df-1][16], # 16
                                    round(df_np[shape_df-1][17],5), # 17
                                    len(open_trades)+1, # 18
                                    0, # 19
                                    trade[18], # 20
                                    df_np[shape_df-1][21], # 21
                                    df_np[shape_df-1][22], # 22
                                    df_np[shape_df-1][23], # 23
                                    df_np[shape_df-1][24]]] # 24

                        df_np = np.append(df_np,new_entry,axis=0)
                        open_trades= np.append(open_trades,[[trade[0],new_entry[0][2],position_size]],axis=0)
                       
                        # DAILY_UPDATE 
                        if daily_update==True:
                            ticker = new_entry[0][2]
                            if 'df_'+ticker not in locals():
                                df_ticker = pd.read_csv(folder_history_data + '/' + ticker+ ".txt", index_col=None, usecols=['Date', 'Close'], parse_dates=['Date'])
                                # df_ticker = df_ticker[(df_ticker.Date>=d) & (df_ticker.Date<=trade[4])]
                                # df_ticker = df_ticker.loc[(df_ticker.Date>=d)]
                                exec('df_'+ ticker + '=df_ticker.loc[(df_ticker.Date>=d)]')


                        new_exit = new_entry.copy()
                        new_exit[0][0]=trade[4]
                        dfx_np = np.append(dfx_np,new_exit,axis=0)


            # EXITS     
            dfx_np_exits = dfx_np[np.in1d(dfx_np[:,0],[d])] 
            if dfx_np_exits.size>0:
                for x in dfx_np_exits:
     
                    # df_np
                    # 'date'0, 'trade_i'1, 'symbol'2, 'position'3, 'transaction'4, 'initial_stop'5, 'price'6, 'p_size'7, 'cost'8, 'slippage'9, 'capital'10, 
                    # 'equity_trades'11, 'equity'12, 'risk'13, 'portfolio_heat'14, 'peak'15, 'under_water'16, 'under_water_%'17, 'open_trades'18, 'profit_loss'19, 'base_trades_i'20, 
                    # 'equity_daily'21, 'peak_daily'22, 'under_water_daily'23, 'under_water_%_daily'24
                   
                    position_exit_capital = x[7]*trt_np[x[1]][7]
                    position_entry_capital=x[10]
                    position_entry_total_cost = x[8]+x[9]
                    position_exit_cost = position_exit_capital*trans_cost_percent+trans_cost_fixed
                    position_exit_slippage = position_exit_capital*trans_slippage
                    position_exit_total_cost = position_exit_cost+position_exit_slippage
                    position_profit=position_exit_capital-position_entry_capital          
                    
                    x[4]='Exit'
                    x[6]=trt_np[x[1]][7]
                    x[8]=position_exit_cost
                    x[9]=position_exit_slippage
                    x[10]=position_exit_capital
                    x[11]=(df_np[df_np.shape[0]-1][11]-position_entry_capital)
                    x[12]=df_np[df_np.shape[0]-1][12]+position_profit-position_exit_total_cost
                    x[14]=(df_np[df_np.shape[0]-1][14]-x[13])
                    x[15]=max(x[12],df_np[df_np.shape[0]-1][15])
                    x[16]=x[12]-x[15]
                    x[17]=x[16]/x[15]
                    x[18]=len(open_trades)-1
                    x[19]=position_profit-position_exit_total_cost-position_entry_total_cost
                    shape_df=df_np.shape[0]
                    x[21]=df_np[shape_df-1][21]
                    x[22]=df_np[shape_df-1][22]
                    x[23]=df_np[shape_df-1][23]
                    x[24]=df_np[shape_df-1][24]

                    df_np = np.append(df_np,[x],axis=0)
                    id=str(x[1])
                    if id in list(open_trades[:,0]): 
                        open_trades = open_trades[np.in1d(list(open_trades[:,0]),id,invert=True)]     

                    # DAILY_UPDATE
                    if daily_update==True:                    
                        if x[2] not in list(open_trades[:,1]):
                            del [locals()['df_'+ x[2]]]

        # DAILY_UPDATE
        shape_df=df_np.shape[0]
        if daily_update==True:
            if d.weekday()<5:
                equity_daily=0
                for ot in open_trades:
                    shares = float(ot[2])
                    ticker = ot[1]
                    mask = (locals()['df_'+ticker].Date<=d)
                    tick = locals()['df_'+ticker].loc[mask].iat[-1,1]
                    equity_daily+= tick*shares

                equity_daily+= df_np[shape_df-1][12]-df_np[shape_df-1][11]
                peak_daily = max(equity_daily,df_np[shape_df-1][22])
                under_water_daily = equity_daily-peak_daily
                under_water_p_daily = under_water_daily/peak_daily
                new_entry = [[d, '', '', '', '', '', '', '', '', '', '', df_np[shape_df-1][11], df_np[shape_df-1][12], '', df_np[shape_df-1][14], 
                                df_np[shape_df-1][15], df_np[shape_df-1][16], df_np[shape_df-1][17], len(open_trades), 0, '', 
                                equity_daily, peak_daily, under_water_daily, under_water_p_daily]]
            else:
                new_entry = [[d, '', '', '', '', '', '', '', '', '', '', df_np[shape_df-1][11], df_np[shape_df-1][12], '', df_np[shape_df-1][14], 
                                df_np[shape_df-1][15], df_np[shape_df-1][16], df_np[shape_df-1][17], len(open_trades), 0, '', 
                                df_np[shape_df-1][21], df_np[shape_df-1][22], df_np[shape_df-1][23], df_np[shape_df-1][24]]]
            df_np = np.append(df_np,new_entry,axis=0)

        elif monte_carlo_iterations==1:
            new_entry = [[d, '', '', '', '', '', '', '', '', '', '', df_np[shape_df-1][11], df_np[shape_df-1][12], '', df_np[shape_df-1][14], 
                            df_np[shape_df-1][15], df_np[shape_df-1][16], df_np[shape_df-1][17], len(open_trades), 0, '', 
                            0, 0, 0, 0]]
            df_np = np.append(df_np,new_entry,axis=0)


    total_trades = len(trt_np)
    trades_taken = dfx_np.shape[0]      
    profit = round(df_np[df_np.shape[0]-1][12]-initial_capital,5)
    profit_percent =round(profit/initial_capital,5)
    max_drawdown = round(df_np[:,16].min(),5) 
    max_drawdown_daily = round(df_np[:,23].min(),5) 
    max_drawdown_p = round(df_np[:,17].min(),5)
    max_drawdown_p_daily = round(df_np[:,24].min(),5)
    if max_drawdown==0:
        recovery = profit
        recovery_p = profit_percent
    else:
        recovery = profit/(-max_drawdown/(1-(-max_drawdown/profit)))
        recovery_p = profit_percent/(-max_drawdown_p/(1+max_drawdown_p))
    if max_drawdown_daily==0:
        recovery_daily = 0 
        recovery_p_daily = 0
    else:
        recovery_daily = profit/(-max_drawdown_daily/(1-(-max_drawdown_daily/profit)))
        recovery_p_daily = profit_percent/(-max_drawdown_p_daily/(1+max_drawdown_p_daily))
    if len(df_np[df_np[:,4]=='Entry'])==0:
        hit_rate=0
    else:
        hit_rate = len(df_np[df_np[:,19]>0])/len(df_np[df_np[:,4]=='Entry'])
    trade_profit_max = df_np[:,19].max()
    trade_loss_max = df_np[:,19].min()
    ex = df_np[df_np[:,4]=='Exit']
    avg_win=0
    if len(ex[ex[:,19]>0,19])>0:
        avg_win = ex[ex[:,19]>0,19].mean() 
    avg_loss=0
    if len(ex[ex[:,19]<=0,19])>0:
        avg_loss = ex[ex[:,19]<=0,19].mean() 
    avg=0
    if len(ex[:,19])>0:
        avg = ex[:,19].mean() 

    d_start = trt_np[:,3].min()
    d_start= int(str(d_start.year)+str(d_start.month).zfill(2)+str(d_start.day).zfill(2))
    d_end = trt_np[:,4].max()
    d_end= int(str(d_end.year)+str(d_end.month).zfill(2)+str(d_end.day).zfill(2))

    lock.acquire()
    simulation_list.append("%.0f %.0f %.0f %.0f %.2f %.2f %.2f %.2f %.2f %.10f %.10f %.10f %.2f %.2f %.10f %.2f %.2f %.2f %.2f %.2f" % 
    (d_start, d_end, total_trades, trades_taken, profit, max_drawdown, max_drawdown_daily, recovery, recovery_daily, 
        profit_percent, max_drawdown_p, max_drawdown_p_daily, recovery_p, recovery_p_daily, 
        hit_rate, avg, avg_win, avg_loss, trade_profit_max, trade_loss_max))
    lock.release()
 
    if monte_carlo_iterations==1: 

        # trades worksheet ---------------------------------------------------------------------------------------------------------------------------

        df = pd.DataFrame(df_np, columns = ['date', 'trade_i', 'symbol', 'position', 'transaction', 'initial_stop', 'price', 'p_size', 
                                            'cost', 'slippage', 'capital', 'equity_trades', 'equity', 'risk', 'portfolio_heat', 'peak', 
                                            'under_water', 'under_water_%', 'open_trades', 'profit_loss', 'base_trades_i', 
                                            'equity_daily', 'peak_daily', 'under_water_daily', 'under_water_%_daily'])     

        df['date'] = df['date'].dt.strftime('%m/%d/%Y')
        df['equity_%'] = (df['equity']-initial_capital)/initial_capital
        df['portfolio_heat_$']=df['portfolio_heat']*1
        if pyramid_profit==False:
            df['portfolio_heat'] = np.maximum(df['portfolio_heat_$']/df['equity'], df['portfolio_heat_$']/initial_capital)
        else:
            df['portfolio_heat'] = df['portfolio_heat_$']/df['equity']

        if daily_update==True:
            df['equity_%_daily'] = (df['equity_daily']-initial_capital)/initial_capital
        else:
            df['equity_%_daily'] = 0

        # final order
        df = df[['date', 'trade_i', 'symbol', 'position', 'transaction', 'initial_stop', 'price', 'p_size', # B C D E F G H I
                'cost', 'slippage', 'capital', 'equity_trades', 'equity', 'equity_%', 'risk', 'portfolio_heat_$', 'portfolio_heat', 'peak', # J K L M N O P Q R S
                'under_water', 'under_water_%', 'open_trades', 'profit_loss', 'base_trades_i', # T U V W X
                'equity_daily', 'equity_%_daily', 'peak_daily', 'under_water_daily', 'under_water_%_daily']]  # Y Z AA AB AC

        
        writer = pd.ExcelWriter(filename + '.xlsx', engine='xlsxwriter')
        workbook = writer.book
        worksheet = workbook.add_worksheet('report')
        worksheet.hide_gridlines([1])
        
        f_money = workbook.add_format({'num_format': '$#,##0.00'})
        f_percent = workbook.add_format({'num_format': '0.00%'})
        f_double = workbook.add_format({'num_format': '0.00'})
        f_center = workbook.add_format({'align':'center'})
        f_right = workbook.add_format({'align':'right'})
        
        df.to_excel(writer, sheet_name='trades')
        ws_trades=workbook.get_worksheet_by_name('trades')
        ws_trades.hide_gridlines([1])
        ws_trades.set_column('J:J', None, f_money)
        ws_trades.set_column('L:L', None, f_money)
        ws_trades.set_column('M:M', None, f_money)
        ws_trades.set_column('N:N', None, f_money)
        ws_trades.set_column('P:P', None, f_money)
        ws_trades.set_column('Q:Q', None, f_money)
        ws_trades.set_column('S:S', None, f_money)
        ws_trades.set_column('T:T', None, f_money)
        ws_trades.set_column('W:W', None, f_money)
        ws_trades.set_column('Y:Y', None, f_money)
        ws_trades.set_column('AA:AA', None, f_money)
        ws_trades.set_column('AB:AB', None, f_money)
        ws_trades.set_column('O:O', None, f_percent)
        ws_trades.set_column('R:R', None, f_percent)
        ws_trades.set_column('U:U', None, f_percent)
        if daily_update==True:
            ws_trades.set_column('Z:Z', None, f_percent)
            ws_trades.set_column('AC:AC', None, f_percent)

        df=df[df['transaction']=='']


        df = df[['date', 'equity_trades', 'equity', 'equity_%', 'portfolio_heat_$', 'portfolio_heat', 'peak', 
                'under_water', 'under_water_%', 'open_trades',
                'equity_daily', 'equity_%_daily', 'peak_daily', 'under_water_daily', 'under_water_%_daily']] 

        if cdi==True:
            try:
                df_bench = pd.read_csv(folder_history_data+'/CDI.csv', sep=',', parse_dates = ['Date'])
                df_bench.columns = ['date','CDI']   
                df_bench['date']=df_bench['date'].dt.strftime('%m/%d/%Y')     
                df = pd.merge(df,df_bench, on='date', how='left')
                df['CDI'] = df['CDI'].fillna(0)
                df.loc[0,'CDI']=0
                df['CDI'] = (1+df['CDI']/100).cumprod()
                df['CDI'] = df['CDI'] -1
            except: pass

        if benchmark!='':
            try:
                df_bench = pd.read_csv(benchmark, sep=',', parse_dates = ['Date'])
                df_bench['Close'] = df_bench['Close'].pct_change()
                df_bench = df_bench[['Date','Close']]
                df_bench.columns = ['date','benchmark']   
                df_bench['date']=df_bench['date'].dt.strftime('%m/%d/%Y')     
                df = pd.merge(df,df_bench, on='date', how='left')
                df['benchmark'] = df['benchmark'].fillna(0)
                df.loc[0,'benchmark']=0
                df['benchmark'] = (1+df['benchmark']).cumprod()
                Roll_Max = df['benchmark'].rolling(len(df['benchmark']), min_periods=1).max()
                Daily_Drawdown = df['benchmark']/Roll_Max
                df['benchmark_dd']  = Daily_Drawdown 
                df['benchmark'] = df['benchmark'] -1
                df['benchmark_dd'] = df['benchmark_dd'] -1

            except: pass

        df.to_excel(writer, sheet_name='chart')
        ws_trades=workbook.get_worksheet_by_name('chart')
        ws_trades.hide_gridlines([1])
        ws_trades.set_column('E:E', None, f_percent)
        ws_trades.set_column('G:G', None, f_percent)
        ws_trades.set_column('J:J', None, f_percent)
        # ws_trades.set_column('Q:Q', None, f_percent)
        if daily_update==True:
            ws_trades.set_column('M:M', None, f_percent)
            ws_trades.set_column('P:P', None, f_percent)


        # report worksheet ---------------------------------------------------------------------------------------------------------------------------
        

        report_columns = [  'Position_Size_Model',
                            'Base_Trades_1', 'Trade_risk_1', 'Trade_size_limit_1',
                            'Base_Trades_2', 'Trade_risk_2', 'Trade_size_limit_2',
                            'Base_Trades_3', 'Trade_risk_3', 'Trade_size_limit_3',
                            '',
                            'Initial_Capital', 'Portfolio_heat_max', 'Pyramid_Profits', 'Pyramid_Trades', 'Daily_Update', 'Max_open_trades', 'Risk_round', 'Trans_cost_fixed', 'Trans_cost_percent', 'Trans_slippage', 
                            'Trans_volume_max',
                            '',
                            'Date_start', 'Date_end',
                            'Total Trades', 'Trades_Taken', 
                            'Net_Profit', "Max_DDown", "Max_DDown_daily", 
                            'Recovery_factor', 'Recovery_f_daily',
                            'Net_Profit_%', "Max_DDown_%", "Max_DDown_%_daily", 
                            'Recovery_factor_%', 'Recovery_f_%_daily',
                            'Hit_rate', 
                            'Trade_avg', 'Trade_avg_win', 'Trade_avg_loss',
                            'Trade_profit_max', 'Trade_loss_max']
        
        row0=0
        col0=0
        for r in range(0,len(report_columns),1):
            r+=row0
            c=col0
            worksheet.write(r,c,report_columns[r])

        worksheet.write(row0,col0+1,str(position_size_model_desc[position_size_model-1]))        

        if base_trades_1!='':
            row0+=1
            worksheet.write(row0,col0+1,path_leaf(base_trades_1))
            row0+=1
            if position_size_model==1:
                worksheet.write(row0,col0+1,trade_risk_1,f_percent)
            else:
                worksheet.write(row0,col0+1,'-',f_center)     
            row0+=1
            worksheet.write(row0,col0+1,trade_size_limit_1,f_percent)
        else:
            row0+=1
            worksheet.write(row0,col0+1,'-',f_center)
            row0+=1
            worksheet.write(row0,col0+1,'-',f_center)
            row0+=1
            worksheet.write(row0,col0+1,'-',f_center)           

        if base_trades_2!='':
            row0+=1
            worksheet.write(row0,col0+1,path_leaf(base_trades_2))
            row0+=1
            if position_size_model==1:
                worksheet.write(row0,col0+1,trade_risk_2,f_percent)
            else:
                worksheet.write(row0,col0+1,'-',f_center)     
            row0+=1
            worksheet.write(row0,col0+1,trade_size_limit_2,f_percent)
        else:
            row0+=1
            worksheet.write(row0,col0+1,'-',f_center)
            row0+=1
            worksheet.write(row0,col0+1,'-',f_center)
            row0+=1
            worksheet.write(row0,col0+1,'-',f_center)           
        
        if base_trades_3!='':
            row0+=1
            worksheet.write(row0,col0+1,path_leaf(base_trades_3))
            row0+=1
            if position_size_model==1:
                worksheet.write(row0,col0+1,trade_risk_3,f_percent)
            else:
                worksheet.write(row0,col0+1,'-',f_center)     
            row0+=1
            worksheet.write(row0,col0+1,trade_size_limit_3,f_percent)
        else:
            row0+=1
            worksheet.write(row0,col0+1,'-',f_center)
            row0+=1
            worksheet.write(row0,col0+1,'-',f_center)
            row0+=1
            worksheet.write(row0,col0+1,'-',f_center)
                
        row0+=2
        worksheet.write(row0,col0+1,initial_capital,f_money)
        row0+=1
        if position_size_model==1:
            worksheet.write(row0,col0+1,portfolio_heat, f_percent)
        else:
            worksheet.write(row0,col0+1,'-',f_center)     
        row0+=1
        worksheet.write(row0,col0+1,str(pyramid_profit),f_right)
        row0+=1
        worksheet.write(row0,col0+1,str(pyramid_trades),f_right)
        row0+=1
        worksheet.write(row0,col0+1,str(daily_update),f_right)        
        row0+=1
        worksheet.write(row0,col0+1,max_open_trades)
        row0+=1
        if position_size_model==1:
            worksheet.write(row0,col0+1,str(risk_round),f_right)     
        else:
            worksheet.write(row0,col0+1,'-',f_center)     
        row0+=1
        worksheet.write(row0,col0+1,trans_cost_fixed,f_money)
        row0+=1
        worksheet.write(row0,col0+1,trans_cost_percent,f_percent)
        row0+=1
        worksheet.write(row0,col0+1,trans_slippage,f_percent)
        row0+=1
        worksheet.write(row0,col0+1,trans_volume_max,f_percent)

        row0+=2
        worksheet.write(row0,col0+1,d_start)
        row0+=1
        worksheet.write(row0,col0+1,d_end)
        row0+=1
        worksheet.write(row0,col0+1,total_trades)
        row0+=1
        worksheet.write(row0,col0+1,trades_taken)
        row0+=1
        worksheet.write(row0,col0+1,profit,f_money)
        row0+=1
        worksheet.write(row0,col0+1,max_drawdown,f_money)
        row0+=1
        if daily_update==True:
            worksheet.write(row0,col0+1,max_drawdown_daily,f_money)
        else:
            worksheet.write(row0,col0+1,'-',f_center)
        row0+=1
        worksheet.write(row0,col0+1,recovery,f_double) 
        row0+=1
        if daily_update==True:          
            worksheet.write(row0,col0+1,recovery_daily,f_double)           
        else:
            worksheet.write(row0,col0+1,'-',f_center)
        row0+=1
        worksheet.write(row0,col0+1,profit_percent,f_percent)
        row0+=1
        worksheet.write(row0,col0+1,max_drawdown_p,f_percent)
        row0+=1
        if daily_update==True:
            worksheet.write(row0,col0+1,max_drawdown_p_daily,f_percent)
        else:
            worksheet.write(row0,col0+1,'-',f_center)
        row0+=1
        worksheet.write(row0,col0+1,recovery_p,f_double) 
        row0+=1
        if daily_update==True:          
            worksheet.write(row0,col0+1,recovery_p_daily,f_double)           
        else:
            worksheet.write(row0,col0+1,'-',f_center)
        row0+=1
        worksheet.write(row0,col0+1,hit_rate,f_percent)
        row0+=1
        worksheet.write(row0,col0+1,avg,f_money)
        row0+=1
        worksheet.write(row0,col0+1,avg_win,f_money)
        row0+=1
        worksheet.write(row0,col0+1,avg_loss,f_money)
        row0+=1    
        worksheet.write(row0,col0+1,trade_profit_max,f_money)
        row0+=1
        worksheet.write(row0,col0+1,trade_loss_max,f_money)
        row0+=1


        worksheet.set_column(col0, col0, 20)
        worksheet.set_column(col0+1, col0+1, 13)

        # equity chart
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({'values': '=chart!D2:D' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'equity_$', 'line':{'width':1}})
        if daily_update==True:
            chart.add_series({'values': '=chart!L2:L' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'daily', 'line':{'width':1}})
            max_y=np.ceil(max(df.equity.max(),df.equity_daily.max())/1000)*1000+1000
            min_y=np.ceil(min(df.equity.min(),df.equity_daily.min())/1000)*1000-1000
        else:
            max_y=np.ceil(df.equity.max()/1000)*1000+1000
            min_y=np.ceil(df.equity.min()/1000)*1000-1000
            chart.set_legend({'none': True})
        chart.set_y_axis({'min':str(min_y), 'max':str(max_y) })
        chart.set_x_axis({'date_axis': True})
        chart.set_x_axis({'visible': False})
        worksheet.insert_chart('D10', chart)


        # equity% chart

        max_y=df['equity_%'].max()
        min_y=df['equity_%'].min()
        cols = list(df)
        if 'CDI' in cols: 
            max_y = np.ceil(max(df['CDI'].max(),max_y)*100)/100
            min_y = np.floor(min(df['CDI'].min(),min_y)*100)/100
        if 'benchmark' in cols: 
            max_y = np.ceil(max(df['benchmark'].max(),max_y)*100)/100
            min_y = np.floor(min(df['benchmark'].min(),min_y)*100)/100

        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({'values': '=chart!E2:E' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'equity_%', 'line':{'width':1}})
        if daily_update==True:
            chart.add_series({'values': '=chart!M2:M' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'daily', 'line':{'width':1}})
            max_y=np.ceil(max(max_y,df['equity_%_daily'].max())*100)/100
            min_y=np.floor(min(min_y,df['equity_%_daily'].min())*100)/100
        if cdi==True or benchmark!=0:
            chart.add_series({'values': '=chart!Q2:Q' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': '=chart!Q1', 'line':{'width':1}})
            if cdi==True and benchmark!=0:     
                chart.add_series({'values': '=chart!R2:R' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': '=chart!R1', 'line':{'width':1}})            

        chart.set_y_axis({'min':str(min_y), 'max':str(max_y) })
        chart.set_x_axis({'date_axis': True})
        chart.set_x_axis({'visible': False})
        worksheet.insert_chart('L10', chart)

        # underwater chart
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({'values': '=chart!I2:I' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'under_water_$', 'line':{'width':1}})
        max_y=0
        if daily_update==True:
            chart.add_series({'values': '=chart!O2:O' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'daily', 'line':{'width':1}})
            min_y=np.ceil(min(df.under_water.min(),df.under_water_daily.min())/1000-1)*1000
        else:
            min_y=np.ceil(df.under_water.min()/1000-1)*1000
            chart.set_legend({'none': True})
        chart.set_y_axis({'min':str(min_y), 'max':str(max_y) })
        chart.set_x_axis({'date_axis': True})
        chart.set_x_axis({'visible': False})
        worksheet.insert_chart('D25', chart)


        # underwater_% chart
        min_y=df['under_water_%'].min()
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({'values': '=chart!J2:J' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'under_water_%', 'line':{'width':1}})
        max_y=0
        if daily_update==True:
            chart.add_series({'values': '=chart!P2:P' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'daily', 'line':{'width':1}})
            min_y=np.floor(min(min_y,df['under_water_%_daily'].min())*100)/100
        if benchmark!='':
            min_y=np.floor(min(df['benchmark_dd'].min(),min_y)*100)/100
            if cdi==True:
                chart.add_series({'values': '=chart!S2:S' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'benchmark', 'line':{'width':1}})
            else:
                chart.add_series({'values': '=chart!R2:R' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'benchmark', 'line':{'width':1}})
        chart.set_y_axis({'min':str(min_y), 'max':str(max_y) })
        chart.set_x_axis({'date_axis': True})
        chart.set_x_axis({'visible': False})
        worksheet.insert_chart('L25', chart)


        # portfolio heat_$
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({'values': '=chart!F2:F' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'portfolio_heat_$', 'line':{'width':1}})
        max_y=np.ceil(df['portfolio_heat_$'].max()/1000)*1000
        min_y=0
        chart.set_y_axis({'min':str(min_y), 'max':str(max_y) })
        chart.set_legend({'none': True})
        chart.set_x_axis({'date_axis': True})
        chart.set_x_axis({'visible': False})
        worksheet.insert_chart('D40', chart)

        # portfolio heat_%
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({'values': '=chart!G2:G' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'portfolio_heat_%', 'line':{'width':1}})
        max_y=np.ceil(df.portfolio_heat.max()*100)/100
        min_y=0
        chart.set_y_axis({'min':str(min_y), 'max':str(max_y) })
        chart.set_legend({'none': True})
        chart.set_x_axis({'date_axis': True})
        chart.set_x_axis({'visible': False})
        worksheet.insert_chart('L40', chart)

        # capital_in_trades_$
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({'values': '=chart!C2:C' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'capital_in_trades_$', 'line':{'width':1}})
        max_y=np.ceil(df.equity_trades.max()/1000)*1000+1000
        min_y=0
        chart.set_y_axis({'min':str(min_y), 'max':str(max_y) })
        chart.set_legend({'none': True})
        chart.set_x_axis({'date_axis': True})
        chart.set_x_axis({'visible': False})
        worksheet.insert_chart('D55', chart)

        # open_trades
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({'values': '=chart!K2:K' + str(len(df)+1), 'categories':'=chart!B2:B' + str(len(df)+1), 'name': 'open_trades', 'line':{'width':1}})
        max_y=df.open_trades.max()+1
        min_y=0
        chart.set_y_axis({'min':str(min_y), 'max':str(max_y) })
        chart.set_legend({'none': True})
        chart.set_x_axis({'date_axis': True})
        chart.set_x_axis({'visible': False})
        worksheet.insert_chart('L55', chart)

        # print SIM filename input parameters
        r=0
        c=19
        worksheet.set_column(c, c, 90)
        worksheet.write(r,c,filename.replace(folder_backtest + "/" ,''))
        r+=1
        worksheet.write(r,c,'')
        z =''
        for variable in filename_args:
            if variable=="":
                r+=1
                worksheet.write(r,c,z)
                z=''
            else:
                z+= '(' + variable + "= " + str(eval(variable)) + ') '

        if benchmark!='':
            r+=2
            worksheet.write(r,c,'benchmark')
            r+=1
            ord_sum=0
            for letter in path_leaf(benchmark): ord_sum+=ord(letter)
            benchmark_ord = benchmark +' -> '+str(ord_sum)
            worksheet.write(r,c,benchmark_ord)

        # print BaseTrades1 input parameters
        if base_trades_1!='':
            r=0
            c+=1
            worksheet.set_column(c, c, 90)
            worksheet.write(r,c,'Base_Trades_1')
            r+=1
            worksheet.write(r,c,base_trades_1+".trt")
            r+=1
            worksheet.write(r,c,'')
            for linha in comments_1:
                r+=1
                linha = linha.replace('## ','')
                worksheet.write(r,c,linha.replace('\n',''))

        # print BaseTrades2 input parameters
        if base_trades_2!='':
            r=0
            c+=1
            worksheet.set_column(c, c, 90)
            worksheet.write(r,c,'Base_Trades_2')
            r+=1
            worksheet.write(r,c,base_trades_2+".trt")
            r+=1
            worksheet.write(r,c,'')
            for linha in comments_2:
                r+=1
                worksheet.write(r,c,linha.replace('## ',''))

        # print BaseTrades3 input parameters
        if base_trades_3!='':
            r=0
            c+=1
            worksheet.set_column(c, c, 90)
            worksheet.write(r,c,'Base_Trades_3')
            r+=1
            worksheet.write(r,c,base_trades_3+".trt")
            r+=1
            worksheet.write(r,c,'')
            for linha in comments_3:
                r+=1
                worksheet.write(r,c,linha.replace('## ',''))


        # print about spreadsheet
        worksheet = workbook.add_worksheet('about')
        version_txt = version_txt.splitlines()
        r=-1
        for linha in version_txt:
            r+=1
            worksheet.write(r,0,linha)
      
        try:
            writer.save()
            # writer.close()
        except:
            print('Arquivo aberto/bloqueado -> ' + filename + '\n')
            sys.exit()

#---------------------------------------------------------------------------------------------------------------

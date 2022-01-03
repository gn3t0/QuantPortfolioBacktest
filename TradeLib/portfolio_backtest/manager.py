version = 1.0

import os
import pandas as pd
import numpy as np
from datetime import datetime
import time
import multiprocessing
import sys
import random
import xlsxwriter
import argparse
from TradeLib import tag
from TradeLib.portfolio_backtest import simulation
from itertools import takewhile
import ntpath
import itertools

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def run(input_file_version, initial_capital, trans_cost_fixed, trans_cost_percent, trans_slippage, trans_volume_max, 
            max_open_trades, pyramid_profit, pyramid_trades, daily_update, monte_carlo_iterations, 
            position_size_model, position_size_model_desc,
            folder_backtest, folder_history_data, folder_base_trades, date_start, multi_proc_batch,
            base_trades_1, trade_size_limit_1, 
            date_end=[''], randomic_start=0,trade_risk_1=[0],
            base_trades_2='', trade_risk_2=[0], trade_size_limit_2=[0], 
            base_trades_3='', trade_risk_3=[0], trade_size_limit_3=[0], 
            portfolio_heat=[0],risk_round=[False], 
            shuffle_input=False, simulation_overwrite=True, cdi=True, benchmark=['']):

    multiprocessing.freeze_support()

    start_time = time.time()

    version_txt = input_file_version.replace(os.getcwd()+'\\','')
    version_txt+='\n' + os.path.basename(__file__) + ' = ' +  str(version)
    version_txt+=simulation.version_txt
    version_txt+='\ntag = ' + str(tag.version)
    print(version_txt + '\n')

    base_trades_1_list=[]
    base_trades_2_list=[]
    base_trades_3_list=[]
    
    if base_trades_1 =='':
        base_trades_1_list=['']
    else:
        if base_trades_1.find(".txt")>=0:
            if os.path.exists(base_trades_1):
                try:
                    df_enf = pd.read_csv(base_trades_1, comment='#', header = None)
                    for index, row in df_enf.iterrows():
                        if not os.path.exists(row[0]):
                            row[0]=path_leaf(row[0])
                            if row[0].find(".trt") <0 :row[0]+='.trt'
                            if os.path.exists (folder_base_trades + "/" + row[0]):
                                trt = folder_base_trades + "/" + row[0]
                            else:
                                print(row[0] + ' -> not found')
                                continue                         
                        else:        
                            trt = row[0].replace(os.getcwd()+"/","")
                            trt = row[0].replace(os.getcwd()+"\\","")

                        trt = trt.replace(".trt","")
                        base_trades_1_list.append(trt)
                except:
                    print(base_trades_1 + ' -> empty')
                    base_trades_1_list=['']
            else:
                print(base_trades_1 + ' -> not found')
                base_trades_1_list=['']
        else:
        	print('base_trades1 -> arquivo inválido')
        	base_trades_1_list=['']
    

    if base_trades_2 =='':
        base_trades_2_list=['']
    else:
        if base_trades_2.find(".txt")>=0:
            if os.path.exists(base_trades_2):
                try:
                    df_enf = pd.read_csv(base_trades_2, comment='#', header = None)
                    for index, row in df_enf.iterrows():
                        if not os.path.exists(row[0]):
                            row[0]=path_leaf(row[0])
                            if row[0].find(".trt") <0 :row[0]+='.trt'
                            if os.path.exists (folder_base_trades + "/" + row[0]):
                                trt = folder_base_trades + "/" + row[0]
                            else:
                                print(row[0] + ' -> not found')
                                continue                         
                        else:        
                            trt = row[0].replace(os.getcwd()+"/","")
                            trt = row[0].replace(os.getcwd()+"\\","")

                        trt = trt.replace(".trt","")
                        base_trades_2_list.append(trt)
                except:
                    print(base_trades_2 + ' -> empty')
                    base_trades_2_list=['']
            else:
                print(base_trades_2 + ' -> not found')
                base_trades_2_list=['']
        else:
            print('base_trades_2 -> arquivo inválido')
            base_trades_2_list=['']
        

    if base_trades_3 =='':
        base_trades_3_list=['']
    else:
        if base_trades_3.find(".txt")>=0:
            if os.path.exists(base_trades_3):
                try:
                    df_enf = pd.read_csv(base_trades_3, comment='#', header = None)
                    for index, row in df_enf.iterrows():
                        if not os.path.exists(row[0]):
                            row[0]=path_leaf(row[0])
                            if row[0].find(".trt") <0 :row[0]+='.trt'
                            if os.path.exists (folder_base_trades + "/" + row[0]):
                                trt = folder_base_trades + "/" + row[0]
                            else:
                                print(row[0] + ' -> not found')
                                continue                         
                        else:        
                            trt = row[0].replace(os.getcwd()+"/","")
                            trt = row[0].replace(os.getcwd()+"\\","")

                        trt = trt.replace(".trt","")
                        base_trades_3_list.append(trt)
                except:
                    print(base_trades_3 + ' -> empty')
                    base_trades_3_list=['']
            else:
                print(base_trades_3 + ' -> not found')
                base_trades_3_list=['']
        else:
            print('base_trades_3 -> arquivo inválido')
            base_trades_3_list=['']

    param_list = [date_start, date_end, initial_capital, trans_cost_fixed, trans_cost_percent, trans_slippage,
                    trans_volume_max, max_open_trades, pyramid_profit, pyramid_trades, daily_update, monte_carlo_iterations,
                    base_trades_1_list, base_trades_2_list, base_trades_3_list,
                    trade_risk_1, trade_size_limit_1,
                    trade_risk_2, trade_size_limit_2,
                    trade_risk_3, trade_size_limit_3,
                    portfolio_heat, risk_round, benchmark]

    param_list = [list(item) if type(item) is range else item for item in param_list]
    param_list = [item.tolist() if type(item) is np.ndarray else item for item in param_list]
    param_list = [[item] if type(item) is not list else item for item in param_list]

    prod_param_list = list(itertools.product(*param_list))

    if shuffle_input==True: random.shuffle(prod_param_list)

    for index, lista in enumerate(prod_param_list):

        date_start = lista[0]
        if date_start !='': 
            date_start = datetime.strptime(date_start, '%Y-%m-%d')
        date_end = lista[1]
        if date_end !='': 
            date_end = datetime.strptime(date_end, '%Y-%m-%d')
        initial_capital = lista[2]
        trans_cost_fixed = lista[3]
        trans_cost_percent = lista[4]
        trans_slippage = lista[5]
        trans_volume_max = lista[6]
        max_open_trades = lista[7]
        pyramid_profit = lista[8]
        pyramid_trades=lista[9]
        daily_update=lista[10]
        monte_carlo_iterations=lista[11]
        base_trades_1=lista[12]
        base_trades_2=lista[13]
        base_trades_3=lista[14]
        trade_risk_1=lista[15]
        trade_size_limit_1=lista[16]
        trade_risk_2=lista[17]
        trade_size_limit_2=lista[18]
        trade_risk_3=lista[19]
        trade_size_limit_3=lista[20]
        portfolio_heat=lista[21]
        risk_round=lista[22]
        benchmark=lista[23]

        if base_trades_1!='':
            tag1 = tag.get_tag(base_trades_1+".trt")
            if tag1==0 : 
                tag1=tag.tag_trt(base_trades_1+".trt")
                if tag1==0:
                    print('\n' + str(index+1) + '/' + str(len(prod_param_list)) + '  base_trades_1 | ' + base_trades_1 + ' -> vazio')
                    continue

        if base_trades_2!='':
            tag2 = tag.get_tag(base_trades_2+".trt")
            if tag2==0 : 
                tag2=tag.tag_trt(base_trades_2+".trt")
                if tag2==0:
                    print('\n' + str(index+1) + '/' + str(len(prod_param_list)) + '  base_trades_2 | ' + base_trades_2 + ' -> vazio')
                    continue

        if base_trades_3!='':
            tag3 = tag.get_tag(base_trades_3+".trt")
            if tag3==0 :
                tag3=tag.tag_trt(base_trades_3+".trt")
                if tag3==0:
                    print('\n' + str(index+1) + '/' + str(len(prod_param_list)) + '  base_trades_3 | ' + base_trades_3 + ' -> vazio')
                    continue


        if randomic_start>0 and randomic_start<=1:
            min_date_start = 99999999
            max_date_start = 00000000
            for n in ['1','2','3']:
                if eval('base_trades_'+n)!='':
                    df_bt=pd.read_csv(eval('base_trades_'+n)+".trt", delimiter=' ', comment='#',
                    names = ["Ticker","Trade_Position","Entry_Date","Exit_Date","Initial_Stop","Entry_Price","Exit_Price","Low_Entry_Price","High_Entry_Price","Low_Exit_Price","High_Exit_Price","Traded_Volume","Trade_Rank","Point_Value","Initial_Margin"])
                    min_date_start = min(min_date_start,df_bt['Entry_Date'].min())
                    max_date_start = max(max_date_start,df_bt['Entry_Date'].max()) 

            if date_start !='' : min_date_start = str(date_start.date()).replace('-','')
            if date_end !='' : 
                max_date_start = min(max_date_start,int(str(date_end.date()).replace('-','')))
                date_end = ''
            date_line = list(pd.date_range(start=datetime.strptime(str(min_date_start),'%Y%m%d'), end=datetime.strptime(str(max_date_start),'%Y%m%d')))
            date_line = [datetime(d.year, d.month, d.day) for d in date_line]
            if randomic_start<1: random.shuffle(date_line)
            date_line = date_line[:int(randomic_start*max(len(date_line),1))]   
        else:
            date_line = [date_start]


        for count, date_start in enumerate(date_line):
            
            date_start_txt='x'
            if date_start !='':
                date_start_txt = str(date_start.date()).replace('-','')

            date_end_txt='x'
            if date_end !='':
                date_end_txt = str(date_end.date()).replace('-','')

            if folder_backtest !='': filename = folder_backtest + '/'

            if monte_carlo_iterations>1:
                filename += 'MC_' 
            else:
                filename += 'SIM_'

            filename_args = ["date_start","date_end", "",
                            "initial_capital","pyramid_profit","pyramid_trades", "",
                            "daily_update","monte_carlo_iterations", "",
                            "position_size_model","portfolio_heat","risk_round","max_open_trades", "",
                            "trans_cost_fixed","trans_cost_percent","trans_slippage","trans_volume_max", ""]
            if base_trades_1!='': filename_args+=["trade_risk_1","trade_size_limit_1", "",]
            if base_trades_2!='': filename_args+=["trade_risk_2","trade_size_limit_2", "",]
            if base_trades_3!='': filename_args+=["trade_risk_3","trade_size_limit_3", "",]

            
            filename+= str(date_start_txt) + "_" + str(date_end_txt) + \
                "_" + str(initial_capital) + "_" + str(pyramid_profit)[0] + "_" + str(pyramid_trades)[0] + \
                "_" + str(daily_update)[0] + "_" + str(monte_carlo_iterations) + \
                "__" + str(position_size_model) + "_" + str(portfolio_heat) + "_" + str(risk_round)[0] + "_" + str(max_open_trades) + \
                "__" + str(trans_cost_fixed) + "_" + str(trans_cost_percent) + "_" + str(trans_slippage) + "_" + str(trans_volume_max)
            if base_trades_1!='':
                filename+= "__" + '[(' + str(tag1) + ')' + "_" + str(trade_risk_1)+ "_" + str(trade_size_limit_1) + ']'
            if base_trades_2!='':
                filename+= "__" + '[(' + str(tag2) + ')' + "_" + str(trade_risk_2)+ "_" + str(trade_size_limit_2) + ']'
            if base_trades_3!='':
                filename+= "__" + '[(' + str(tag3) + ')' + "_" + str(trade_risk_3)+ "_" + str(trade_size_limit_3) + ']'

            if monte_carlo_iterations==1:
                ord_sum=0
                for c in path_leaf(benchmark): ord_sum+=ord(c)
                filename+="_" + str(ord_sum)

            filename = filename.replace(".0_","_")
            filename = filename.replace(".","p")
            filename = filename.replace('p0_','_')
            filename = filename.replace('p0]',']')
            filename = filename.replace(",","")

            print('\n' + str(index+1) + '/' + str(len(prod_param_list)) + " | "+ str(count+1) + '/' + str(len(date_line)) + "  "+ filename + ' -> ...')

            if simulation_overwrite == False:
                if os.path.exists(filename + '.xlsx'): 
                    print('overwrite=False -> ' + str(filename + '.xlsx') + ' -> exists')
                    continue
                else:
                    workbook = xlsxwriter.Workbook(filename + '.xlsx')
                    workbook.close()

            processes = []
            lock = multiprocessing.Lock()
            simulation_list= multiprocessing.Manager().list()

            cont = 0
            for i in range(0,monte_carlo_iterations,1):
                print(i+1)

                p = multiprocessing.Process(target=simulation.run, args=(version_txt, lock, simulation_list, monte_carlo_iterations, filename, folder_history_data,
                                                                    base_trades_1, base_trades_2, base_trades_3, date_start, date_end, initial_capital*1000, 
                                                                    position_size_model, position_size_model_desc, portfolio_heat/100, risk_round, 
                                                                    trade_risk_1/100, trade_risk_2/100, trade_risk_3/100, 
                                                                    trade_size_limit_1/100, trade_size_limit_2/100, trade_size_limit_3/100, 
                                                                    trans_cost_fixed, trans_cost_percent/100, trans_slippage/100, 
                                                                    max_open_trades, pyramid_profit, pyramid_trades, trans_volume_max/100, daily_update,
                                                                    filename_args,folder_backtest,folder_base_trades, cdi, benchmark))
                processes.append(p)
                cont+=1
                p.start()
                if cont == multi_proc_batch:            
                    for process in processes:
                        process.join()
                    processes=[]
                    cont=0
            for process in processes: process.join()


            # MONTE CARLO --------------------------------------------------------------------------------------------------------------------------------------------


            if monte_carlo_iterations>1: 
                dfmc = pd.DataFrame()
                monte_carlo_columns = ['Date_start', 'Date_end','Total_Trades', 'Trades_Taken', 
                                        'Net_Profit', "Max_DDown", "Max_DDown_daily", 'Recovery_factor', 'Recovery_f_daily',
                                        'Net_Profit_%', "Max_DDown_%", "Max_DDown_%_daily", 'Recovery_factor_%', 'Recovery_f_%_daily',
                                        'Hit_rate', 'Trade_avg', 'Trade_avg_win', 'Trade_avg_loss', 'Trade_profit_max', 'Trade_loss_max']
                                        
                for i in simulation_list:
                    s = dict(zip(monte_carlo_columns,map(float,list(i.split(' ')))))
                    dfmc = pd.concat([dfmc, pd.DataFrame([s])], ignore_index=True)                              
                        
                writer = pd.ExcelWriter(filename + '.xlsx', engine='xlsxwriter')
                workbook = writer.book
                worksheet = workbook.add_worksheet('report')
                worksheet.hide_gridlines([1])

                f_money = workbook.add_format({'num_format': '$#,##0.00'})
                f_percent = workbook.add_format({'num_format': '0.00%'})
                f_double = workbook.add_format({'num_format': '0.00'})
                f_center = workbook.add_format({'align':'center'})
                f_right = workbook.add_format({'align':'right'})

                dfmc.to_excel(writer, sheet_name='simulations')
                ws_sim=workbook.get_worksheet_by_name('simulations')
                ws_sim.hide_gridlines([1])
                ws_sim.set_column('F:F', None, f_money)
                ws_sim.set_column('G:G', None, f_money)
                ws_sim.set_column('H:H', None, f_money)
                ws_sim.set_column('Q:Q', None, f_money)
                ws_sim.set_column('R:R', None, f_money)
                ws_sim.set_column('S:S', None, f_money)
                ws_sim.set_column('T:T', None, f_money)
                ws_sim.set_column('U:U', None, f_money)
                ws_sim.set_column('K:K', None, f_percent)
                ws_sim.set_column('L:L', None, f_percent)
                ws_sim.set_column('M:M', None, f_percent)
                ws_sim.set_column('N:N', None, f_percent)
                ws_sim.set_column('O:O', None, f_percent)
                ws_sim.set_column('P:P', None, f_percent)

                report_columns = [  'Position_Size_Model',
                                    'Base_Trades_1', 'Trade_risk_1', 'Trade_size_limit_1',
                                    'Base_Trades_2', 'Trade_risk_2', 'Trade_size_limit_2',
                                    'Base_Trades_3', 'Trade_risk_3', 'Trade_size_limit_3',
                                    '', 
                                    'Initial_Capital', 'Simulations', 'Pyramid_Profits', 'Pyramid_Trades', 'Daily_Update',
                                    'Portfolio_heat_max', 'Max_open_trades', 'Risk_round', 
                                    'Trans_cost_fixed', 'Trans_cost_percent', 'Trans_slippage', 'Trans_volume_max',
                                    '', 
                                    'Date_start', 'Date_end','Total Trades',
                                    '','',                                                                            
                                    'Trades_Taken', 
                                    'Net_Profit',
                                    'Max_DDown',
                                    'Max_DDown_daily',
                                    'Recovery_factor', 
                                    'Recovery_f_daily', 
                                    'Net_Profit_%', 
                                    'Max_DDown_%',  
                                    'Max_DDown_%_daily',  
                                    'Recovery_factor_%', 
                                    'Recovery_f_%_daily',
                                    'Hit_rate', 
                                    'Trade_avg',
                                    'Trade_avg_win',
                                    'Trade_avg_loss',
                                    'Trade_profit_max', 
                                    'Trade_loss_max']

                row=0
                col=0

                for r, rc in enumerate(report_columns):
                    worksheet.write(r,col,rc)
                worksheet.set_column(col, col, 20)
                worksheet.set_column(col+1, col+1, 12)
                worksheet.set_column(col+2, col+2, 12)
                worksheet.set_column(col+3, col+3, 12)
                worksheet.set_column(col+4, col+4, 12)

                worksheet.write(row,col+1,str(position_size_model_desc[position_size_model-1]))

                if base_trades_1!='':
                    row+=1
                    worksheet.write(row,col+1,path_leaf(base_trades_1))
                    row+=1
                    if position_size_model==1:
                        worksheet.write(row,col+1,trade_risk_1/100,f_percent)
                    else:
                        worksheet.write(row,col+1,'-',f_center)     
                    row+=1
                    worksheet.write(row,col+1,trade_size_limit_1/100,f_percent)
                else:
                    row+=1
                    worksheet.write(row,col+1,'-',f_center)
                    row+=1
                    worksheet.write(row,col+1,'-',f_center)
                    row+=1
                    worksheet.write(row,col+1,'-',f_center)                                                                                                                

                if base_trades_2!='':
                    row+=1
                    worksheet.write(row,col+1,path_leaf(base_trades_2))
                    row+=1
                    if position_size_model==1:
                        worksheet.write(row,col+1,trade_risk_2/100,f_percent)
                    else:
                        worksheet.write(row,col+1,'-',f_center)     
                    row+=1
                    worksheet.write(row,col+1,trade_size_limit_2/100,f_percent)
                else:
                    row+=1
                    worksheet.write(row,col+1,'-',f_center)
                    row+=1
                    worksheet.write(row,col+1,'-',f_center)
                    row+=1
                    worksheet.write(row,col+1,'-',f_center)      

                if base_trades_3!='':
                    row+=1
                    worksheet.write(row,col+1,path_leaf(base_trades_3))
                    row+=1
                    if position_size_model==1:
                        worksheet.write(row,col+1,trade_risk_3/100,f_percent)
                    else:
                        worksheet.write(row,col+1,'-',f_center)     
                    row+=1
                    worksheet.write(row,col+1,trade_size_limit_3/100,f_percent)
                else: 
                    row+=1
                    worksheet.write(row,col+1,'-',f_center)
                    row+=1
                    worksheet.write(row,col+1,'-',f_center)
                    row+=1
                    worksheet.write(row,col+1,'-',f_center)    

                row+=2
                worksheet.write(row,col+1,initial_capital*1000,f_money)
                row+=1
                worksheet.write(row,col+1,monte_carlo_iterations)
                row+=1
                worksheet.write(row,col+1,str(pyramid_profit),f_right)
                row+=1
                worksheet.write(row,col+1,str(pyramid_trades),f_right)
                row+=1
                worksheet.write(row,col+1,str(daily_update),f_right)
                row+=1
                if position_size_model==1:
                    worksheet.write(row,col+1,portfolio_heat/100, f_percent)
                else:
                    worksheet.write(row,col+1,'-',f_center)     
                row+=1
                worksheet.write(row,col+1,max_open_trades)
                row+=1
                if position_size_model==1:
                    worksheet.write(row,col+1,str(risk_round),f_right)     
                else:
                    worksheet.write(row,col+1,'-',f_center)     
                row+=1
                worksheet.write(row,col+1,trans_cost_fixed,f_money)
                row+=1                                             
                worksheet.write(row,col+1,trans_cost_percent/100,f_percent)
                row+=1
                worksheet.write(row,col+1,trans_slippage/100,f_percent)
                row+=1
                worksheet.write(row,col+1,trans_volume_max/100,f_percent)

                row+=2
                worksheet.write(row,col+1,dfmc['Date_start'].min())
                row+=1
                worksheet.write(row,col+1,dfmc['Date_end'].max())
                row+=1
                worksheet.write(row,col+1,dfmc.Total_Trades.mean())

                row+=2
                worksheet.write(row,col+1,'avg',f_center)
                worksheet.write(row,col+2,'max',f_center)
                worksheet.write(row,col+3,'min',f_center)
                worksheet.write(row,col+4,'sdev',f_center)

                row+=1
                worksheet.write(row,col+1,dfmc.Trades_Taken.mean(),f_double)
                worksheet.write(row,col+2,dfmc.Trades_Taken.max())
                worksheet.write(row,col+3,dfmc.Trades_Taken.min())
                worksheet.write(row,col+4,dfmc.Trades_Taken.std(),f_double)
                row+=1
                worksheet.write(row,col+1,dfmc.Net_Profit.mean(),f_money)
                worksheet.write(row,col+2,dfmc.Net_Profit.max(),f_money)
                worksheet.write(row,col+3,dfmc.Net_Profit.min(),f_money)
                worksheet.write(row,col+4,dfmc.Net_Profit.std(),f_money)
                row+=1
                worksheet.write(row,col+1,dfmc.Max_DDown.mean(),f_money)
                worksheet.write(row,col+2,dfmc.Max_DDown.min(),f_money)
                worksheet.write(row,col+3,dfmc.Max_DDown.max(),f_money)
                worksheet.write(row,col+4,dfmc.Max_DDown.std(),f_money)
                row+=1
                if daily_update==True:
                    worksheet.write(row,col+1,dfmc.Max_DDown_daily.mean(),f_money)
                    worksheet.write(row,col+2,dfmc.Max_DDown_daily.min(),f_money)
                    worksheet.write(row,col+3,dfmc.Max_DDown_daily.max(),f_money)
                    worksheet.write(row,col+4,dfmc.Max_DDown_daily.std(),f_money)
                else:
                    worksheet.write(row,col+1,'-',f_center)
                    worksheet.write(row,col+2,'-',f_center)
                    worksheet.write(row,col+3,'-',f_center)
                    worksheet.write(row,col+4,'-',f_center)                                                            
                row+=1
                worksheet.write(row,col+1,dfmc.Recovery_factor.mean(),f_double)
                worksheet.write(row,col+2,dfmc.Recovery_factor.max(),f_double)
                worksheet.write(row,col+3,dfmc.Recovery_factor.min(),f_double)
                worksheet.write(row,col+4,dfmc.Recovery_factor.std(),f_double)
                row+=1
                if daily_update==True:
                    worksheet.write(row,col+1,dfmc.Recovery_f_daily.mean(),f_double)
                    worksheet.write(row,col+2,dfmc.Recovery_f_daily.max(),f_double)
                    worksheet.write(row,col+3,dfmc.Recovery_f_daily.min(),f_double)
                    worksheet.write(row,col+4,dfmc.Recovery_f_daily.std(),f_double)
                else:
                    worksheet.write(row,col+1,"-",f_center)
                    worksheet.write(row,col+2,"-",f_center)
                    worksheet.write(row,col+3,"-",f_center)
                    worksheet.write(row,col+4,"-",f_center)
                row+=1
                worksheet.write(row,col+1,dfmc['Net_Profit_%'].mean(),f_percent)
                worksheet.write(row,col+2,dfmc['Net_Profit_%'].max(),f_percent)
                worksheet.write(row,col+3,dfmc['Net_Profit_%'].min(),f_percent)
                worksheet.write(row,col+4,dfmc['Net_Profit_%'].std(),f_percent)
                row+=1
                worksheet.write(row,col+1,dfmc['Max_DDown_%'].mean(),f_percent)
                worksheet.write(row,col+2,dfmc['Max_DDown_%'].min(),f_percent)
                worksheet.write(row,col+3,dfmc['Max_DDown_%'].max(),f_percent)
                worksheet.write(row,col+4,dfmc['Max_DDown_%'].std(),f_percent)
                row+=1
                if daily_update==True:
                    worksheet.write(row,col+1,dfmc['Max_DDown_%_daily'].mean(),f_percent)
                    worksheet.write(row,col+2,dfmc['Max_DDown_%_daily'].min(),f_percent)
                    worksheet.write(row,col+3,dfmc['Max_DDown_%_daily'].max(),f_percent)
                    worksheet.write(row,col+4,dfmc['Max_DDown_%_daily'].std(),f_percent)
                else:
                    worksheet.write(row,col+1,'-',f_center)
                    worksheet.write(row,col+2,'-',f_center)
                    worksheet.write(row,col+3,'-',f_center)
                    worksheet.write(row,col+4,'-',f_center)                                                            
                row+=1
                worksheet.write(row,col+1,dfmc['Recovery_factor_%'].mean(),f_double)
                worksheet.write(row,col+2,dfmc['Recovery_factor_%'].max(),f_double)
                worksheet.write(row,col+3,dfmc['Recovery_factor_%'].min(),f_double)
                worksheet.write(row,col+4,dfmc['Recovery_factor_%'].std(),f_double)
                row+=1
                if daily_update==True:
                    worksheet.write(row,col+1,dfmc['Recovery_f_%_daily'].mean(),f_double)
                    worksheet.write(row,col+2,dfmc['Recovery_f_%_daily'].max(),f_double)
                    worksheet.write(row,col+3,dfmc['Recovery_f_%_daily'].min(),f_double)
                    worksheet.write(row,col+4,dfmc['Recovery_f_%_daily'].std(),f_double)
                else:
                    worksheet.write(row,col+1,"-",f_center)
                    worksheet.write(row,col+2,"-",f_center)
                    worksheet.write(row,col+3,"-",f_center)
                    worksheet.write(row,col+4,"-",f_center)
                row+=1
                worksheet.write(row,col+1,dfmc.Hit_rate.mean(),f_percent)
                worksheet.write(row,col+2,dfmc.Hit_rate.max(),f_percent)
                worksheet.write(row,col+3,dfmc.Hit_rate.min(),f_percent)
                worksheet.write(row,col+4,dfmc.Hit_rate.std(),f_percent)
                row+=1
                worksheet.write(row,col+1,dfmc.Trade_avg.mean(),f_money)
                worksheet.write(row,col+2,dfmc.Trade_avg.max(),f_money)
                worksheet.write(row,col+3,dfmc.Trade_avg.min(),f_money)
                worksheet.write(row,col+4,dfmc.Trade_avg.std(),f_money)
                row+=1
                worksheet.write(row,col+1,dfmc.Trade_avg_win.mean(),f_money)
                worksheet.write(row,col+2,dfmc.Trade_avg_win.max(),f_money)
                worksheet.write(row,col+3,dfmc.Trade_avg_win.min(),f_money)
                worksheet.write(row,col+4,dfmc.Trade_avg_win.std(),f_money)
                row+=1
                worksheet.write(row,col+1,dfmc.Trade_avg_loss.mean(),f_money)
                worksheet.write(row,col+2,dfmc.Trade_avg_loss.min(),f_money)
                worksheet.write(row,col+3,dfmc.Trade_avg_loss.max(),f_money)
                worksheet.write(row,col+4,dfmc.Trade_avg_loss.std(),f_money)
                row+=1
                worksheet.write(row,col+1,dfmc.Trade_profit_max.mean(),f_money)
                worksheet.write(row,col+2,dfmc.Trade_profit_max.max(),f_money)
                worksheet.write(row,col+3,dfmc.Trade_profit_max.min(),f_money)
                worksheet.write(row,col+4,dfmc.Trade_profit_max.std(),f_money)
                row+=1
                worksheet.write(row,col+1,dfmc.Trade_loss_max.mean(),f_money)
                worksheet.write(row,col+2,dfmc.Trade_loss_max.min(),f_money)
                worksheet.write(row,col+3,dfmc.Trade_loss_max.max(),f_money)
                worksheet.write(row,col+4,dfmc.Trade_loss_max.std(),f_money)


                hist_Net_Profit = pd.DataFrame(dfmc['Net_Profit'].value_counts(bins=60, ascending=True, sort=False))
                hist_Net_Profit.to_excel(writer, sheet_name='simulations', startcol=23)

                hist_Net_Profit_p = pd.DataFrame(dfmc['Net_Profit_%'].value_counts(bins=60, ascending=True, sort=False))
                hist_Net_Profit_p.to_excel(writer, sheet_name='simulations', startcol=26)

                hist_Drawdown = pd.DataFrame(dfmc['Max_DDown'].value_counts(bins=60, ascending=True, sort=False))
                hist_Drawdown.to_excel(writer, sheet_name='simulations', startcol=29)

                hist_Drawdown_p = pd.DataFrame(dfmc['Max_DDown_%'].value_counts(bins=60, ascending=True, sort=False))
                hist_Drawdown_p.to_excel(writer, sheet_name='simulations', startcol=32)

                chart = workbook.add_chart({'type': 'column'})
                chart.add_series({'values': '=simulations!Y2:Y61', 'categories':'=simulations!X2:X61', 'name': 'Net_Profit'})
                chart.set_legend({'none': True})
                chart.set_x_axis({'visible': False})
                worksheet.insert_chart('G10', chart)

                chart = workbook.add_chart({'type': 'column'})
                chart.add_series({'values': '=simulations!AB2:AB61', 'categories':'=simulations!AA2:AA61', 'name': 'Net_Profit_%'})
                chart.set_legend({'none': True})
                chart.set_x_axis({'visible': False})
                worksheet.insert_chart('G25', chart)

                chart = workbook.add_chart({'type': 'column'})
                chart.add_series({'values': '=simulations!AE2:AE61', 'categories':'=simulations!AD2:AD61', 'name': 'Max_Drawdown'})
                chart.set_legend({'none': True})
                chart.set_x_axis({'visible': False})
                worksheet.insert_chart('O10', chart)

                chart = workbook.add_chart({'type': 'column'})
                chart.add_series({'values': '=simulations!AH2:AH61', 'categories':'=simulations!AG2:AG61', 'name': 'Max_Drawdown_%'})
                chart.set_legend({'none': True})
                chart.set_x_axis({'visible': False})
                worksheet.insert_chart('O25', chart)

                if daily_update==True:
                    hist_Drawdown = pd.DataFrame(dfmc['Max_DDown_daily'].value_counts(bins=60, ascending=True, sort=False))
                    hist_Drawdown.to_excel(writer, sheet_name='simulations', startcol=35)

                    hist_Drawdown_p = pd.DataFrame(dfmc['Max_DDown_%_daily'].value_counts(bins=60, ascending=True, sort=False))
                    hist_Drawdown_p.to_excel(writer, sheet_name='simulations', startcol=38)

                    chart = workbook.add_chart({'type': 'column'})
                    chart.add_series({'values': '=simulations!AK2:AK61', 'categories':'=simulations!AJ2:AJ61', 'name': 'Max_Drawdown_daily'})
                    chart.set_legend({'none': True})
                    chart.set_x_axis({'visible': False})
                    worksheet.insert_chart('G40', chart)

                    chart = workbook.add_chart({'type': 'column'})
                    chart.add_series({'values': '=simulations!AN2:AN61', 'categories':'=simulations!AM2:AM61', 'name': 'Max_Drawdown_%_daily'})
                    chart.set_legend({'none': True})
                    chart.set_x_axis({'visible': False})
                    worksheet.insert_chart('O40', chart)

                # print SIM filename input parameters
                r=0
                c=22
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
                        z+= ' (' + variable + "= " + str(eval(variable)) + ')'


                # print BaseTrades1 input parameters
                if base_trades_1!='':
                    with open(base_trades_1+".trt", 'r') as fobj:
                        list(takewhile(lambda s: not s.startswith("##"), fobj))
                        comments_1 = list(takewhile(lambda s: s.startswith('##'), fobj))
                    fobj.close()
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
                    with open(base_trades_2+".trt", 'r') as fobj:
                        list(takewhile(lambda s: not s.startswith("##"), fobj))
                        comments_2 = list(takewhile(lambda s: s.startswith('##'), fobj))
                    fobj.close()
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
                        linha = linha.replace('## ','')
                        worksheet.write(r,c,linha.replace('\n',''))

                # print BaseTrades1 input parameters
                if base_trades_3!='':
                    with open(base_trades_3+".trt", 'r') as fobj:
                        list(takewhile(lambda s: not s.startswith("##"), fobj))
                        comments_3 = list(takewhile(lambda s: s.startswith('##'), fobj))
                    fobj.close()
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
                        linha = linha.replace('## ','')
                        worksheet.write(r,c,linha.replace('\n',''))


                # print about spreadsheet
                worksheet = workbook.add_worksheet('about')
                about = version_txt.splitlines()
                r=-1
                for linha in about:
                    r+=1
                    worksheet.write(r,0,linha)

                try:
                    writer.save()
                    # writer.close()
                except:
                    print('Arquivo aberto/bloqueado -> ' + filename + '\n')
                                                                

    print("\nTOTAL %.2f seconds " % (time.time() - start_time))

    # timer=0
    # hora = time.time()                
    # timer = timer+(time.time()-hora)
    # print (timer)

#-----------------------------------------------------------------------------------------------------------------------

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

#-----------------------------------------------------------------------------------------------------------------------
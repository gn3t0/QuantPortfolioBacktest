version = 1.0

import multiprocessing
import numpy as np
from datetime import datetime
import time
import sys
import os
from TradeLib import calclib as calc
import pandas as pd
from random import shuffle
import itertools
import inspect
import importlib

def run(input_file_version, multi_proc_batch=4, folder_history_data='BASE_HISTORICA_swing', name='TS', date_start='', date_end='', tickers_selection=[], 
        slippage=0, folder_base_trades='BASE_TRADES', tukey=1, randomic=1, plot=False, plots=[], subplots=[], plot_trade_enforce=True, real_time=False, 
        initial_stop=0, breakeven_level=0, 
        stoploss_1=0, stoploss_level_1=0, stoploss_2=0, stoploss_level_2=0, stoploss_3=0, stoploss_level_3=0,
        max_duration=0, gain=0, compensate_entry_gaps=True, value_open_trades_on_stop=False, 
        filter_scenario_1=1, filter_scenario_2=1, filter_scenario_3=1, filter_scenario_4=0, 
        filter_ohlc_1=1, filter_ohlc_2=1, filter_ohlc_3=1, filter_ohlc_4=0,         
        shuffle_input=False, base_trades_overwrite=True, strategy='TradeLib.base_trades.strategy.swing_pyalgotrade',
        stoploss_order_type=['M'], gain_order_type=['M'], 
        entry_side='L', entry_order_type=['M'], entry_order_price=[0],       
        filter_volume_qtde=[0], filter_volume_qtde_operator=['AND'], filter_volume_qtde_ranking=[0], 
        filter_volume_neg=[0], filter_volume_neg_operator=['AND'],filter_volume_neg_ranking=[0], 
        filter_volume_fin=[0], filter_volume_fin_operator=['AND'], filter_volume_fin_ranking=[0],
        filter_volume_lock_ranking=[]):

    multiprocessing.freeze_support()

    strategy = importlib.import_module(strategy)

    start_time = time.time()

    version_txt = input_file_version.replace(os.getcwd()+'\\','')
    version_txt+='\n# ' + os.path.basename(__file__) + ' = ' +  str(version)
    version_txt+=strategy.version_txt
    version_txt+='\n# calclib = ' + str(calc.version)
    print(version_txt + '\n')

    if not os.path.exists(folder_history_data):
        print("Base Histórica (folder_history_data) não encontrada!")
        input()
        sys.exit()

    if tickers_selection==['']: tickers_selection=[]
    if date_start==[]: date_start=['']
    if date_end==[]: date_end=['']
    if plots==['']: plots=[]
    if subplots==['']: subplots=[]

    if len(tickers_selection)>0:
        tickers = tickers_selection
        for ticker in tickers:
            ticker_path = folder_history_data+"/"+ticker
            if not os.path.exists(ticker_path+".txt"):
                print(ticker_path + " -> not found !")
                tickers.remove(ticker)
        if not len(tickers)>0:
            print("tickers_selection -> inválida !")
            input()
            sys.exit()
    elif plot==True:
        print('-> Só é permitido plot para uma seleção de tickers !')
        input()
        sys.exit()  
    else:
        tickers =os.listdir(folder_history_data)
        tickers = [ticker.replace(".txt","") for ticker in tickers if ticker.endswith(".txt")]
    
   
    ibov_path = folder_history_data + "/IBOV.txt"
    if not os.path.exists(ibov_path):
        print(ibov_path + " -> not found !")
        input()
        sys.exit()
    df_ibov = pd.read_csv(ibov_path, index_col="Date")
    hoje_ibov = datetime.strptime(df_ibov.tail(1).index.item(), '%Y-%m-%d').date()


    if len(filter_volume_lock_ranking) > 0:
        filter_volume_fin_ranking = filter_volume_lock_ranking
        filter_volume_qtde_ranking = [0]
        filter_volume_neg_ranking = [0]


    param_list_keys = ['date_start', 'date_end', 
        'slippage', 'randomic',
        'initial_stop', 'breakeven_level', 
        'stoploss_1', 'stoploss_level_1', 'stoploss_2', 'stoploss_level_2', 'stoploss_3', 'stoploss_level_3',
        'max_duration', 'gain', 'compensate_entry_gaps', 'value_open_trades_on_stop', 
        'filter_scenario_1', 'filter_scenario_2' , 'filter_scenario_3', 'filter_scenario_4', 
        'filter_ohlc_1', 'filter_ohlc_2', 'filter_ohlc_3' , 'filter_ohlc_4' ,         
        'stoploss_order_type', 'gain_order_type', 
        'entry_order_type', 'entry_order_price',       
        'filter_volume_qtde', 'filter_volume_qtde_operator', 'filter_volume_qtde_ranking', 
        'filter_volume_neg', 'filter_volume_neg_operator','filter_volume_neg_ranking', 
        'filter_volume_fin', 'filter_volume_fin_operator', 'filter_volume_fin_ranking']

    param_list=[]
    for k in param_list_keys: param_list.append(eval(k))
    
    param_list = [list(item) if type(item) is range else item for item in param_list]
    param_list = [item.tolist() if type(item) is np.ndarray else item for item in param_list]
    param_list = [[item] if type(item) is not list else item for item in param_list]

    prod_param_list = list(itertools.product(*param_list))

    if shuffle_input==True: shuffle(prod_param_list)

    for comb in prod_param_list:

        p={}
        for i, k in enumerate(param_list_keys): p[k]=comb[i]

        if p['date_start']!='': p['date_start'] = datetime.strptime(p['date_start'], '%Y-%m-%d').date()
        if p['date_end']!='': p['date_end'] = datetime.strptime(p['date_end'], '%Y-%m-%d').date()
        
        if len(filter_volume_lock_ranking)>0:
            p['filter_volume_qtde_ranking']=p['filter_volume_fin_ranking']
            p['filter_volume_neg_ranking']=p['filter_volume_fin_ranking']

        if p['entry_order_type']=='M' or p['entry_order_type']=='C': p['entry_order_price']=0


        # Nome da base de trades a ser gravada --------------------------------------------------------------------------------------------------

        base_trades_name=['date_start', 'date_end', "",
                          'name', 'slippage','tukey', 'randomic', "",
                          'initial_stop','breakeven_level','max_duration',  "",
                          'gain', 'gain_order_type', "", 
                          'stoploss_1', 'stoploss_level_1', "",
                          'stoploss_2', 'stoploss_level_2', "",
                          'stoploss_3', 'stoploss_level_3', "",
                          'stoploss_order_type', "", 
                          'compensate_entry_gaps','value_open_trades_on_stop', "",
                          'entry_order_type', 'entry_order_price', "",
                          'filter_scenario_1', 'filter_scenario_2' , 'filter_scenario_3', 'filter_scenario_4', "",
                          'filter_ohlc_1', 'filter_ohlc_2', 'filter_ohlc_3' , 'filter_ohlc_4', "",         
                          'filter_volume_qtde', 'filter_volume_qtde_operator', 'filter_volume_qtde_ranking', "",
                          'filter_volume_neg', 'filter_volume_neg_operator','filter_volume_neg_ranking', "",
                          'filter_volume_fin', 'filter_volume_fin_operator', 'filter_volume_fin_ranking']
                         

        base_trades_name_txt = '##'
        # base_trades_name_txt+= ' (' + 'name' + "= " + str(name) + ')'
        for variable in base_trades_name:
            if variable=="": 
                base_trades_name_txt+= "\n##"
            else:
                base_trades_name_txt+= ' (' + variable + "= " + str(p.get(variable,eval(variable))) + ')'

        base_trades = name + "_" + str(p['slippage']) + "_" + str(tukey) + "_" + str(p['randomic']) + \
            "__" + str(p['initial_stop']) + "_" + str(p['breakeven_level']) + "_" + str(p['max_duration']) + \
            "__" + str(p['gain']) + "_" + str(p['gain_order_type']) + \
            "__" + str(p['stoploss_1']) + "_" + str(p['stoploss_level_1']) + \
            "__" + str(p['stoploss_2']) + "_" + str(p['stoploss_level_2']) + \
            "__" + str(p['stoploss_3']) + "_" + str(p['stoploss_level_3']) + \
            "__" + str(p['stoploss_order_type']) + \
            "__" + str(p['compensate_entry_gaps'])[0] + "_"+ str(p['value_open_trades_on_stop'])[0] + \
            "__" + str(p['entry_order_type'])+ "_" + str(p['entry_order_price']) + \
            "__" + str(p['filter_scenario_1'])+ "_" + str(p['filter_scenario_2'])+ "_" + str(p['filter_scenario_3']) + "_" + str(p['filter_scenario_4']) + \
            "__" + str(p['filter_ohlc_1']) + "_" + str(p['filter_ohlc_2'])+ "_" + str(p['filter_ohlc_3']) + "_" + str(p['filter_ohlc_4']) + \
            "__" + str(p['filter_volume_qtde'])+ "_" + str(p['filter_volume_qtde_operator'])+ "_" + str(p['filter_volume_qtde_ranking']) + \
            "__" + str(p['filter_volume_neg'])+ "_" + str(p['filter_volume_neg_operator'])+ "_" + str(p['filter_volume_neg_ranking']) + \
            "__" + str(p['filter_volume_fin'])+ "_" + str(p['filter_volume_fin_operator'])+ "_" + str(p['filter_volume_fin_ranking']) 


        base_trades = base_trades.replace(".0_","_")
        base_trades = base_trades.replace(".0]","]")
        base_trades = base_trades.replace(".","p")
        base_trades = base_trades + ".trt"
        base_trades = base_trades.replace("p0.",".")
        base_trades = base_trades.replace(",","")

        print(str(prod_param_list.index(comb)+1) + '/' + str(len(prod_param_list)) + "  " + base_trades + ' -> ...')


        # Validar parametos da estrategia --------------------------------------------------------------------------------------------------

        erro = strategy.validate_parameters(p['stoploss_level_1'],p['stoploss_level_2'],p['stoploss_level_3']) 
        if erro != '' : 
            print(erro)
            print(base_trades + " -> NÃO gravado !\n")
            continue

        # --------------------------------------------------------------------------------------------------------------------------------------

        plot_title = base_trades.replace(".trt","")

        if os.path.exists(folder_base_trades):
            base_trades = folder_base_trades + "/" + base_trades
            base_trades_temp = base_trades.replace(".trt",".txt")

        if base_trades_overwrite == False and plot==False and real_time==False:
            if os.path.exists(base_trades) or os.path.exists(base_trades_temp): 
                if os.path.exists(base_trades): print('overwrite=False -> ' + str(base_trades) + ' -> exists')
                if os.path.exists(base_trades_temp): print('overwrite=False -> ' + str(base_trades) + ' -> building...')
                continue
            else:
                txt_file = open(base_trades_temp, "w") 
                txt_file.close()

        cont = 0
        processes = []
        trades_trt= multiprocessing.Manager().list()
        lock = multiprocessing.Lock()


        insp_args = inspect.getfullargspec(strategy.Strategy).args
        local_keys = list(locals().keys())
        keys = [arg for arg in insp_args if arg in local_keys]
        kwargs={}
        for k in keys: kwargs[k]=eval(k)
        keys = [arg for arg in p if arg in kwargs]
        for k in keys: kwargs[k]=p[k]


        for ticker in tickers:
            if plot==False and ticker=="IBOV": continue
            txt = folder_history_data+"/"+ticker+".txt"
            kwargs['trade_enforce']=False
            kwargs['txt']=txt
            kwargs['ticker']=ticker
            print(ticker)                            
            
            p = multiprocessing.Process(target=strategy.run, kwargs=kwargs)

            processes.append(p)
            cont+=1
            p.start()
            if cont == multi_proc_batch:            
                for process in processes:
                    process.join()
                processes=[]
                cont=0

        for process in processes:
            process.join()


        # Trades Enforce
        if real_time==True or (plot==True and plot_trade_enforce==True):
            if os.path.exists('trades_enforce.txt'):
                try:
                    df_enf = pd.read_csv('trades_enforce.txt', comment='#')
                    for index, row in df_enf.iterrows():
                        ticker = row[0]
                        if ticker in tickers:
                            txt = folder_history_data+"/"+ticker+".txt"
                            date_start = datetime.strptime(row[1], '%Y-%m-%d').date()
                            if len(row)>2:
                                if float(row[2])>0: initial_stop = row[2]
                            print('trade_enforce: ' + str(ticker) + " " + str(date_start))

                            kwargs['trade_enforce']=True
                            kwargs['txt']=txt
                            kwargs['ticker']=ticker
                            kwargs['date_start']=date_start
                            kwargs['initial_stop']=initial_stop
                            
                            p = multiprocessing.Process(target=strategy.run, kwargs=kwargs)
                                                                                                
                            q.start()
                            q.join()

                except:
                    print('trades_enforce.txt -> ERRO')


        if len(trades_trt)>0:

            if real_time==True:

                with open(name + ".txt", "w") as txt_file:
                    for line in trades_trt:
                        txt_file.write(line + "\n") 
                txt_file.close
                print(name + ".txt" + " -> gravado !")

            elif real_time==False and plot==False: # Base TradeSim

                # (Opcional) tukey_filter para excluir trades outliers ----------------------------------------------------------------------------------------

                if tukey>0:
                    texto = calc.tukey_filter(trades_trt, tukey)
                else:
                    texto = [v[1] for v in trades_trt]

                # --------------------------------------------------------------------------------------------------------------------------------------

                with open(base_trades, "w") as txt_file:
                    txt_file.write(version_txt+ "\n") 
                    txt_file.write("## \n") 
                    txt_file.write("## " + base_trades.replace(folder_base_trades + "/" ,'') + "\n") 
                    txt_file.write("## \n") 
                    txt_file.write(base_trades_name_txt + "\n")
                    txt_file.write("# \n") 
                    txt_file.write("# <ticker> <operacao> <data_in> <data_out> <stop_inicial> <preco_entrada> <preco_saida> 0 0 0 0 <volume_financeiro> 0 0 0 \n") 
                    for line in texto:
                        txt_file.write(line + "\n") 
                txt_file.close()

                print(base_trades + " -> gravado !\n")

        else:
            print('qtde_trades=0 -> ' + str(base_trades) + ' -> não gravado !\n')

        try:
            os.remove(base_trades_temp)
        except: pass


    print("%.2f seconds\n" % (time.time() - start_time))

#-----------------------------------------------------------------------------------------------------------------------



version = 1.0

import inspect
from TradeLib.base_trades import manager
from TradeLib.calclib import my_arange 
# UTILIZAR "my_arange" AO INVÉS DE "range" PARA VALORES NÃO INTEIROS

if __name__ == '__main__':

### GENERAL -----------------------------------------------------------------------------------------------------

    # shuffle_input=True
    # base_trades_overwrite=False
    # strategy = 'TradeLib.base_trades.strategy.swing_pyalgotrade'

    multi_proc_batch = 4
    folder_history_data ='BASE_HISTORICA_swing'

    name = 'TREND'   
    date_start = [''] # 'yyyy-mm-dd'
    date_end = ['']   # ''-> até o final do historico disponivel
    tickers_selection = []   # ['PETR4','GGBR4','ITUB4', etc...]


### POSSIBLE OUTCOMES -----------------------------------------------------------------------------------------------

    ### (1) BASE TRADES -> DEFAULT 

    slippage = [0.00]    # 1 -> 1%
    folder_base_trades ='BASE_TRADES'
    tukey = 1  # 0(OFF); 1(1-99); 2(1-99/exclude tickers)
    randomic = [1] # 1 -> desabilita  |  de 0 (zero) a 1

    ### (2) PLOT CHARTS 
    
    plot = False
    plots = ['stop_loss_1']  # -> Na mesma janela do preço 
    subplots = ['ATR']  # -> Em janelas separadas do preço 
    plot_trade_enforce = True

    ### (3) REAL TIME TRADES 

    real_time = False
    

### EXIT TRADES PARAMETERS | TradeLib/exit.py ----------------------------------------------

    initial_stop = [2]   # 0 -> desabilita    
    
    # breakeven_level = [0.0]   # 0 -> desabilita 

    # max_duration = [0]   # 0 -> desabilita    

    # gain = [0]   # 0 -> desabilita    
    # gain_order_type = ['M']   # 'M'(Market); 'L'(Limit); 'C'(Close)

    # ------------------------------------------------------

    stoploss_1 = [4.5]         # 0 -> desabilita    
    # stoploss_level_1 = [0]   

    # stoploss_2 = [0]  
    # stoploss_level_2 = [0]

    # stoploss_3 = [0] 
    # stoploss_level_3 = [0]

    # stoploss_order_type = ['M'] # 'M'(Market); 'S'(Stop); 'C'(Close)

    # ------------------------------------------------------

    # compensate_entry_gaps = [True]

    # value_open_trades_on_stop = [False]


### ENTRY TRADES PARAMETERS | TradeLib/entry.py ----------------------------------------------
    
    # entry_side = 'L'   # 'L'(Long); 'S'(Short)

    # entry_order_type = ['M']    # 'M'(Market); 'L'(Limit); 'S'(Stop); 'C'(Close)
    # entry_order_price = [0] 

    # TradeLib/volumes.py ------------------------------------

    # filter_volume_qtde = [100]   # volume_qtde * 1000
    # filter_volume_qtde_operator = ['AND']   # 'AND' | 'OR'
    # filter_volume_qtde_ranking = [0]   # 0 -> desabilita

    filter_volume_neg = [0.5]   # volume_neg * 1000
    # filter_volume_neg_operator = ['AND']
    # filter_volume_neg_ranking = [0] 

    # filter_volume_fin = [0]   # volume_fin * 1000
    # filter_volume_fin_operator = ['AND']
    # filter_volume_fin_ranking = [0]

    # filter_volume_lock_ranking = []   # [] -> desabilita

    # -------------------------------------------------------

    ### filter_1 AND filter_2 AND filter_3 AND filter_4 | TradeLib/filter/scenario.py

    filter_scenario_1 = [2]
    filter_scenario_2 = [1]
    filter_scenario_3 = [1]
    filter_scenario_4 = [1]

    ### filter_1 AND filter_2 AND (filter_3 OR filter_4) | TradeLib/filter/ohlc.py

    filter_ohlc_1 = [1]
    filter_ohlc_2 = [1]
    filter_ohlc_3 = [1]
    filter_ohlc_4 = [0]


##################################################################################################################################################    

    args = inspect.getfullargspec(manager.run).args
    input_file_version="# " + __file__  + ' = ' + str(version)
    keys = list(locals().keys())
    kwargs = dict((arg, eval(arg)) for arg in args if arg in keys)

    manager.run(**kwargs)


##################################################################################################################################################    
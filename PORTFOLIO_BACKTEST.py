version = 1.0

import inspect
from TradeLib.portfolio_backtest import manager
from TradeLib.portfolio_backtest.manager import my_arange
# UTILIZAR "my_arange" AO INVÉS DE "range" PARA VALORES NÃO INTEIROS

if __name__ == '__main__':


    # shuffle_input = True
    # simulation_overwrite =False
    multi_proc_batch = 4

    folder_backtest='PORTFOLIO_BACKTEST'
    folder_history_data ='BASE_HISTORICA_swing'
    folder_base_trades ='BASE_TRADES'
    date_start=['']   # yyyy-mm-dd
    # date_end=['']
    # randomic_start=0.00  # de 0 (zero) a 1  |  0-> desabilita  |  1-> simulations starting in all possible dates
    cdi=True
    benchmark=['BASE_HISTORICA_swing/BOVA11.txt'] 

    initial_capital = [300]  # initial_capital * 1000
    trans_cost_fixed = [5.00] # R$
    trans_cost_percent = [0.03]   # 1 -> 1%
    trans_slippage = [0.05]   # 1 -> 1%
    trans_volume_max = [0.5]   # 1 -> 1% | 0 -> desabilita
    max_open_trades = [100]


    pyramid_profit = [True]
    pyramid_trades = [False]
    daily_update = [False]
    monte_carlo_iterations = [100]


    base_trades_1 = 'base_trades_1.txt'  
    # base_trades_2= '' 
    # base_trades_3= '' 
    
    # -------------------------------------------------------------------------------

    position_size_model = 1  # (1) -> FIXED PERCENT RISK | (2) -> EQUAL PERCENT $ UNITS


    if position_size_model==1:  # FIXED PERCENT RISK

        trade_risk_1 = [0.3]   # 1 -> 1%
        trade_size_limit_1 = [5.0]   # 1 -> 1%

        # trade_risk_2 = [0.0]
        # trade_size_limit_2 = [0.0]

        # trade_risk_3 = [0.0]
        # trade_size_limit_3 = [0.0]

        portfolio_heat = [9.0]   # 1 -> 1%
        risk_round = [True]
    

    elif position_size_model==2:  # EQUAL PERCENT $ UNITS

        ### trade_risk_1, trade_risk_2, trade_risk_3 -> does't apply
        
        trade_size_limit_1 = [2.5]   # 1 -> 1%
        # trade_size_limit_2 = [0]
        # trade_size_limit_3= [0]

        ### portfolio_heat, risk_round -> does't apply


##################################################################################################################################################

    args = inspect.getfullargspec(manager.run).args
    position_size_model_desc=['FIXED PERCENT RISK','EQUAL PERCENT $ UNITS']
    input_file_version = __file__  + ' = ' + str(version)
    keys = list(locals().keys())
    kwargs = dict((arg, eval(arg)) for arg in args if arg in keys)

    manager.run(**kwargs)

##################################################################################################################################################

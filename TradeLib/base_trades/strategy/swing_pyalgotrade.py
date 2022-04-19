version = 1.04

from pyalgotrade import strategy
from pyalgotrade.barfeed import quandlfeed
import numpy as np
import pandas as pd
import os
import sys
import time
import random
import inspect
from datetime import datetime
from TradeLib import exit 
from TradeLib import entry 
from TradeLib import volume
from TradeLib import chart
from TradeLib.filter import scenario
from TradeLib.filter import ohlc

version_txt='\n# ' + os.path.basename(__file__) + ' = ' + str(version)
version_txt+='\n# exit = ' + str(exit.version)
version_txt+='\n# scenario = ' + str(scenario.version)
version_txt+='\n# ohlc = ' + str(ohlc.version)
version_txt+='\n# volume = ' + str(volume.version)
version_txt+='\n# chart = ' + str(chart.version)

def validate_parameters(stoploss_level_1,stoploss_level_2,stoploss_level_3, filters_scenarios, filters_ohlc ):

    filters_scenarios = [x for x in filters_scenarios if x not in [0,1]]
    filters_scenarios_count = len(filters_scenarios)
    if len(set(filters_scenarios))<filters_scenarios_count: return(' duplicated filter_scenario'.strip())
    
    filters_ohlc = [x for x in filters_ohlc if x not in [0,1]]
    filters_ohlc_count = len(filters_ohlc)
    if len(set(filters_ohlc))<filters_ohlc_count: return(' duplicated filter_ohlc'.strip())
   
    if stoploss_level_1<0 or stoploss_level_2<0 or stoploss_level_3<0: return(' Invalid_StopLoss_Levels'.strip())
    if stoploss_level_2 >0 and stoploss_level_2<=stoploss_level_1: return(' Invalid_StopLoss_Levels'.strip())
    if stoploss_level_3 >0 and stoploss_level_3<=stoploss_level_2: return(' Invalid_StopLoss_Levels'.strip())

    return ('')

#-----------------------------------------------------------------------------------------------------------------------

def scenario_filter(filter_scenario_1, filter_scenario_2, filter_scenario_3, filter_scenario_4):

    # if filter_scenario_1 and filter_scenario_2 and ( filter_scenario_3 or filter_scenario_4 ) : return(True) 
    if filter_scenario_1 and filter_scenario_2 and filter_scenario_3 and filter_scenario_4  : return(True) 

#-----------------------------------------------------------------------------------------------------------------------
   
def ohlc_filter(filter_ohlc_1, filter_ohlc_2, filter_ohlc_3, filter_ohlc_4):

    if filter_ohlc_1 and filter_ohlc_2 and ( filter_ohlc_3 or filter_ohlc_4 ) : return(True) 
    # if filter_ohlc_1 and filter_ohlc_2 and filter_ohlc_3 and filter_ohlc_4  : return(True) 

#-----------------------------------------------------------------------------------------------------------------------

def volume_filter(filter_volume, filter_volume_operator, filter_volume_ranking):

    if filter_volume_operator=='AND':
        if filter_volume and filter_volume_ranking : return(True) 

    elif filter_volume_operator=='OR':
        if filter_volume or filter_volume_ranking : return(True) 

    return(False)

#-----------------------------------------------------------------------------------------------------------------------
   
class trade_struct:
    
    __slots__ = ('side', 'entry_signal', 'entry_signal_bar','entry_order_price', 'initial_stop', 'volume', 'entry_date',
                 'entry_price', 'stop_price', 'gain_price', 'exit_signal', 'exit_date', 'exit_price', 'state',
                 'stop_plot_x', 'stop_plot_y', 'gain_plot_y', 'position','breakeven_level_price',
                 'stoploss_level_1_price', 'stoploss_level_2_price', 'stoploss_level_3_price')

    def __init__(self, side='L', entry_signal=0, entry_signal_bar=0, entry_order_price=0, initial_stop=0, volume=0, entry_date=0,
                 entry_price=0, stop_price=0, gain_price=0, exit_signal=None, exit_date=None, exit_price=0, state='Entry',
                 position=None, breakeven_level_price=0, stoploss_level_1_price=0, stoploss_level_2_price=0, stoploss_level_3_price=0):

        self.side=side
        self.entry_signal=entry_signal
        self.entry_signal_bar=entry_signal_bar
        self.entry_order_price=entry_order_price
        self.initial_stop=initial_stop
        self.volume=volume
        
        self.entry_date=entry_date
        self.entry_price=entry_price
        self.stop_price=stop_price
        self.gain_price=gain_price
        self.exit_signal=exit_signal
        self.exit_date=exit_date
        self.exit_price=exit_price
        self.state = state
        self.stop_plot_x =[]
        self.stop_plot_y =[]
        self.gain_plot_y =[]
        self.position = position
        self.breakeven_level_price = breakeven_level_price
        self.stoploss_level_1_price = stoploss_level_1_price
        self.stoploss_level_2_price = stoploss_level_2_price
        self.stoploss_level_3_price = stoploss_level_3_price

#-------------------------------------------------------------------------------------------------------------------------


class Strategy(strategy.BacktestingStrategy):

    def __init__(self, feed, ticker, txt, name, date_start, date_end, lock, trades_trt, hoje_ibov,
        plot, plots, subplots, plot_title, real_time, trade_enforce,
        slippage, randomic, 
        initial_stop, breakeven_level, 
        stoploss_1, stoploss_level_1, stoploss_2, stoploss_level_2, stoploss_3, stoploss_level_3,
        max_duration, gain, compensate_entry_gaps, value_open_trades_on_stop, 
        filter_scenario_1, filter_scenario_2, filter_scenario_3, filter_scenario_4, 
        filter_ohlc_1, filter_ohlc_2, filter_ohlc_3, filter_ohlc_4,         
        stoploss_order_type, gain_order_type, 
        entry_order_type, entry_order_price,       
        filter_volume_qtde,filter_volume_qtde_operator, filter_volume_qtde_ranking, 
        filter_volume_neg, filter_volume_neg_operator, filter_volume_neg_ranking, 
        filter_volume_fin, filter_volume_fin_operator, filter_volume_fin_ranking):


        super(Strategy, self).__init__(feed, 10000000)
        self.getBroker().getFillStrategy().setVolumeLimit(None)

        for item in inspect.signature(Strategy).parameters:
            atrib = '_Strategy__' + item
            setattr(self, atrib, eval(item))

        if self.__trade_enforce==True:
            self.__min_bars =1
        else:
            self.__min_bars = max(entry.MIN_BARS, exit.MIN_BARS, scenario.MIN_BARS, ohlc.MIN_BARS, volume.MIN_BARS)      

        self.__df = pd.read_csv(self.__txt, index_col="Date")     
        self.__df_ibov = pd.read_csv(self.__txt.replace(ticker,'IBOV'), index_col="Date")

        entry.order_price_calc(self.__df, self.__entry_order_price)
        exit.initial_stop_calc(self.__df,self.__initial_stop)
        exit.stoploss_calc(self.__df, self.__stoploss_1, self.__stoploss_2, self.__stoploss_3)
        exit.gain_calc(self.__df,self.__gain)       
        volume.filter_calc(self.__df, self.__filter_volume_qtde, self.__filter_volume_neg, self.__filter_volume_fin)
        volume.rank_calc(self.__df, ticker, txt, self.__filter_volume_qtde_ranking, self.__filter_volume_neg_ranking, self.__filter_volume_fin_ranking)
        scenario.filter_calc(self.__df, self.__df_ibov, [self.__filter_scenario_1,self.__filter_scenario_2,self.__filter_scenario_3,self.__filter_scenario_4])
        ohlc.filter_calc(self.__df,[self.__filter_ohlc_1,self.__filter_ohlc_2,self.__filter_ohlc_3,self.__filter_ohlc_4])


        self.__O = feed[self.__ticker].getOpenDataSeries()
        self.__H = feed[self.__ticker].getHighDataSeries()
        self.__L = feed[self.__ticker].getLowDataSeries()
        self.__C = feed[self.__ticker].getCloseDataSeries()

        self.__barcount = -1

        self.__trades =[]

        self.feed = feed


    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()

        curr = [trade for i, trade in enumerate(self.__trades) if trade.position==position]
        trade = curr[0]

        trade.entry_price = execInfo.getPrice()
        if self.__entry_order_type=='C': 
            trade.entry_price = self.__df['Close'][trade.entry_signal_bar]

        trade.entry_date = execInfo.getDateTime().date()
                
        # Corrige Initial Stop
        if trade.initial_stop>0:
            trade.initial_stop = max(trade.initial_stop + trade.entry_price - trade.entry_order_price, 0.01)

        # Iguala o stop ao Initial Stop logo depois da entrada
        if self.__compensate_entry_gaps == True:
            trade.stop_price = trade.initial_stop
            if trade.gain_price>0:
                trade.gain_price = max(trade.gain_price + trade.entry_price- trade.entry_order_price, 0.01)

        # Calc Breakeven Level
        if self.__breakeven_level>0:
            # trade.breakeven_level_price = trade.entry_price + self.__breakeven_level * (trade.entry_price-trade.initial_stop)
            trade.breakeven_level_price = exit.breakeven_calc(trade.entry_price, self.__breakeven_level, trade.initial_stop)

        # Calc StopLoss Levels
        if self.__stoploss_1>0:
            # trade.stoploss_level_1_price = trade.entry_price + self.__stoploss_level_1 * (trade.entry_price-trade.initial_stop)
            trade.stoploss_level_1_price = exit.stoploss_level_calc(trade.entry_price, self.__stoploss_level_1, trade.initial_stop)
        if self.__stoploss_2>0:
            # trade.stoploss_level_2_price = trade.entry_price + self.__stoploss_level_2 * (trade.entry_price-trade.initial_stop)
            trade.stoploss_level_2_price = exit.stoploss_level_calc(trade.entry_price, self.__stoploss_level_2, trade.initial_stop)
        if self.__stoploss_3>0:
            # trade.stoploss_level_3_price = trade.entry_price + self.__stoploss_level_3 * (trade.entry_price-trade.initial_stop)
            trade.stoploss_level_3_price = exit.stoploss_level_calc(trade.entry_price, self.__stoploss_level_3, trade.initial_stop)


    # def onEnterCanceled(self, position):


    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
                
        # TRADE FINALIZADO --------------------------------------------------------------------------------------------------------------------

        curr = [trade for i, trade in enumerate(self.__trades) if trade.position==position]
        trade = curr[0]

        p_saida = execInfo.getPrice()
        trade.exit_date = execInfo.getDateTime().date()

        trade.exit_price = p_saida
        saida = str(trade.exit_date).replace("-","")
        entrada = str(trade.entry_date).replace("-","")

        self.__lock.acquire()
        if self.__real_time==True:
            if trade.exit_date==self.__hoje_ibov:
                self.__trades_trt.append("%s ARQUIVO > %s SINAL %s DATA_in %s P_in $%.2f DATA_out %s %s P_out $%.2f %s" % 
                                (saida, self.__ticker, trade.entry_signal, entrada, trade.entry_price,
                                saida, "Arquivo", p_saida, self.__name))
        else: # Base de Trades

            if float("{:.5f}".format(trade.entry_price)) > float("{:.5f}".format(trade.initial_stop)):

                p_saida = p_saida * (1-self.__slippage/100*2)

                self.__trades_trt.append([((p_saida/trade.entry_price)-1)*100,
                                   '%s L %s %s %.5f %.5f %.5f %s %s %s %s %.0f %s %s %s' % \
                                   (self.__ticker, entrada, saida, trade.initial_stop, trade.entry_price, p_saida,"0","0","0","0", trade.volume,"0","0","0"),
                                   self.__ticker,
                                   (p_saida-trade.entry_price)/(trade.entry_price-trade.initial_stop)])

                                    # Estrutura trades_trt para base de dados de Trades :
                                    # trades_trt[0] -> delta percentual trade
                                    # trades_trt[1] -> linha texto p\ base trt 
                                    # trades_trt[2] -> ativo
                                    # trades_trt[3] -> R-Multiplo

        self.__lock.release()

        #----------------------------------------------------------------------------------------------------------------------------------------

    def onBars(self, bars):

        bar = bars[self.__ticker]
        self.__barcount +=1
        bc = self.__barcount

        # Checar quantidade mínima de pregões necessarios
        if len(self.__C) < self.__min_bars : return

        # Data inicial ou final
        if self.__date_start != '' and bar.getDateTime().date() < self.__date_start : return
        if self.__date_end != '' and self.__feed.getDataSeries()[-2].getDateTime().date()>=self.__date_end: 
            if self.__feed.eof()==True and self.__plot == True:
                chart.plot_chart(self.__plot_title, self.__ticker, self.__df, self.__subplots, self.__plots, self.__trades)
            return
        
        # SAIDAS ------------------------------------------------------------------------------

        curr = [i for i, trade in enumerate(self.__trades) if trade.exit_signal==None and trade.entry_price>0]
        if len(curr)>0:
            for x in curr:
                trade = self.__trades[x]
                if bar.getClose()<trade.stop_price or (self.__gain>0 and bar.getClose()>trade.gain_price) or (self.__max_duration>0 and trade.position.getAge().days>=self.__max_duration) :

                    trade.position.exitMarket()
                    trade.exit_signal = bar.getDateTime().date()

                    if self.__feed.eof()==True and self.__real_time==True and self.__hoje_ibov == trade.exit_signal:
                        
                        if self.__gain>0 and bar.getClose()>trade.gain_price:
                            sinal_out = "Gain"
                        elif bar.getClose()<trade.stop_price:
                            sinal_out="Stop"
                        else:
                            signal_out = "Duration"
                        entrada = str(trade.entry_date).replace("-","")
                        saida_sinal = str(trade.exit_signal).replace("-","")
                        self.__lock.acquire()
                        self.__trades_trt.append("%s SAIDA > %s SINAL %s DATA_in %s P_in $%.2f STOP $%.5f %s CLOSE $%.2f %s" % 
                                            (saida_sinal, self.__ticker, trade.entry_signal, entrada, trade.entry_price,
                                            trade.stop_price, sinal_out, bar.getClose(), self.__name))
                        self.__lock.release()
        
        # TRADES ABERTOS ------------------------------------------------------------------------------

        curr = [i for i, trade in enumerate(self.__trades) if trade.exit_date==None and trade.entry_price>0]
        if len(curr)>0:

            for x in curr:

                trade = self.__trades[x]

                if self.__plot==True:
                    trade.stop_plot_x.append(bar.getDateTime().date())
                    trade.stop_plot_y.append(trade.stop_price)
                    trade.gain_plot_y.append(trade.gain_price)

                # se for a ultima barra da base do ticker OU hoje_ibov OU date_end do backtest 
                if self.__feed.eof()==True or (self.__date_end != '' and bar.getDateTime().date()>=self.__date_end) or self.__hoje_ibov == bar.getDateTime().date(): 
                    
                    trade.exit_date= bar.getDateTime().date()
                    saida = str(trade.exit_date).replace("-","")
                    entrada = str(trade.entry_date).replace("-","")

                    if self.__value_open_trades_on_stop==False:
                        trade.exit_price = bar.getClose()
                    else:
                        trade.exit_price = trade.stop_price

                    self.__lock.acquire()

                    if self.__real_time == True:
                        if self.__hoje_ibov == trade.exit_date and trade.exit_signal==None:
                            self.__trades_trt.append("%s EM_ANDAMENTO > %s SINAL %s DATA_in %s P_in $%.2f STOP $%.5f %s CLOSE $%.2f %s" % 
                                                (saida, self.__ticker, trade.entry_signal, entrada, trade.entry_price,
                                                trade.stop_price, trade.state, bar.getClose(), self.__name))

                    else: # Base Trades

                        if float("{:.5f}".format(trade.entry_price)) > float("{:.5f}".format(trade.initial_stop)):

                            p_saida = trade.exit_price*(1-self.__slippage/100*2)
                            self.__trades_trt.append([((p_saida/trade.entry_price)-1)*100,
                                               '%s L %s %s %.5f %.5f %.5f %s %s %s %s %.0f %s %s %s' % \
                                               (self.__ticker, entrada, saida, trade.initial_stop, trade.entry_price, p_saida,"0","0","0","0",trade.volume,"0","0","0"),
                                               self.__ticker,
                                               (p_saida-trade.entry_price)/(trade.entry_price-trade.initial_stop)])

                                                # Estrutura trades_trt para base de dados de Trades :
                                                # trades_trt[0] -> delta percentual trade
                                                # trades_trt[1] -> linha texto p\ base trt 
                                                # trades_trt[2] -> ativo
                                                # trades_trt[3] -> R-Multiplo
                    
                    self.__lock.release()

                # Movimentações de Stop e Gain
                if trade.exit_signal==None:
                    exit.stoploss_move(trade, self.__df, bc, self.__breakeven_level, self.__stoploss_1, self.__stoploss_2, self.__stoploss_3)
                    exit.gain_move(trade, self.__df, bc, self.__gain)


        # ENTRADAS ---------------------------------------------------------------------------------------

        trade_signal=False
        
        if self.__trade_enforce==True:
            if bar.getDateTime().date() == self.__date_start :
                trade_signal=True

        else:

            O = self.__O[-5:]
            H = self.__H[-5:]
            L = self.__L[-5:]
            C = self.__C[-5:]

            v_qtde = volume.filter_qtde(self.__df,bc,self.__filter_volume_qtde)
            v_neg = volume.filter_neg(self.__df,bc,self.__filter_volume_neg)
            v_fin = volume.filter_fin(self.__df,bc,self.__filter_volume_fin)
            v_ranking_qtde = volume.filter_ranking(self.__df, bc,'volume_rank', self.__filter_volume_qtde_ranking)
            v_ranking_neg = volume.filter_ranking(self.__df, bc, 'neg_rank', self.__filter_volume_neg_ranking)
            v_ranking_fin = volume.filter_ranking(self.__df, bc, 'fin_rank', self.__filter_volume_fin_ranking)
            sc1 = scenario.filter(O,H,L,C,self.__df,bc,self.__filter_scenario_1)
            sc2 = scenario.filter(O,H,L,C,self.__df,bc,self.__filter_scenario_2)
            sc3 = scenario.filter(O,H,L,C,self.__df,bc,self.__filter_scenario_3)
            sc4 = scenario.filter(O,H,L,C,self.__df,bc,self.__filter_scenario_4)
            ohlc1 = ohlc.filter(O,H,L,C,self.__filter_ohlc_1)
            ohlc2 = ohlc.filter(O,H,L,C,self.__filter_ohlc_2)
            ohlc3 = ohlc.filter(O,H,L,C,self.__filter_ohlc_3)
            ohlc4 = ohlc.filter(O,H,L,C,self.__filter_ohlc_4)


            if self.__date_end == '' or bar.getDateTime().date() < self.__date_end: 
                if volume_filter(v_qtde, self.__filter_volume_qtde_operator, v_ranking_qtde):
                    if volume_filter(v_neg, self.__filter_volume_neg_operator, v_ranking_neg):
                        if volume_filter(v_fin, self.__filter_volume_fin_operator, v_ranking_fin):
                            if scenario_filter(sc1,sc2,sc3,sc4):
                                if ohlc_filter(ohlc1,ohlc2,ohlc3,ohlc4):
                                    if self.__randomic==1 or random.random()<self.__randomic:
                                        trade_signal=True
        if trade_signal==True:    

            position=None

            order_price=self.__df.entry_order_price[bc]
            stop = self.__df.initial_stop[bc]
            gain = self.__df.gain[bc]

            if order_price >=0 and stop>=0 and gain>=0:

                if self.__entry_order_type=='M' or self.__entry_order_type=='C':
                    position = self.enterLong(self.__ticker, 1)
                else:
                    if self.__entry_order_type=='L': 
                        position = self.enterLongLimit(self.__ticker, order_price,  1)
                    elif self.__entry_order_type=='S': 
                        position = self.enterLongStop(self.__ticker, order_price, 1)

            if position != None:

                hj = bar.getDateTime().date()
                new_trade= trade_struct(
                    entry_signal = str(hj).replace("-",""),
                    entry_signal_bar = bc,
                    entry_order_price = order_price,
                    initial_stop = stop,
                    stop_price = stop,
                    gain_price = gain,
                    volume = self.__df.EMA_Fin[bc],
                    position = position)

                self.__trades.append(new_trade)

                if self.__real_time==True:
                    if self.__feed.eof()==True and self.__hoje_ibov == hj:
                        self.__lock.acquire()
                        self.__trades_trt.append("%s ENTRADA > %s BUY at $%.2f STOP_in $%.5f VOLUME %.0f %s" % 
                            (new_trade.entry_signal, self.__ticker, new_trade.entry_order_price, stop, self.__df.EMA_Fin[bc], self.__name))
                        self.__lock.release()

        # PLOT CHART ------------------------------------------------------------------------------

        if self.__feed.eof()==True and self.__plot == True:

            chart.plot_chart(self.__plot_title, self.__ticker, self.__df, self.__subplots, self.__plots, self.__trades)


#------------------------------------------------------------------------------------------------

def run(**kwargs):

    feed = quandlfeed.Feed()
    feed.addBarsFromCSV(kwargs.get('ticker'), kwargs.get('txt'))

    pyalgo = Strategy(feed,**kwargs)

    pyalgo.run()

#------------------------------------------------------------------------------------------------

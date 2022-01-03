import os
import sys
import pandas as pd

folder=__file__.replace(os.path.basename(__file__),'')

tickers =os.listdir(folder)
tickers = [ticker for ticker in tickers if ticker.endswith(".txt")]

df = pd.DataFrame()
df_qtde = pd.DataFrame()
df_neg = pd.DataFrame()
df_fin = pd.DataFrame()


def calc_fin(O,H,L,C,V,Fin): 
    if Fin==0:
        return (O*2+H+L+C*2)/6*V
    else:
        return Fin

for ticker in tickers:
    if ticker=="IBOV.txt": continue
    
    df_ticker = pd.read_csv(folder+ticker, index_col=None)
    df_ticker["Fin"]=df_ticker.apply(lambda row: calc_fin(row["Open"],row["High"],row["Low"],row["Close"],row["Volume"],row["Fin"]),axis=1)
    df_ticker['Ticker'] = ticker.replace(".txt","")
    df = pd.concat([df,df_ticker], ignore_index=True)


df_qtde = df.sort_values(by=['Date', 'Volume'], ascending=[True,False])
df_rank = df_qtde.groupby('Date')['Ticker'].apply(list).reset_index(name='Ticker')
df_rank['Ticker']= df_rank.Ticker.apply(lambda x: ','.join([str(i) for i in x]))
df_rank.to_csv(folder+'ranking_qtde.csv', index=False)

df_neg = df.sort_values(by=['Date', 'Neg'], ascending=[True,False])
df_rank = df_neg.groupby('Date')['Ticker'].apply(list).reset_index(name='Ticker')
df_rank['Ticker']= df_rank.Ticker.apply(lambda x: ','.join([str(i) for i in x]))
df_rank.to_csv(folder+'ranking_neg.csv', index=False)

df_fin = df.sort_values(by=['Date', 'Fin'], ascending=[True,False])
df_rank = df_fin.groupby('Date')['Ticker'].apply(list).reset_index(name='Ticker')
df_rank['Ticker']= df_rank.Ticker.apply(lambda x: ','.join([str(i) for i in x]))
df_rank.to_csv(folder+'ranking_fin.csv', index=False)



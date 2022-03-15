version = 1.02

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_chart(title, ticker, df, subplots, plots, trades):

    rows=3
    n_sp = len(subplots)
    specs=[ [{"rowspan": 3}], [None], [None] ] + (n_sp * [[{}]])

    fig= make_subplots(rows=rows+n_sp,cols=1,specs=specs, print_grid=True, shared_xaxes=True)

    for item in subplots:
        rows+=1

        if item=='Volume':
            fig.add_trace(go.Bar(x=df.index, y=df[item], name=item, marker_color='black', opacity=1),row=rows, col=1)
            fig.update_layout(bargap=0)
        else:
            if type(item) is list:
                title_sub=''
                for index, i in enumerate(item):
                    fig.add_trace(go.Scatter(x=df.index, y=df[i], name=i, line={"width":1}), row=rows, col=1)
                    if index==0: title_sub+=str(i)
                    else: title_sub+= ' | ' + str(i) 
                fig.update_yaxes(title_text=title_sub, row=rows, col=1)
       
            else:
                fig.add_trace(go.Scatter(x=df.index, y=df[item], name=item, line={"width":1}), row=rows, col=1)
                fig.update_yaxes(title_text=item, row=rows, col=1)

    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC'))
    
    fig.update_layout(
    title=title + ' --> ' + ticker,
    yaxis_title=ticker)

    for item in plots:
        fig.add_trace(go.Scatter(x=df.index, y=df[item], name = item, line={"width":1}))

    if not ticker=='IBOV':
        for t in trades:
            if t.entry_date==0: continue
            nt = str(trades.index(t))
            fig.add_annotation(x=t.entry_date, y=t.entry_price, text='E'+nt)
            fig.add_annotation(x=t.exit_date, y=t.exit_price, text='X'+nt) 
            fig.add_trace(go.Scatter(x=t.stop_plot_x, y=t.stop_plot_y, mode='markers', name='Stop'+nt, marker={'size':4}))
            if t.gain_price>0:
                fig.add_trace(go.Scatter(x=t.stop_plot_x, y=t.gain_plot_y, mode='markers', name='Gain'+nt, marker={'size':4}))    
    
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()

#--------------------------------------------------------------------------
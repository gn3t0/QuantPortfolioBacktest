version = 1.0

MIN_BARS = 5

def order_price_calc(df, entry_order_price):
    
    if entry_order_price==0:
        df['entry_order_price']=df['Close']
        return

    if entry_order_price>0 and entry_order_price<=100:
        df['entry_order_price']=calc.rolling_highest(series=df['High'],period=entry_order_price)
        return

    if entry_order_price>100 and entry_order_price<=200:
        df['entry_order_price']=calc.rolling_lowest(series=df['Low'],period=entry_order_price-100)
        return

    df['entry_order_price']=0


#--------------------------------------------------------------------------

def entry_calc(df):

    pass
       
#--------------------------------------------------------------------------
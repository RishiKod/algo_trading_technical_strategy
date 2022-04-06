import pandas as pd
import yfinance as yf
import numpy as np
import datetime as dt
import copy

def macd(df, fast = 12, slow = 26, signal = 9):
    df= df.copy()
    df['ma_fast'] = df['Adj Close'].ewm(span = fast, min_periods = fast).mean()
    df['ma_slow'] = df['Adj Close'].ewm(span = slow, min_periods = slow).mean()
    df['macd'] = df['ma_fast'] - df['ma_slow']
    df['signal'] = df['macd'].ewm(span = signal, min_periods = signal).mean()
#    df.dropna(inplace = True)
    return df[['macd', 'signal']]

def cagr(df, n):
    df = df.copy()
    df["cum_return"] = (1 + df["daily_return"]).cumprod()
    cagr = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return cagr

tickers = ['ADANIPORTS.NS',
 'ASIANPAINT.NS',
 'AXISBANK.NS',
 'BAJAJ-AUTO.NS',
 'BAJFINANCE.NS',
 'BAJAJFINSV.NS',
 'BPCL.NS',
 'BHARTIARTL.NS',
 'INFRATEL.NS',
 'BRITANNIA.NS',
 'CIPLA.NS',
 'COALINDIA.NS',
 'DRREDDY.NS',
 'EICHERMOT.NS',
 'GAIL.NS',
 'GRASIM.NS',
 'HCLTECH.NS',
 'HDFCBANK.NS',
 'HDFCLIFE.NS',
 'HEROMOTOCO.NS',
 'HINDALCO.NS',
 'HINDUNILVR.NS',
 'ICICIBANK.NS',
 'ITC.NS',
 'IOC.NS',
 'INDUSINDBK.NS',
 'INFY.NS',
 'JSWSTEEL.NS',
 'KOTAKBANK.NS',
 'LT.NS',
 'M&M.NS',
 'MARUTI.NS',
 'NTPC.NS',
 'NESTLEIND.NS',
 'ONGC.NS',
 'POWERGRID.NS',
 'RELIANCE.NS',
 'SHREECEM.NS',
 'SBIN.NS',
 'SUNPHARMA.NS',
 'TCS.NS',
 'TATAMOTORS.NS',
 'TATASTEEL.NS',
 'TECHM.NS',
 'TITAN.NS',
 'UPL.NS',
 'ULTRACEMCO.NS',
 'WIPRO.NS',
 'ZEEL.NS']

#start = dt.date.today() - dt.timedelta(40+365*1)
start = '2014-12-31'
#end = dt.date.today()
end = '2019-12-31'
ohlcv_dict = {}

for ticker in tickers:
    ohlcv_dict[ticker] = yf.download(ticker, start, end, interval = '1d')
    ohlcv_dict[ticker].dropna(inplace = True, how = 'all')
tickers = ohlcv_dict.keys()

ohlcv = copy.deepcopy(ohlcv_dict)
return_df = pd.DataFrame()
for ticker in tickers:
    print("calculating monthly return for ",ticker)
    ohlcv[ticker]["mon_ret"] = ohlcv[ticker]['Adj Close'].pct_change()
    return_df[ticker] = ohlcv[ticker]["mon_ret"]
#return_df.drop(return_df.index[:2], inplace = True)

ohlcv_macd = pd.DataFrame()
for ticker in tickers:
    ohlcv_macd['m'+ticker] = macd(ohlcv[ticker])['macd']
    ohlcv_macd['s'+ticker] = macd(ohlcv[ticker])['signal']

trade = pd.DataFrame(index = return_df.index, columns = tickers)
for ticker in tickers:
    position = ''
    for i in list(range(len(ohlcv_macd))):
        if ohlcv_macd.loc[ohlcv_macd.index[i],'m'+ticker] > ohlcv_macd.loc[ohlcv_macd.index[i],'s'+ticker] and position != 'buy':
            position = 'buy'
        elif ohlcv_macd.loc[ohlcv_macd.index[i],'m'+ticker] < ohlcv_macd.loc[ohlcv_macd.index[i],'s'+ticker] and position == 'buy':
            position = 'sell'
            trade.loc[trade.index[i], ticker] = return_df.loc[return_df.index[i], ticker]
        elif position == 'buy':
            trade.loc[trade.index[i], ticker] = return_df.loc[return_df.index[i], ticker]

trade['daily_return'] = trade.mean(axis = 1)
trade['daily_return'].fillna(0, inplace = True)
trade['worth'] = pd.Series(dtype = object)
trade.loc[trade.index[0],'worth'] = 100

for i in list(range(1, len(trade))):    
    trade.loc[trade.index[i], 'worth'] = trade.loc[trade.index[i-1],'worth']*(1+trade.loc[trade.index[i], 'daily_return'])

check = pd.DataFrame(index = return_df.index)
for ticker in tickers:
    check[ticker]= trade[ticker]
    check['m'+ticker] = ohlcv_macd['m'+ticker]
    check['s'+ticker] = ohlcv_macd['s'+ticker]
    check[ticker+ ' d_ret'] = return_df[ticker]

cagr(trade, 4.8)
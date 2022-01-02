import yfinance as yf
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import ta  # technical analysis calculation library

stock = 'BTC-USD'
# can go back 60 days with a 30min interval
df = yf.download(stock, start='2021-12-01', interval = '30m')

# calc technical indicators

# calc K line
df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window = 14, smooth_window = 3)

# calc D line
df['%D'] = df['%K'].rolling(window = 3).mean()

# calc RSI
df['rsi'] = ta.momentum.rsi(df.Close, window = 14)

# calc MACD
df['macd'] = ta.trend.macd_diff(df.Close)

df.dropna(inplace = True)

# check crossings of K and D lines
# rows show if K and D lines cross (1) or not (0) aka buy trigger
# lags is number of time steps you want to look back
def getTriggers(df, lags, buy = True):
    dfx = pd.DataFrame()
    for i in range(1,lags+1):
        if buy:
            mask = (df['%K'].shift(i) < 20) & (df['%D'].shift(i) < 20)
        else: # sell
            mask = (df['%K'].shift(i) > 80) & (df['%D'].shift(i) > 80)
        dfx = dfx.append(mask, ignore_index = True)
    return dfx.sum(axis = 0)

df['BuyTrigger'] = np.where(getTriggers(df, 4,), 1, 0)

df['SellTrigger'] = np.where(getTriggers(df, 4, False), 1, 0)

df['Buy'] = np.where((df.BuyTrigger) 
                    & (df['%K'].between(20, 80))
                    & (df['%D'].between(20,80)) 
                    & (df.rsi > 50) 
                    & (df.macd > 0), 1, 0)

df['Sell'] = np.where((df.SellTrigger) 
                    & (df['%K'].between(20, 80))
                    & (df['%D'].between(20,80)) 
                    & (df.rsi < 50) 
                    & (df.macd < 0), 1, 0)

Buying_dates = []
Selling_dates = []

for i in range(len(df) - 1):
    if df.Buy.iloc[i]:
        Buying_dates.append(df.iloc[i + 1].name)
        for num,j in enumerate(df.Sell[i:]):
            if j:
                Selling_dates.append(df.iloc[i + num + 1].name)
                break

# find buyting and selling dates
cutit = len(Buying_dates) - len(Selling_dates)

if cutit:
    Buying_dates = Buying_dates[:-cutit]

frame = pd.DataFrame({'Buying_dates':Buying_dates, 'Selling_dates':Selling_dates})

# avoid overlapping positions

actuals = frame[frame.Buying_dates > frame.Selling_dates.shift(1)]

# calc profits
def profitCalc():
    BuyPrices = df.loc[actuals.Buying_dates].Open
    SellPrices = df.loc[actuals.Selling_dates].Open
    return (SellPrices.values - BuyPrices.values) / BuyPrices.values

profits = profitCalc()

print('Percent profits are:')
print(profits * 100)

mean_profit = profits.mean()
# leverage not taken into account
cumultive_profit = profits.cumsum()

plt.figure(figsize=(20,10))
plt.plot(df.Close, label = 'Asset Price', color='k', alpha=0.7)
plt.scatter(actuals.Buying_dates, df.Open[actuals.Buying_dates], label = 'Buy Trigger', marker = '^', color='g', s=500)
plt.scatter(actuals.Selling_dates, df.Open[actuals.Selling_dates], label = 'Sell Trigger', marker = 'v', color='r', s=500)
plt.legend()
plt.savefig(stock + '_stocastic_RSI_MACD_plots')
plt.show()
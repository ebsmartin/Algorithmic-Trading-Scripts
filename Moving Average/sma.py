import yfinance as yf
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

stock = 'BTC-USD'
df = yf.download(stock, start='2020-01-01')

df['MA20'] = df['Adj Close'].rolling(window=20).mean()
df['MA50'] = df['Adj Close'].rolling(window=50).mean()

df = df.dropna()

df = df[['Adj Close', 'MA20', 'MA50']]

Buy = []
Sell = []

for i in range(len(df)):
    if df.MA20.iloc[i] > df.MA50.iloc[i] and df.MA20.iloc[i-1] < df.MA50.iloc[i-1]:
        Buy.append(i)
    elif df.MA20.iloc[i] < df.MA50.iloc[i] and df.MA20.iloc[i-1] > df.MA50.iloc[i-1]:
        Sell.append(i)

print(Buy)
print(Sell)

plt.figure(figsize = (12, 5))
plt.plot(df['Adj Close'], label = 'Asset Price', c = 'blue', alpha = 0.5)
plt.plot(df['MA20'], label = '20 Day Moving Average', c = 'black', alpha = 0.9)
plt.plot(df['MA50'], label = '50 Day Moving Average', c = 'magenta', alpha = 0.9)
plt.scatter(df.iloc[Buy].index, df.iloc[Buy]['Adj Close'], marker = '^', c = 'green', s = 100, label = 'Buy Signal')
plt.scatter(df.iloc[Sell].index, df.iloc[Sell]['Adj Close'], marker = 'v', c = 'red', s = 100, label = 'Sell Signal')
plt.legend()
plt.savefig(stock + '_plots')
plt.show()



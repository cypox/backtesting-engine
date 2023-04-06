import yfinance as yf
import pandas as pd
from datetime import date

from strategy import *


tickers = ['MSFT', 'TSLA', 'AAPL', 'NVDA', 'NIO', 'AMD', 'GME', 'AMC', 'NFLX', 'META']

today = date.today()
start_date= "2005-01-01"
end_date="2020-11-19"

data = None
for ticker in tickers:
    df = yf.download(ticker, start=start_date, end=today)
    df = df.rename(columns={"Adj Close": ticker})
    if data is None:
        data = df
    else:
        data = pd.concat([data, df], axis=1)

data = data[tickers]

HISTORY = 10
FEE = 1
n = len(data)
t = len(tickers)

bot1 = SMAStrategy()
bot2 = SMAAggressiveStrategy()
bot3 = SMAHodlStrategy()
bot4 = TendencyStrategy()

for i in range(n-HISTORY-1):
    input_data = data[i:i+HISTORY+1]
    bot1.process(input_data)
    bot2.process(input_data)
    bot3.process(input_data)
    bot4.process(input_data)

bot1.net_worth(data.iloc[n-1])
bot2.net_worth(data.iloc[n-1])
bot3.net_worth(data.iloc[n-1])
bot4.net_worth(data.iloc[n-1])

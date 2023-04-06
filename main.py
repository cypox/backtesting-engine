import yfinance as yf
import pandas as pd
from datetime import date

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
INITIAL_BALANCE = 1000
n = len(data)
t = len(tickers)

class Strategy:
    def __init__(self):
        self.balance = INITIAL_BALANCE
        self.held_stocks = {ticker: 0 for ticker in tickers}
        self.held_stocks_cost = {ticker: 0 for ticker in tickers}
        self.returns_by_stock = {ticker: 0 for ticker in tickers}
        self.trades_per_stock = {ticker: 0 for ticker in tickers}
        self.days = 0
    
    def net_worth(self, stock_prices):
        net_worth = self.balance
        net_worth += sum([self.held_stocks[t] * stock_prices[t] for t in tickers])
        print(f"net worth: ${net_worth:0.0f}, liquidity: ${self.balance:0.0f}")
        net_earnings = net_worth - INITIAL_BALANCE
        print(f"estimated returns: ${(net_earnings/self.days):.2f} per day")
        trades = sum(self.trades_per_stock.values())
        print(f"realised {trades} trades")
        print(f"realised {(trades/self.days):.2f} trades per day")
        print(f"returns by trade: ${(net_earnings/trades):.2f} per trade")
        print(f"current portfolio: {self.held_stocks}")
        print(f"cost of held stocks: {self.held_stocks_cost}")
        print(f"returns by ticker: {self.returns_by_stock}")
        print(f"trades by ticker: {self.trades_per_stock}")

    def process(self, input_data):
        pass

    def order(self, ticker, qtty, unit_price):
        if qtty > 0: # buy
            actual_qtty = min(qtty, int(self.balance / unit_price))
            if actual_qtty <= 0:
                return
            self.trades_per_stock[ticker] += 1
            self.balance -= unit_price * actual_qtty
            self.held_stocks[ticker] += actual_qtty
            self.held_stocks_cost[ticker] += unit_price * actual_qtty
            print(f"bought {actual_qtty} units of {ticker} @ {unit_price} and current balance is ${self.balance}")
        elif qtty < 0: # sell
            qtty = -qtty
            actual_qtty = min(qtty, self.held_stocks[ticker])
            if actual_qtty <= 0:
                return
            self.trades_per_stock[ticker] += 1
            average_ticker_buy_price = self.held_stocks_cost[ticker] / self.held_stocks[ticker]
            self.returns_by_stock[ticker] += (unit_price - average_ticker_buy_price) * actual_qtty
            self.balance += unit_price * actual_qtty
            self.held_stocks[ticker] -= actual_qtty
            self.held_stocks_cost[ticker] -= average_ticker_buy_price * actual_qtty
            print(f"sold {actual_qtty} units of {ticker} @ {unit_price} and current balance is ${self.balance}")

class SMAStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self)
    
    def process(self, input_data):
        self.days += 1
        for ticker in tickers:
            average = input_data[ticker][0:HISTORY].sum() / HISTORY
            current_price = input_data[ticker][HISTORY]
            if average == 0 or current_price == 'NaN':
                continue
            pct = (current_price - average) / average
            qtty = 0
            if pct > 0.2:
                qtty = -10
            elif pct > 0.1:
                qtty = -2
            elif pct < -0.1:
                qtty = 2
            elif pct < -0.2:
                qtty = 10
            if qtty != 0:
                self.order(ticker, qtty, current_price)

class SMAAggressiveStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self)
    
    def process(self, input_data):
        self.days += 1
        for ticker in tickers:
            average = input_data[ticker][0:HISTORY].sum() / HISTORY
            current_price = input_data[ticker][HISTORY]
            if average == 0 or current_price == 'NaN':
                continue
            pct = (current_price - average) / average
            qtty = 0
            if pct > 0.1:
                qtty = -10
            elif pct > 0.05:
                qtty = -2
            elif pct < -0.05:
                qtty = 2
            elif pct < -0.1:
                qtty = 10
            if qtty != 0:
                self.order(ticker, qtty, current_price)

class SMAHodlStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self)
    
    def process(self, input_data):
        self.days += 1
        for ticker in tickers:
            average = input_data[ticker][0:HISTORY].sum() / HISTORY
            current_price = input_data[ticker][HISTORY]
            if average == 0 or current_price == 'NaN':
                continue
            pct = (current_price - average) / average
            qtty = 0
            if pct > 0.3:
                qtty = -10
            elif pct > 0.2:
                qtty = -2
            elif pct < -0.05:
                qtty = 2
            elif pct < -0.1:
                qtty = 10
            if qtty != 0:
                self.order(ticker, qtty, current_price)

bot1 = SMAStrategy()
bot2 = SMAAggressiveStrategy()
bot3 = SMAHodlStrategy()

for i in range(n-HISTORY-1):
    input_data = data[i:i+HISTORY+1]
    bot1.process(input_data)
    bot2.process(input_data)
    bot3.process(input_data)

bot1.net_worth(data.iloc[n-1])
bot2.net_worth(data.iloc[n-1])
bot3.net_worth(data.iloc[n-1])

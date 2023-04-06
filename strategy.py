INITIAL_BALANCE = 1000

class Strategy:
    def __init__(self, tickers, history):
        self.balance = INITIAL_BALANCE
        self.tickers = tickers
        self.held_stocks = {ticker: 0 for ticker in tickers}
        self.held_stocks_cost = {ticker: 0 for ticker in tickers}
        self.returns_by_stock = {ticker: 0 for ticker in tickers}
        self.trades_per_stock = {ticker: 0 for ticker in tickers}
        self.days = 0
        self.history = history
    
    def net_worth(self, stock_prices):
        net_worth = self.balance
        net_worth += sum([self.held_stocks[t] * stock_prices[t] for t in self.tickers])
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
        for ticker in self.tickers:
            average = input_data[ticker][0:self.history].sum() / self.history
            current_price = input_data[ticker][self.history]
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
        for ticker in self.tickers:
            average = input_data[ticker][0:self.history].sum() / self.history
            current_price = input_data[ticker][self.history]
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
        for ticker in self.tickers:
            average = input_data[ticker][0:self.history].sum() / self.history
            current_price = input_data[ticker][self.history]
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

class TendencyStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self)
    
    def process(self, input_data):
        self.days += 1
        for ticker in self.tickers:
            price_m2 = input_data[ticker][-3]
            price_m1 = input_data[ticker][-2]
            price_m0 = input_data[ticker][-1]
            qtty = 0
            if price_m0 > price_m1 and price_m1 > price_m2:
                qtty = 5
            elif price_m0 > price_m1:
                qtty = 1
            elif price_m0 < price_m1 and price_m1 < price_m2:
                qtty = -2
            if qtty != 0:
                self.order(ticker, qtty, price_m0)

import pandas as pd
import numpy as np


class PortfolioManager:
    def __init__(self, initial_capital):  # signals, stock_data):
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        # self.signals = signals
        self.stock_data = None

        self.portfolio = None
        self.init_portfolio()

        self.portfolio_total = None
        self.portfolio_total_return = None
        self.sharp_ratio = None
        self.cagr = None

    def init_portfolio(self):
        self.portfolio = pd.DataFrame(dict(Date=[],
                                           num_shares=[],
                                           holdings=[],
                                           cash=[],
                                           total=[],
                                           returns=[]))
        self.portfolio.set_index("Date", inplace=True)

    def get_last_portfolio_value(self):
        if self.portfolio.shape[0]>0:
            return self.portfolio.iloc[-1]
        else:
            return None

    def update(self, signals, stock_data):
        last_signal = signals.iloc[-1]
        last_stock_data = stock_data.iloc[-1]
        self.stock_data = stock_data

        position = int(last_signal.positions)
        # print(position)
        if position == 1:
            num_shares = int(self.current_cash / last_stock_data["Close"])
            # print(f"Num shares {num_shares}")
            holdings = num_shares * last_stock_data["Close"]
            # print(f"Holdings {holdings}")
            cash = self.current_cash - holdings
            # print(f"Cash {cash}")
            self.current_cash = cash
            total = holdings + cash
            # print(f"Total {total}")
            self.portfolio.loc[last_signal.name] = [cash, holdings, num_shares, 0, total]
        elif position == -1:
            last_portfolio = self.portfolio.iloc[-1]
            # print(last_portfolio)
            cash = last_portfolio.cash + last_portfolio.num_shares * last_stock_data["Close"]
            self.current_cash = cash
            num_shares = 0
            holdings = 0
            total = holdings + cash
            self.portfolio.loc[last_signal.name] = [cash, holdings, num_shares, 0, total]
        else:
            if self.portfolio.shape[0]>0:
                last_portfolio = self.portfolio.iloc[-1]
                self.portfolio.loc[last_signal.name] = last_portfolio
                self.portfolio.loc[last_signal.name]["holdings"] = \
                    self.portfolio.loc[last_signal.name].num_shares * last_stock_data["Close"]
                self.portfolio.loc[last_signal.name]["total"] = \
                    self.portfolio.loc[last_signal.name]["holdings"] + \
                    self.portfolio.loc[last_signal.name]["cash"]
            else:
                self.portfolio.loc[last_signal.name] = [self.current_cash, 0, 0, 0, self.current_cash]


    # def backtest_portfolio(self):
    #     # Generate a pandas DataFrame to store quantity held at any “bar” timeframe
    #     positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
    #     positions["Stock"] = 100 * self.signals['signal']   # Transact 100 shares on a signal
    #
    #     # self.portfolio = positions
    #     # self.portfolio["cash"] = self.initial_capital
    #     #
    #     # for idx in self.portfolio.shape[1]:
    #     #     self.portfolio["Stock"][idx] = int(self.portfolio["cash"][idx] / self.stock_data['Close']) * self.stock_data['Close']
    #     #     self.portfolio['holdings'][idx] = self.portfolio["Stock"][idx]
    #     #
    #     #     self.portfolio['cash'][idx] = self.initial_capital - (pos_diff.multiply(self.stock_data['Close'], axis=0)).sum(
    #     #         axis=1).cumsum()
    #
    #     # Initialize the portfolio with value owned
    #     self.portfolio = positions.multiply(self.stock_data['Close'], axis=0)
    #
    #     # Store the difference in shares owned
    #     pos_diff = positions.diff()
    #
    #     # Add `holdings` to portfolio
    #     self.portfolio['holdings'] = (positions.multiply(self.stock_data['Close'], axis=0)).sum(axis=1)
    #
    #     # Add `cash` to portfolio
    #     self.portfolio['cash'] = self.initial_capital - (pos_diff.multiply(self.stock_data['Close'], axis=0)).sum(axis=1).cumsum()
    #
    #     # Add `total` to portfolio
    #     self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdings']
    #
    #     # Add `returns` to portfolio
    #     self.portfolio['returns'] = self.portfolio['total'].pct_change()

    def calc_portfolio_metrics(self):
        self.calc_returns()

        self.calc_portfolio_total()
        self.calc_portfolio_total_return()
        self.calc_sharp_ratio()
        self.calc_cagr()

    def calc_returns(self):
        self.portfolio["returns"] = self.portfolio['total'].pct_change()

    def calc_portfolio_total(self):
        self.portfolio_total = round(self.portfolio['total'][-1], 2)

    def calc_portfolio_total_return(self):
        self.portfolio_total_return = round((self.portfolio['total'][-1] / self.portfolio['total'][0]-1)*100, 2)

    def calc_sharp_ratio(self):
        # Isolate the returns of your strategy
        returns = self.portfolio['returns']

        # annualized Sharpe ratio
        sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())

        self.sharp_ratio = round(sharpe_ratio, 2)

    def calc_cagr(self):
        # Get the number of days in `aapl`
        days = (self.stock_data.index[-1] - self.stock_data.index[0]).days

        # Calculate the CAGR
        self.cagr = round((((self.portfolio['total'][-1] / self.portfolio['total'][0]) ** (365.0 / days)) - 1)*100, 2)


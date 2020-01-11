import pandas as pd
import numpy as np


class PortfolioManager:
    def __init__(self, tickers, initial_capital, percentage=None):  # signals, stock_data):
        self.tickers = tickers
        self.initial_capital = {}
        self.current_cash = {}
        self.set_initial_capitals(initial_capital, percentage)

        self.stock_data = None
        self.portfolio = None
        self.init_portfolio()

        self.portfolio_total = None
        self.portfolio_total_return = None
        self.sharp_ratio = None
        self.cagr = None

    def set_initial_capitals(self, initial_capital, percentage):
        if percentage is None:
            num_of_tickers = len(self.tickers)
            for ticker in self.tickers:
                self.initial_capital[ticker] = initial_capital / num_of_tickers
                self.current_cash[ticker] = initial_capital / num_of_tickers
        else:
            for ticker, perc in zip(self.tickers, percentage):
                self.initial_capital[ticker] = initial_capital * perc
                self.current_cash[ticker] = initial_capital * perc

    def init_portfolio(self):
        self.portfolio = pd.DataFrame(dict(Date=[],
                                           cash=[],
                                           total=[],
                                           returns=[]))
        for ticker in self.tickers:
            self.portfolio[ticker] = []
            self.portfolio[ticker+"_holdings"] = []
        self.portfolio.set_index("Date", inplace=True)

    def get_last_portfolio_value(self):
        if self.portfolio.shape[0] > 0:
            return self.portfolio.iloc[-1]
        else:
            return None

    def update(self, signals, stock_data):
        last_signal = None
        for ticker in self.tickers:
            last_signal = signals[ticker].iloc[-1]
            last_stock_data = stock_data.loc[ticker].iloc[-1]
            self.stock_data = stock_data.loc[ticker]
            position = int(last_signal.positions)
            if position == 1:
                num_shares = int(self.current_cash[ticker] / last_stock_data["Close"])
                holdings = num_shares * last_stock_data["Close"]
                cash = self.current_cash[ticker] - holdings
                self.current_cash[ticker] = cash
                if not self.portfolio.index.isin([last_signal.name]).any():
                    self.portfolio.loc[last_signal.name] = 0
                self.portfolio.loc[last_signal.name][ticker] = num_shares
                self.portfolio.loc[last_signal.name][ticker+"_holdings"] = holdings
                # self.portfolio.loc[last_signal.name] = [cash, holdings, num_shares, 0, total]
            elif position == -1:
                last_portfolio = self.portfolio.iloc[-1]
                cash = last_portfolio.cash + last_portfolio[ticker] * last_stock_data["Close"]
                self.current_cash[ticker] = cash
                num_shares = 0
                holdings = 0
                if not self.portfolio.index.isin([last_signal.name]).any():
                    self.portfolio.loc[last_signal.name] = 0
                self.portfolio.loc[last_signal.name][ticker] = num_shares
                self.portfolio.loc[last_signal.name][ticker + "_holdings"] = holdings
            else:
                if self.portfolio.shape[0] > 0:
                    last_portfolio = self.portfolio.iloc[-1]
                    if not self.portfolio.index.isin([last_signal.name]).any():
                        self.portfolio.loc[last_signal.name] = last_portfolio
                    self.portfolio.loc[last_signal.name][ticker + "_holdings"] = \
                        self.portfolio.loc[last_signal.name][ticker] * last_stock_data["Close"]
                else:
                    self.portfolio.loc[last_signal.name] = 0
                    self.portfolio.loc[last_signal.name][ticker] = 0
                    self.portfolio.loc[last_signal.name][ticker + "_holdings"] = 0
        current_cash = 0
        total = 0
        for ticker in self.tickers:
            current_cash += self.current_cash[ticker]
            total += self.portfolio.loc[last_signal.name][ticker+"_holdings"]
        total += current_cash
        self.portfolio.loc[last_signal.name]["cash"] = current_cash
        self.portfolio.loc[last_signal.name]["total"] = total

        self.calc_portfolio_metrics()

    def calc_portfolio_metrics(self):
        if self.portfolio.shape[0] > 0:
            # self.calc_returns()

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
        # returns = self.portfolio['returns']
        returns = self.portfolio['total'].pct_change()

        # annualized Sharpe ratio
        sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())

        self.sharp_ratio = round(sharpe_ratio, 2)

    def calc_cagr(self):
        # Get the number of days in `aapl`
        days = (self.stock_data.index[-1] - self.stock_data.index[0]).days

        # Calculate the CAGR
        if days > 0:
            self.cagr = round((((self.portfolio['total'][-1] / self.portfolio['total'][0]) ** (365.0 / days)) - 1)*100, 2)
        else:
            self.cagr = 0


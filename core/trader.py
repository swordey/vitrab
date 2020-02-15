#! trader.py

#  Strategies
from core.strategies import buy_and_hold, sma, MACD, RSI, CCI, DEMA, PPO
from core.strategies import sma

# DataFetcher
from core.data.data_fetcher import DataFetcher


class Trader:
    def __init__(self):
        self.dataFetcher = DataFetcher()
        self.strategy = None
        self.benchmark_strategy = None

    def initialize(self, tickers, strategy_name, initial_capital, *args):
        if strategy_name == "Moving Average Crossover":
            self.strategy = sma.SMAStrategy(40, 100, tickers, float(initial_capital))
        elif strategy_name == "Buy and Hold":
            self.strategy = buy_and_hold.BuyAndHold(tickers, float(initial_capital))
        elif strategy_name == "MACD":
            self.strategy = MACD.MACDStrategy(tickers, float(initial_capital))
        elif strategy_name == "RSI":
            self.strategy = RSI.RSIStrategy(tickers, float(initial_capital))
        elif strategy_name == "CCI":
            self.strategy = CCI.CCIStrategy(tickers, float(initial_capital))
        elif strategy_name == "DEMA":
            self.strategy = DEMA.DEMAStrategy(tickers, float(initial_capital))
        elif strategy_name == "PPO":
            self.strategy = PPO.PPOStrategy(tickers, float(initial_capital))
        else:
            NotImplementedError("Strategy Not Implemented")

        self.benchmark_strategy = buy_and_hold.BuyAndHold(["^GSPC"], float(initial_capital))

        self.dataFetcher.initialize(tickers, *args)

    def init_plots(self, plot_area):
        self.strategy.init_plot(plot_area)

    def plot(self):
        self.strategy.plot()

    def run(self):
        curr_data, benchmark_data = self.dataFetcher.fetch_data()
        if curr_data is not None:
            self.strategy.handle_data(curr_data)
            self.benchmark_strategy.handle_data(benchmark_data)
        return curr_data

    def evaluate(self):
        self.strategy.evaluate_strategy()

    def get_signals(self):
        return self.strategy.signals

    def get_last_signal_by_ticker(self, ticker):
        return self.strategy.signals[ticker].iloc[-1]

    def get_portfolio_manager(self):
        return self.strategy.portfolio_manager

    def get_benchmark_portfolio_manager(self):
        return self.benchmark_strategy.portfolio_manager


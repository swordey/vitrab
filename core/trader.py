#! trader.py

#  Strategies
from core.strategies import buy_and_hold, sma, fourbarplay
from core.strategies import sma

# DataFetcher
from core.data.data_fetcher import DataFetcher


class Trader:
    def __init__(self):
        # self.plot_area = plot_area

        self.dataFetcher = DataFetcher()
        self.strategy = None

    def initialize(self, strategy_name, initial_capital, plot_area, *args):
        if strategy_name == "Moving Average Crossover":
            self.strategy = sma.SMA(40, 100, float(initial_capital))
        elif strategy_name == "Buy and Hold":
            self.strategy = buy_and_hold.BuyAndHold(float(initial_capital))
        elif strategy_name == "4 Bar Play":
            self.strategy = fourbarplay.FourBarPlay()
        else:
            NotImplementedError("Strategy Not Implemented")

        self.strategy.init_plot(plot_area)
        self.dataFetcher.initialize(*args)

    def plot(self):
        self.strategy.plot()

    def run(self):
        curr_data = self.dataFetcher.fetch_data()
        if curr_data is not None:
            self.strategy.handle_data(curr_data)

        return curr_data

    def evaluate(self):
        self.strategy.evaluate_strategy()

    def get_signals(self):
        return self.strategy.signals

    def get_last_signal(self):
        return self.strategy.signals.iloc[-1]

    def get_portfolio_manager(self):
        return self.strategy.portfolio_manager


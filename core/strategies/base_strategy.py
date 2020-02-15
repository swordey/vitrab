from abc import ABC, abstractmethod
import pandas as pd

from core.portfolio.manager import PortfolioManager


class BaseStrategy(ABC):
    def __init__(self, tickers, initial_capital, *args, **kwargs):
        super().__init__()
        self.initial_capital = initial_capital
        self.tickers = tickers
        self.i = 0
        self.signals = dict()

        self.portfolio_manager = PortfolioManager(tickers, initial_capital)

    @abstractmethod
    def init_signals(self):
        pass

    @abstractmethod
    def calc_signals(self, history):
        pass

    @abstractmethod
    def init_plot(self, plot_area):
        pass

    @abstractmethod
    def plot(self):
        pass

    @abstractmethod
    def reset_column_data_sources(self):
        pass

    def handle_data(self, history):
        self.i += 1
        self.calc_signals(history)
        self.portfolio_manager.update(self.signals, history)

    def evaluate_strategy(self):
        self.portfolio_manager.calc_portfolio_metrics()

    @staticmethod
    def convert_to_df(data):
        df = pd.DataFrame(data)
        df.set_index("Date", inplace=True)
        return df


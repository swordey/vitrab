from abc import ABC, abstractmethod
import pandas as pd

from core.portfolio.manager import PortfolioManager


class BaseStrategy(ABC):
    def __init__(self, initial_capital, *args, **kwargs):
        super().__init__()
        # self.plot_area = plot_area
        self.initial_capital = initial_capital
        self.i = 0
        self.signals = None

        self.portfolio_manager = PortfolioManager(initial_capital)

    @abstractmethod
    def init_signals(self):
        pass

    @abstractmethod
    def handle_data(self, history):
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

    def evaluate_strategy(self):
        self.portfolio_manager.calc_portfolio_metrics()

    # def __del__(self):
    #     self.reset_column_data_sources()

    @staticmethod
    def convert_to_df(data):
        df = pd.DataFrame(data)
        df.set_index("Date", inplace=True)
        return df
    #
    # def update_history(self, data):
    #     self.history[data.Index] =


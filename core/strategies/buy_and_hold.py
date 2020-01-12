#! buy_and_hold.py
# Buy and hold strategy
import pandas as pd

from core.strategies.base_strategy import BaseStrategy


class BuyAndHold(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def init_signals(self):
        for ticker in self.tickers:
            self.signals[ticker] = pd.DataFrame(dict(Date=[],
                                             signal=[],
                                             positions=[]))
            self.signals[ticker].set_index("Date", inplace=True)

    def calc_signals(self, history):
        for ticker in self.tickers:
            if self.i == 1:
                self.init_signals()
                signal = 0.0
                position = 0.0
            else:
                signal = 1.0
                position = signal - self.signals[ticker].iloc[-1].signal
            self.signals[ticker].loc[history.loc[ticker].iloc[-1].name] = [position, signal]

    def init_plot(self, plot_area):
        pass

    def plot(self):
        pass

    def reset_column_data_sources(self):
        pass

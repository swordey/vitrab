#! 4barplay.py
# Buy and hold strategy
import pandas as pd

from core.strategies.base_strategy import BaseStrategy


class FourBarPlay(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last4bars = None
        self.signals = None

    def init_signals(self):
        self.signals = pd.DataFrame(dict(Date=[],
                                         signal=[],
                                         positions=[]))
        self.signals.set_index("Date", inplace=True)

    def handle_data(self, history):
        self.i += 1
        if self.i == 1:
            self.init_signals()
            signal = 0.0
            position = 0.0
        else:
            signal = 1.0
            position = signal - self.signals.iloc[-1].signal

        self.signals.loc[history.iloc[-1].name] = [position, signal]

        self.portfolio_manager.update(self.signals, history)

    def init_plot(self, plot_area):
        pass

    def plot(self):
        pass

    def reset_column_data_sources(self):
        pass

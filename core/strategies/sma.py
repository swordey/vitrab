#! sma.py
# Simple Moving Average Crossover Strategy
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource

from core.strategies.base_strategy import BaseStrategy


class SMA(BaseStrategy):
    def __init__(self, short_window, long_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.short_window = short_window
        self.long_window = long_window

        self.signalsDataSource = ColumnDataSource()
        self.reset_column_data_sources()

    # Abstract methods
    def init_signals(self):
        self.signals = pd.DataFrame(dict(Date=[],
                                         signal=[],
                                         short_mavg=[],
                                         long_mavg=[],
                                         positions=[]))
        self.signals.set_index("Date", inplace=True)

    def handle_data(self, history):
        self.i += 1
        if self.i < self.short_window:
            return
        elif self.i == self.short_window:
            self.init_signals()

        short_mavg = history['Close'].iloc[-self.short_window:].mean()
        long_mavg = history['Close'].iloc[-self.long_window:].mean()
        signal = 1.0 if short_mavg > long_mavg else 0.0
        if self.signals.shape[0] > 0:
            position = signal - self.signals.iloc[-1].signal
        else:
            position = 0.0

        self.signals.loc[history.iloc[-1].name] = [long_mavg, position, short_mavg, signal]

        self.portfolio_manager.update(self.signals, history)

    def init_plot(self, plot_area):
        self.short_mavg = plot_area.select_one({'name': 'short_mavg'})
        if not self.short_mavg:
            self.short_mavg = plot_area.line(x='Date',
                            y='short_mavg',
                            source=self.signalsDataSource,
                            legend_label="Short Moving Average",
                            line_color="blue",
                            name="short_mavg")
        else:
            self.signalsDataSource = self.short_mavg.data_source

        self.long_mavg = plot_area.select_one({'name': 'long_mavg'})
        if not self.long_mavg:
            self.long_mavg = plot_area.line(x='Date',
                            y='long_mavg',
                            source=self.signalsDataSource,
                            legend_label="Long Moving Average",
                            line_color="green",
                            name="long_mavg")

    def plot(self):
        if self.signals is None:
            return

        signal_data = dict(
            Date=[self.signals.iloc[-1].name],
            short_mavg=[self.signals.iloc[-1].short_mavg],
            long_mavg=[self.signals.iloc[-1].long_mavg]
        )
        self.signalsDataSource.stream(signal_data)

    def __del__(self):
        # del self.long_mavg
        self.signalsDataSource.data = dict(Date=[], short_mavg=[], long_mavg=[])

    def reset_column_data_sources(self):
        self.signalsDataSource.data = dict(Date=[], short_mavg=[], long_mavg=[])

    def handle_data_old(self, history):
        self.i += 1
        # Skip dates when average can't be calculated
        if self.i < self.short_window:
            return

        # Create a dataframe from incoming data
        # df = self.convert_to_df(data)
        df = history

        # Initialize the `signals` DataFrame with the `signal` column
        self.signals = pd.DataFrame(index=df.index)
        self.signals['signal'] = 0.0

        # Create short simple moving average over the short window
        self.signals['short_mavg'] = df['Close'].rolling(window=self.short_window, min_periods=1, center=False).mean()

        # Create long simple moving average over the long window
        self.signals['long_mavg'] = df['Close'].rolling(window=self.long_window, min_periods=1, center=False).mean()

        # Create signals
        self.signals['signal'][self.short_window:] = \
            np.where(self.signals['short_mavg'][self.short_window:] > \
                     self.signals['long_mavg'][self.short_window:], 1.0, 0.0)

        self.signals['positions'] = self.signals['signal'].diff()


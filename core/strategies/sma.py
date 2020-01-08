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

        self.signalsDataSource = {}
        for ticker in self.tickers:
            self.signalsDataSource[ticker] = ColumnDataSource()
        self.reset_column_data_sources()

    # Abstract methods
    def init_signals(self):
        for ticker in self.tickers:
            self.signals[ticker] = pd.DataFrame(dict(Date=[],
                                             signal=[],
                                             short_mavg=[],
                                             long_mavg=[],
                                             positions=[]))
            self.signals[ticker].set_index("Date", inplace=True)

    def calc_signals(self, history):
        if self.i < self.short_window:
            return False
        elif self.i == self.short_window:
            self.init_signals()

        for ticker in self.tickers:
            short_mavg = history.loc[ticker]['Close'].iloc[-self.short_window:].mean()
            long_mavg = history.loc[ticker]['Close'].iloc[-self.long_window:].mean()
            signal = 1.0 if short_mavg > long_mavg else 0.0
            if self.signals[ticker].shape[0] > 0:
                position = signal - self.signals[ticker].iloc[-1].signal
            else:
                position = 0.0
            self.signals[ticker].loc[history.loc[ticker].iloc[-1].name] = [long_mavg, position, short_mavg, signal]
        return True

    def init_plot(self, plot_area):
        for ticker in self.tickers:
            self.short_mavg = plot_area.select_one({'name': ticker+'_short_mavg'})
            if not self.short_mavg:
                self.short_mavg = plot_area.line(x='Date',
                                                 y='short_mavg',
                                                 source=self.signalsDataSource[ticker],
                                                 legend_label=ticker + " Short Moving Average",
                                                 line_color="blue",
                                                 name=ticker+'_short_mavg')
            else:
                self.signalsDataSource[ticker] = self.short_mavg.data_source

            self.long_mavg = plot_area.select_one({'name': ticker+'_long_mavg'})
            if not self.long_mavg:
                self.long_mavg = plot_area.line(x='Date',
                                                y='long_mavg',
                                                source=self.signalsDataSource[ticker],
                                                legend_label=ticker + " Long Moving Average",
                                                line_color="green",
                                                name=ticker+'_long_mavg')

    def plot(self):
        for ticker in self.tickers:
            if ticker not in self.signals:
                continue
            signal_data = dict(
                Date=[self.signals[ticker].iloc[-1].name],
                short_mavg=[self.signals[ticker].iloc[-1].short_mavg],
                long_mavg=[self.signals[ticker].iloc[-1].long_mavg]
            )
            self.signalsDataSource[ticker].stream(signal_data)

    def __del__(self):
        # del self.long_mavg
        self.reset_column_data_sources()

    def reset_column_data_sources(self):
        for ticker in self.tickers:
            self.signalsDataSource[ticker].data = dict(Date=[], short_mavg=[], long_mavg=[])

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


#! sma.py
# Simple Moving Average Crossover Strategy
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource

from core.strategies.base_strategy import BaseStrategy
from core.strategies.indicators.SMA import SMA


class SMAStrategy(BaseStrategy):
    def __init__(self, short_window, long_window, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.short_sma = SMA(short_window)
        self.long_sma = SMA(long_window)

        self.signalsDataSource = {}
        for ticker in self.tickers:
            self.signalsDataSource[ticker] = ColumnDataSource()
        self.reset_column_data_sources()

        self.init_signals()

    # Abstract methods
    def init_signals(self):
        for ticker in self.tickers:
            self.signals[ticker] = pd.DataFrame(dict(Date=[],
                                             signal=[],
                                             short_sma=[],
                                             long_sma=[],
                                             positions=[]))
            self.signals[ticker].set_index("Date", inplace=True)

    def calc_signals(self, history):
        for ticker in self.tickers:
            self.short_sma.update(history.loc[ticker]['Close'].iloc[-1])
            self.long_sma.update(history.loc[ticker]['Close'].iloc[-1])

            signal = 1.0 if self.short_sma.result > self.long_sma.result else 0.0
            if self.signals[ticker].shape[0] > 0:
                position = signal - self.signals[ticker].iloc[-1].signal
            else:
                position = 0.0
            self.signals[ticker].loc[history.loc[ticker].iloc[-1].name] = [self.long_sma.result, position, self.short_sma.result, signal]

    def init_plot(self, plot_area):
        for ticker in self.tickers:
            self.short_mavg = plot_area.select_one({'name': ticker+'_short_sma'})
            if not self.short_mavg:
                self.short_mavg = plot_area.line(x='Date',
                                                 y='short_sma',
                                                 source=self.signalsDataSource[ticker],
                                                 legend_label=ticker + " Short Moving Average",
                                                 line_color="blue",
                                                 name=ticker+'_short_sma')
            else:
                self.signalsDataSource[ticker] = self.short_mavg.data_source

            self.long_mavg = plot_area.select_one({'name': ticker+'_long_sma'})
            if not self.long_mavg:
                self.long_mavg = plot_area.line(x='Date',
                                                y='long_sma',
                                                source=self.signalsDataSource[ticker],
                                                legend_label=ticker + " Long Moving Average",
                                                line_color="green",
                                                name=ticker+'_long_sma')

    def plot(self):
        for ticker in self.tickers:
            if ticker not in self.signals:
                continue
            signal_data = dict(
                Date=[self.signals[ticker].iloc[-1].name],
                short_sma=[self.signals[ticker].iloc[-1].short_sma],
                long_sma=[self.signals[ticker].iloc[-1].long_sma]
            )
            self.signalsDataSource[ticker].stream(signal_data)

    def __del__(self):
        # del self.long_mavg
        self.reset_column_data_sources()

    def reset_column_data_sources(self):
        for ticker in self.tickers:
            self.signalsDataSource[ticker].data = dict(Date=[], short_sma=[], long_sma=[])


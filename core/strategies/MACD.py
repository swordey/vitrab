#! MACD.py
# Moving Average Convergence Divergence Strategy
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource

from core.strategies.indicators.MACD import MACD
from core.strategies.base_strategy import BaseStrategy


class MACDConfig:
    def __init__(self):
        self.up = 0.25
        self.down = -0.25
        self.persistence = 5


class MACDTrend:
    def __init__(self, direction=None):
        self.direction = direction
        self.duration = 0
        self.persisted = False
        self.adviced = False


class MACDStrategy(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.short_window = 12
        self.long_window = 26

        self.macd = MACD(12, 26, 9)

        self.trend = MACDTrend()
        self.thresholds = MACDConfig()

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
                                             EMA_12d=[],
                                             EMA_26d=[],
                                             MACD=[],
                                             positions=[]))
            self.signals[ticker].set_index("Date", inplace=True)

    def calc_signals(self, history):
        for ticker in self.tickers:
            self.macd.update(history.loc[ticker]['Close'].iloc[-1])

            if self.macd.result > self.thresholds.up:
                if self.trend.direction != "up":
                    self.trend = MACDTrend("up")

                self.trend.duration += 1

                if self.trend.duration > self.thresholds.persistence:
                    self.trend.persisted = True

                if self.trend.persisted and not self.trend.adviced:
                    self.trend.adviced = True
                    signal = 1.0
                    position = 1.0
                else:
                    signal = 1.0
                    position = 0.0
            elif self.macd.result < self.thresholds.down:
                if self.trend.direction != "down":
                    self.trend = MACDTrend("down")

                self.trend.duration += 1

                if self.trend.duration > self.thresholds.persistence:
                    self.trend.persisted = True

                if self.trend.persisted and not self.trend.adviced:
                    self.trend.adviced = True
                    signal = 0.0
                    position = -1.0
                else:
                    signal = 0.0
                    position = 0.0
            else:
                signal = 0.0
                position = 0.0

            self.signals[ticker].loc[history.loc[ticker].iloc[-1].name] = 0
            self.signals[ticker]["signal"] = signal
            self.signals[ticker]["EMA_12d"] = self.macd.short.result
            self.signals[ticker]["EMA_26d"] = self.macd.long.result
            self.signals[ticker]["MACD"] = self.macd.result
            self.signals[ticker]["positions"] = position

    def init_plot(self, plot_area):
        for ticker in self.tickers:
            self.ema_12d = plot_area.select_one({'name': ticker + '_ema_12d'})
            if not self.ema_12d:
                self.ema_12d = plot_area.line(x='Date',
                                              y='EMA_12d',
                                              source=self.signalsDataSource[ticker],
                                              legend_label=ticker + " EMA 12 day",
                                              line_color="blue",
                                              name=ticker+'_ema_12d')
            else:
                self.signalsDataSource[ticker] = self.ema_12d.data_source

            self.ema_26d = plot_area.select_one({'name': ticker + '_ema_26d'})
            if not self.ema_26d:
                self.ema_26d = plot_area.line(x='Date',
                                              y='EMA_26d',
                                              source=self.signalsDataSource[ticker],
                                              legend_label=ticker + " EMA 26 day",
                                              line_color="green",
                                              name=ticker+'_ema_26d')

    def plot(self):
        for ticker in self.tickers:
            if ticker not in self.signals:
                continue
            signal_data = dict(
                Date=[self.signals[ticker].iloc[-1].name],
                signal=[self.signals[ticker].iloc[-1].signal],
                EMA_12d=[self.signals[ticker].iloc[-1].EMA_12d],
                EMA_26d=[self.signals[ticker].iloc[-1].EMA_26d],
                MACD=[self.signals[ticker].iloc[-1].MACD],
                positions=[self.signals[ticker].iloc[-1].positions]
            )
            self.signalsDataSource[ticker].stream(signal_data)

    def __del__(self):
        self.reset_column_data_sources()

    def reset_column_data_sources(self):
        for ticker in self.tickers:
            self.signalsDataSource[ticker].data = dict(Date=[],
                                                       signal=[],
                                                       EMA_12d=[],
                                                       EMA_26d=[],
                                                       MACD=[],
                                                       positions=[])


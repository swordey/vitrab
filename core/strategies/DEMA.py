#! DEMA.py
# Double Exponential Moving Average Strategy
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource

from core.strategies.indicators.DEMA import DEMA
from core.strategies.indicators.SMA import SMA
from core.strategies.base_strategy import BaseStrategy


class DEMAConfig:
    def __init__(self):
        self.weight = 21
        self.down = -0.025
        self.up = 0.025


class DEMATrend:
    def __init__(self, direction=None):
        self.direction = direction
        self.duration = 0
        self.persisted = False
        self.adviced = False


class DEMAStrategy(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentTrend = None

        self.age = 0
        self.trend = DEMATrend("undefined")
        self.config = DEMAConfig()

        self.dema = DEMA(self.config.weight)
        self.sma = SMA(self.config.weight)

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
                                                     DEMA=[],
                                                     SMA=[],
                                                     positions=[]))
            self.signals[ticker].set_index("Date", inplace=True)

    def calc_signals(self, history):
        for ticker in self.tickers:
            self.dema.update(history.loc[ticker]["Close"].iloc[-1])
            self.sma.update(history.loc[ticker]["Close"].iloc[-1])
            signal = 0
            position = 0

            resDEMA = self.dema.result
            resSMA = self.sma.result
            price = history.loc[ticker]["Close"].iloc[-1]
            diff = resSMA - resDEMA

            if diff > self.config.up:
                if self.currentTrend is not 'up':
                    self.currentTrend = 'up'
                    position = 1
                    signal = 1
                else:
                    position = 0
                    signal = 0

            elif diff < self.config.down:
                if self.currentTrend is not 'down':
                    self.currentTrend = 'down'
                    position = -1
                    signal = 0
                else:
                    position = 0
                    signal = 0
            else:
                position = 0
                signal = 0

            self.signals[ticker].loc[history.loc[ticker].iloc[-1].name] = 0
            self.signals[ticker]["signal"] = signal
            self.signals[ticker]["DEMA"] = self.dema.result
            self.signals[ticker]["SMA"] = self.sma.result
            self.signals[ticker]["positions"] = position

    def init_plot(self, plot_area):
        for ticker in self.tickers:
            self.sma_visu = plot_area.select_one({'name': ticker + '_sma'})
            if not self.sma_visu:
                self.sma_visu = plot_area.line(x='Date',
                                               y='SMA',
                                               source=self.signalsDataSource[ticker],
                                               legend_label=ticker + " SMA",
                                               line_color="blue",
                                               name=ticker+'_sma')
            else:
                self.signalsDataSource[ticker] = self.sma_visu.data_source

            self.dema_visu = plot_area.select_one({'name': ticker + '_dema'})
            if not self.dema_visu:
                self.dema_visu = plot_area.line(x='Date',
                                                y='DEMA',
                                                source=self.signalsDataSource[ticker],
                                                legend_label=ticker + " DEMA",
                                                line_color="green",
                                                name=ticker+'_dema')

    def plot(self):
        for ticker in self.tickers:
            if ticker not in self.signals:
                continue
            signal_data = dict(
                Date=[self.signals[ticker].iloc[-1].name],
                signal=[self.signals[ticker].iloc[-1].signal],
                SMA=[self.signals[ticker].iloc[-1].SMA],
                DEMA=[self.signals[ticker].iloc[-1].DEMA],
                positions=[self.signals[ticker].iloc[-1].positions]
            )
            self.signalsDataSource[ticker].stream(signal_data)

    def __del__(self):
        self.reset_column_data_sources()

    def reset_column_data_sources(self):
        for ticker in self.tickers:
            self.signalsDataSource[ticker].data = dict(Date=[],
                                                       signal=[],
                                                       SMA=[],
                                                       DEMA=[],
                                                       positions=[])


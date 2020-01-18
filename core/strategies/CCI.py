#! CCI.py
# Commodity Channel Index Strategy
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource

from core.strategies.indicators.CCI import CCI
from core.strategies.base_strategy import BaseStrategy


class CCIConfig:
    def __init__(self):
        self.constant = 0.015
        self.history = 90
        self.uplevel = 100
        self.downlevel = -100
        self.persisted = 0


class CCITrend:
    def __init__(self, direction=None):
        self.direction = direction
        self.duration = 0
        self.persisted = False
        self.adviced = False


class CCIStrategy(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentTrend = None

        self.age = 0
        self.trend = CCITrend("undefined")
        self.config = CCIConfig()
        self.ppoadv = 'none'

        self.cci = CCI(self.config.constant, self.config.history)

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
                                             CCI=[],
                                             positions=[]))
            self.signals[ticker].set_index("Date", inplace=True)

    def calc_signals(self, history):
        for ticker in self.tickers:
            self.cci.update(history.loc[ticker].iloc[-1])

            lastPrice = history.loc[ticker]["Close"].iloc[-1]
            self.age += 1
            signal = 0
            position = 0
            if self.cci.result is not None:
                if self.cci.result >= self.config.uplevel and \
                   (self.trend.persisted or self.config.persisted == 0) and \
                   not self.trend.adviced and self.trend.direction is "overbought":
                    self.trend.adviced = True
                    self.trend.duration += 1
                    signal = 0
                    position = -1
                    # self.advice('short');
                elif self.cci.result >= self.config.uplevel and self.trend.direction != 'overbought':
                    self.trend.duration = 1
                    self.trend.direction = 'overbought'
                    self.trend.persisted = False
                    self.trend.adviced = False
                    if self.config.persisted == 0:
                        self.trend.adviced = True
                        signal = 0
                        position = -1
                        # self.advice('short')
                elif self.cci.result >= self.config.uplevel:
                    self.trend.duration += 1
                    if self.trend.duration >= self.config.persisted:
                        self.trend.persisted = True

                elif self.cci.result <= self.config.downlevel and \
                    (self.trend.persisted or self.config.persisted == 0) and \
                    not self.trend.adviced and self.trend.direction == 'oversold':
                    self.trend.adviced = True
                    self.trend.duration += 1
                    signal = 1
                    position = 1
                    # self.advice('long');
                elif self.cci.result <= self.config.downlevel and self.trend.direction != 'oversold':
                    self.trend.duration = 1
                    self.trend.direction = 'oversold'
                    self.trend.persisted = False
                    self.trend.adviced = False
                    if self.config.persisted == 0:
                        self.trend.adviced = True
                        signal = 1
                        position = 1
                        # this.advice('long');
                elif self.cci.result <= self.config.downlevel:
                    self.trend.duration += 1
                    if self.trend.duration >= self.config.persisted:
                        self.trend.persisted = True
                    else:
                        if self.trend.direction != 'nodirection':
                            self.trend = CCITrend("nodirection")
                        else:
                            self.trend.duration += 1
                        # this.advice()
                        signal = 0
                        position = 0
            else:
                signal = 0
                position = 0

            self.signals[ticker].loc[history.loc[ticker].iloc[-1].name] = 0
            self.signals[ticker]["signal"] = signal
            self.signals[ticker]["CCI"] = self.cci.result
            self.signals[ticker]["positions"] = position

    def init_plot(self, plot_area):
        for ticker in self.tickers:
            self.cci_visu = plot_area.select_one({'name': ticker + '_cci'})
            if not self.cci_visu:
                self.cci_visu = plot_area.line(x='Date',
                                              y='CCI',
                                              source=self.signalsDataSource[ticker],
                                              legend_label=ticker + " CCI",
                                              line_color="blue",
                                              name=ticker+'_cci')
            else:
                self.signalsDataSource[ticker] = self.cci_visu.data_source

    def plot(self):
        for ticker in self.tickers:
            if ticker not in self.signals:
                continue
            signal_data = dict(
                Date=[self.signals[ticker].iloc[-1].name],
                signal=[self.signals[ticker].iloc[-1].signal],
                CCI=[self.signals[ticker].iloc[-1].CCI],
                positions=[self.signals[ticker].iloc[-1].positions]
            )
            self.signalsDataSource[ticker].stream(signal_data)

    def __del__(self):
        self.reset_column_data_sources()

    def reset_column_data_sources(self):
        for ticker in self.tickers:
            self.signalsDataSource[ticker].data = dict(Date=[],
                                                       signal=[],
                                                       CCI=[],
                                                       positions=[])


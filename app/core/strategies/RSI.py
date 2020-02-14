#! RSI.py
# Relative Strength Index
import pandas as pd
from bokeh.models import ColumnDataSource

from core.strategies.indicators.RSI import RSI
from core.strategies.base_strategy import BaseStrategy


class Config:
    def __init__(self):
        self.high = 70
        self.low = 40
        self.persistence = 5


class Trend:
    def __init__(self, direction=None):
        self.direction = direction
        self.duration = 0
        self.persisted = False
        self.adviced = False


class RSIStrategy(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.trend = Trend()
        self.requiredHistory = 10
        self.rsi = RSI(14)

        self.config = Config()

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
                                             RSI=[],
                                             positions=[]))
            self.signals[ticker].set_index("Date", inplace=True)

    def calc_signals(self, history):
        for ticker in self.tickers:
            self.rsi.update(history.loc[ticker]['Close'].iloc[-1])
            rsiVal = self.rsi.result

            if rsiVal > self.config.high:
                # new trend detected
                if self.trend.direction != 'high':
                    self.trend = Trend("high")

                self.trend.duration += 1

                if self.trend.duration >= self.config.persistence:
                    self.trend.persisted = True

                if self.trend.persisted and not self.trend.adviced:
                    self.trend.adviced = True
                    signal = 0
                    position = -1
                else:
                    signal = 0
                    position = 0

            elif rsiVal < self.config.low:
                # new trend detected
                if self.trend.direction != 'low':
                    self.trend = Trend("low")

                self.trend.duration += 1

                if self.trend.duration >= self.config.persistence:
                    self.trend.persisted = True

                if self.trend.persisted and not self.trend.adviced:
                    self.trend.adviced = True
                    signal = 1
                    position = 1
                else:
                    signal = 1
                    position = 0

            else:
                signal = 0
                position = 0

            if self.rsi.result != 0:
                self.signals[ticker].loc[history.loc[ticker].iloc[-1].name] = 0
                self.signals[ticker]["signal"] = signal
                self.signals[ticker]["RSI"] = self.rsi.result
                self.signals[ticker]["positions"] = position

    def init_plot(self, plot_area):
        for ticker in self.tickers:
            self.rsi_plot = plot_area.select_one({'name': ticker + '_rsi'})
            if not self.rsi_plot:
                self.rsi_plot = plot_area.line(x='Date',
                                              y='RSI',
                                              source=self.signalsDataSource[ticker],
                                              legend_label=ticker + " RSI",
                                              line_color="blue",
                                              name=ticker+'_rsi')
            else:
                self.signalsDataSource[ticker] = self.rsi_plot.data_source

    def plot(self):
        for ticker in self.tickers:
            if ticker not in self.signals or self.signals[ticker].shape[0] == 0:
                continue
            signal_data = dict(
                Date=[self.signals[ticker].iloc[-1].name],
                signal=[self.signals[ticker].iloc[-1].signal],
                RSI=[self.signals[ticker].iloc[-1].RSI],
                positions=[self.signals[ticker].iloc[-1].positions]
            )
            self.signalsDataSource[ticker].stream(signal_data)

    def __del__(self):
        self.reset_column_data_sources()

    def reset_column_data_sources(self):
        for ticker in self.tickers:
            self.signalsDataSource[ticker].data = dict(Date=[],
                                                       signal=[],
                                                       RSI=[],
                                                       positions=[])


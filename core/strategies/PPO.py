#! PPO.py
# Percentage Price Oscillator Strategy
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource

from core.strategies.indicators.PPO import PPO
from core.strategies.base_strategy import BaseStrategy


class PPOConfig:
    def __init__(self):
        self.short = 12
        self.long = 26
        self.signal = 9
        self.down = -0.025
        self.up = 0.025
        self.persistence = 2


class PPOTrend:
    def __init__(self, direction=None):
        self.direction = direction
        self.duration = 0
        self.persisted = False
        self.adviced = False


class PPOStrategy(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentTrend = None

        self.age = 0
        self.trend = PPOTrend("none")
        self.config = PPOConfig()

        self.ppo = PPO(self.config.short, self.config.long, self.config.signal)

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
                                                     PPOhist=[],
                                                     positions=[]))
            self.signals[ticker].set_index("Date", inplace=True)

    def calc_signals(self, history):
        for ticker in self.tickers:
            self.ppo.update(history.loc[ticker]["Close"].iloc[-1])
            signal = 0
            position = 0

            ppoHist = self.ppo.result["PPOhist"]

            if ppoHist > self.config.up:
                # new trend detected
                if self.trend.direction is not 'up':
                    self.trend = PPOTrend("up")

                self.trend.duration += 1

                if self.trend.duration >= self.config.persistence:
                    self.trend.persisted = True

                if self.trend.persisted and not self.trend.adviced:
                    self.trend.adviced = True
                    position = 1
                    signal = 1
                else:
                    position = 0
                    signal = 0

            elif ppoHist < self.config.down:
                # new trend detected
                if self.trend.direction is not 'down':
                    self.trend = PPOTrend("down")

                self.trend.duration += 1

                if self.trend.duration >= self.config.persistence:
                    self.trend.persisted = True

                if self.trend.persisted and not self.trend.adviced:
                    self.trend.adviced = True
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
            self.signals[ticker]["PPOhist"] = self.ppo.result["PPOhist"]
            self.signals[ticker]["positions"] = position

    def init_plot(self, plot_area):
        for ticker in self.tickers:
            self.ppo_visu = plot_area.select_one({'name': ticker + '_ppo'})
            if not self.ppo_visu:
                self.ppo_visu = plot_area.line(x='Date',
                                               y='PPOhist',
                                               source=self.signalsDataSource[ticker],
                                               legend_label=ticker + " PPO hist",
                                               line_color="blue",
                                               name=ticker+'_ppo')
            else:
                self.signalsDataSource[ticker] = self.ppo_visu.data_source

    def plot(self):
        for ticker in self.tickers:
            if ticker not in self.signals:
                continue
            signal_data = dict(
                Date=[self.signals[ticker].iloc[-1].name],
                signal=[self.signals[ticker].iloc[-1].signal],
                PPOhist=[self.signals[ticker].iloc[-1].PPOhist],
                positions=[self.signals[ticker].iloc[-1].positions]
            )
            self.signalsDataSource[ticker].stream(signal_data)

    def __del__(self):
        self.reset_column_data_sources()

    def reset_column_data_sources(self):
        for ticker in self.tickers:
            self.signalsDataSource[ticker].data = dict(Date=[],
                                                       signal=[],
                                                       PPOhist=[],
                                                       positions=[])


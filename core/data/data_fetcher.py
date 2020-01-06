#! data_fetcher.py
import pandas_datareader as pdr


class DataFetcher:
    def __init__(self):
        self.history = None
        self.ticker = None

        # params for historical data playback
        self.startDate = None
        self.endDate = None

        self.idx = -1

    def initialize(self, ticker, start=None, end=None):
        self.ticker = ticker
        self.startDate = start
        self.endDate = end

        self.idx = 0

        if start and end:
            self.download_data()
        else:
            self.history = None

    def download_data(self):
        self.history = pdr.get_data_yahoo(self.ticker,
                                          start=self.startDate,
                                          end=self.endDate)

    def all_historical_data_used(self):
        return self.history.shape[0] < self.idx

    def fetch_data(self):
        if self.history is not None:  # we work with historical data
            self.idx += 1
            if self.all_historical_data_used():
                return None
            return self.history.iloc[:self.idx]
        else:
            pass


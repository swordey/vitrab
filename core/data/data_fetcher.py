#! data_fetcher.py
import pandas_datareader as pdr
import pandas as pd


class DataFetcher:
    def __init__(self):
        self.history = None
        self.benchmark_tickers = ["^GSPC"]  # S&P-500
        self.benchmark_name = "S&P 500"
        self.benchmark = None
        self.tickers = None

        # params for historical data playback
        self.startDate = None
        self.endDate = None

        self.idx = -1

    def initialize(self, tickers, start=None, end=None):
        if type(tickers) is list:
            self.tickers = tickers
        else:
            self.tickers = [tickers]
        self.startDate = start
        self.endDate = end
        self.idx = 0

        if start and end:
            self.download_data()
            self.download_benchmark()
        else:
            self.history = None

    @staticmethod
    def get(tickers, startdate, enddate):
        def data(ticker):
            return (pdr.get_data_yahoo(ticker, start=startdate, end=enddate))

        datas = map(data, tickers)
        df = pd.concat(datas, keys=tickers, names=['Ticker', 'Date'])
        return df

    def download_benchmark(self):
        self.benchmark = self.get(self.benchmark_tickers, self.startDate, self.endDate)

    def download_data(self):
        self.history = self.get(self.tickers, self.startDate, self.endDate)

    def all_historical_data_used(self):
        return self.history.shape[0] < self.idx

    def fetch_data(self):
        if self.history is not None:  # we work with historical data
            self.idx += 1
            if self.all_historical_data_used():
                return None, None

            h_df = pd.concat([self.history.loc[ticker][:self.idx] for ticker in self.tickers],
                            keys=self.tickers,
                            names=['Ticker', 'Date'])
            b_df = pd.concat([self.benchmark.loc[ticker][:self.idx] for ticker in self.benchmark_tickers],
                            keys=self.benchmark_tickers,
                            names=['Ticker', 'Date'])
            return h_df, b_df
        else:
            pass


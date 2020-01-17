from core.strategies.indicators.SMA import SMA


class UO:
    def __init__(self, weight1, weight2, weight3, period1, period2, period3):
        self.lastClose = 0
        self.uo = 0
        self.firstWeight = weight1
        self.secondWeight = weight2
        self.thirdWeight = weight3
        self.firstLow = SMA(period1)
        self.firstHigh = SMA(period1)
        self.secondLow = SMA(period2)
        self.secondHigh = SMA(period2)
        self.thirdLow = SMA(period3)
        self.thirdHigh = SMA(period3)

    def update(self, candle):
        close = candle.close
        prevClose = self.lastClose
        low = candle.low
        high = candle.high

        bp = close - min(low, prevClose)
        tr = max(high, prevClose) - min(low, prevClose)

        self.firstLow.update(tr)
        self.secondLow.update(tr)
        self.thirdLow.update(tr)

        self.firstHigh.update(bp)
        self.secondHigh.update(bp)
        self.thirdHigh.update(bp)

        first = self.firstHigh.result / self.firstLow.result
        second = self.secondHigh.result / self.secondLow.result
        third = self.thirdHigh.result / self.thirdLow.result

        self.uo = 100 * (self.firstWeight * first + self.secondWeight * second + self.thirdWeight * third) / (
                         self.firstWeight + self.secondWeight + self.thirdWeight)

        self.lastClose = close

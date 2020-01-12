from core.strategies.indicators import EMA


class MACD:
    def __init__(self, short, long, signal):
        self.diff = None
        self.result = None
        self.short = EMA.EMA(short)
        self.long = EMA.EMA(long)
        self.signal = EMA.EMA(signal)

    def update(self, price):
        self.short.update(price)
        self.long.update(price)
        self.calcEMAdiff()
        self.signal.update(self.diff)
        self.result = self.diff - self.signal.result
        return self.result

    def calcEMAdiff(self):
        self.diff = self.short.result - self.long.result


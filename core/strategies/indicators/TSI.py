from core.strategies.indicators.EMA import EMA


class TSI:
    def __init__(self, short, long):
        self.lastClose = None
        self.tsi = 0
        self.inner = EMA(long)
        self.outer = EMA(short)
        self.absoluteInner = EMA(long)
        self.absoluteOuter = EMA(short)

    def update(self, price):
        close = price
        prevClose = self.lastClose

        if prevClose is None:
            # Set initial price to prevent invalid change calculation
            self.lastClose = close
            # Do not calculate TSI on first close
            return

        momentum = close - prevClose

        self.inner.update(momentum)
        self.outer.update(self.inner.result)

        self.absoluteInner.update(abs(momentum))
        self.absoluteOuter.update(self.absoluteInner.result)

        self.tsi = 100 * self.outer.result / self.absoluteOuter.result

        self.lastClose = close

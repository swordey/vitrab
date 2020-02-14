from core.strategies.indicators.EMA import EMA


class DEMA:
    def __init__(self, weight):
        self.result = False
        self.inner = EMA(weight)
        self.outer = EMA(weight)

    def update(self, price):
        self.inner.update(price)
        self.outer.update(self.inner.result)
        self.result = 2 * self.inner.result - self.outer.result

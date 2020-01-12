from core.strategies.indicators.SMA import SMA


class SMMA:
    def __init__(self, weight):
        self.sma = SMA(weight)
        self.weight = weight
        self.prices = {}
        self.result = 0
        self.age = 0

    def update(self, price):
        self.prices[self.age] = price

        if len(self.prices) < self.weight:
            self.sma.update(price)
        elif len(self.prices) == self.weight:
            self.sma.update(price)
            self.result = self.sma.result
        else:
            self.result = (self.result * (self.weight - 1) + price) / self.weight

        self.age += 1


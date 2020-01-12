from core.strategies.indicators.SMMA import SMMA


class RSI:
    def __init__(self, interval):
        self.lastClose = None
        self.weight = interval
        self.avgU = SMMA(self.weight)
        self.avgD = SMMA(self.weight)
        self.u = 0
        self.d = 0
        self.rs = 0
        self.result = 0
        self.age = 0

    def update(self, price):
        currentClose = price

        if self.lastClose is None:
            # Set initial price to prevent invalid change calculation
            self.lastClose = currentClose

            # Do not calculate RSI for this reason - there's no change!
            self.age += 1
            return
        if currentClose > self.lastClose:
            self.u = currentClose - self.lastClose
            self.d = 0

        else:
            self.u = 0
            self.d = self.lastClose - currentClose

        self.avgU.update(self.u)
        self.avgD.update(self.d)
        if self.age >= self.weight:
            self.rs = self.avgU.result / self.avgD.result
            self.result = 100 - (100 / (1 + self.rs))

            if self.avgD.result == 0 and self.avgU.result != 0:
                self.result = 100
            elif self.avgD.result == 0:
                self.result = 0

        self.lastClose = currentClose
        self.age += 1


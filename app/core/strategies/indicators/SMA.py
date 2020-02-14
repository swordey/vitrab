class SMA:
    def __init__(self, windowLength):
        self.windowLength = windowLength
        self.prices = {}
        self.result = None
        self.age = 0
        self.sum = 0
        pass

    def update(self, price):
        if self.age in self.prices:
            tail = self.prices[self.age]
        else:
            tail = 0
        self.prices[self.age] = price
        self.sum += price - tail
        self.result = self.sum / len(self.prices)
        self.age = (self.age + 1) % self.windowLength


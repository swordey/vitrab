class EMA:
    def __init__(self, weight):
        self.weight = weight
        self.result = None

    def update(self, price):
        if self.result is None:
            self.result = price

        self.calculate(price)

        return self.result

    def calculate(self, price):
        k = 2 / ( self.weight + 1)
        y = self.result
        self.result = price * k + y * (1-k)


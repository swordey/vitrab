class CCI:
    def __init__(self, constant, history):
        self.tp = 0.0
        self.result = None
        self.maxSize = history
        self.hist = [0.0] * self.maxSize
        self.mean = 0.0
        self.size = 0
        self.constant = constant

    def update(self, candle):
        tp = (candle.High + candle.Close + candle.Low) / 3
        if self.size < self.maxSize:
            self.hist[self.size] = tp
            self.size += 1
        else:
            for i in range(self.maxSize - 1):
                self.hist[i] = self.hist[i+1]
            self.hist[self.maxSize-1] = tp

        if self.size < self.maxSize:
            self.result = False
        else:
            self.calculate(tp)

    def calculate(self, tp):
        sumtp = 0.0

        for i in range(self.size):
            sumtp = sumtp + self.hist[i]

        self.avgtp = sumtp / self.size

        self.tp = tp

        sum = 0.0
        for i in range(self.size):
            z = (self.hist[i] - self.avgtp)
            if z < 0:
                z = z * -1.0
            sum = sum + z

        self.mean = (sum / self.size)

        self.result = (self.tp - self.avgtp) / (self.constant * self.mean)


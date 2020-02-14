class LRC:
    def __init__(self, depth):
        self.depth = depth
        self.result = False
        self.age = 0
        self.history = [0.0] * self.depth
        self.x = list(range(self.depth))

    def update(self, price):
        if self.result is False and self.age < self.depth:
            self.history[self.age] = price
            self.age += 1
            self.result = False
            return

        self.age += 1
        for i in range(self.depth - 1):
            self.history[i] = self.history[i + 1]

        self.history[self.depth - 1] = price

        self.calculate()

    def calculate(self):
        reg = self.linreg(self.x, self.history)

        self.result = ((self.depth - 1) * reg[0]) + reg[1]

    def linreg(self, values_x, values_y):
        sum_x = 0
        sum_y = 0
        sum_xy = 0
        sum_xx = 0
        count = 0
        values_length = len(values_x)

        if values_length != len(values_y):
            Exception('The parameters values_x and values_y need to have same size!')

        if values_length == 0:
            return [[], []]

        for v in range(values_length):
            x = values_x[v]
            y = values_y[v]
            sum_x += x
            sum_y += y
            sum_xx += x * x
            sum_xy += x * y
            count += 1

        m = (count * sum_xy - sum_x * sum_y) / (count * sum_xx - sum_x * sum_x)
        b = (sum_y / count) - (m * sum_x) / count

        return [m, b]

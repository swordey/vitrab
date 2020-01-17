from core.strategies.indicators.EMA import EMA


class PPO:
    def __init__(self, short, long, signal):
        self.result = {}
        self.input = 'price'
        self.macd = 0
        self.ppo = 0
        self.short = EMA(short)
        self.long = EMA(long)
        self.MACDsignal = EMA(signal)
        self.PPOsignal = EMA(signal)

    def update(self, price):
        self.short.update(price)
        self.long.update(price)
        self.calculatePPO()
        self.MACDsignal.update(self.result.macd)
        self.MACDhist = self.result.macd - self.MACDsignal.result
        self.PPOsignal.update(self.result.ppo)
        self.PPOhist = self.result.ppo - self.PPOsignal.result

        self.result.MACDsignal = self.MACDsignal.result
        self.result.MACDhist = self.MACDhist
        self.result.PPOsignal = self.PPOsignal.result
        self.result.PPOhist = self.PPOhist

    def calculatePPO(self):
        self.result.shortEMA = self.short.result
        self.result.longEMA = self.long.result
        self.result.macd = self.result.shortEMA - self.result.longEMA
        self.result.ppo = 100 * (self.result.macd / self.result.longEMA)

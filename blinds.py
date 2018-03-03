from random import randint


class Blinds:

    INCREASE_FREQUENCY = 12
    INCREASE_VARIANCE = 3
    INITIAL_BLINDS = [25, 50, 100, 200, 500, 1000, 1500, 2000, 5000, 10000]

    def __init__(self, num_players, buy_in):
        self.counter = 0
        self.increases = 0
        self.small_blind = self.INITIAL_BLINDS[0]

    def small_blind(self):
        return self.small_blind

    def big_blind(self):
        return self.small_blind * 2

    def next_round(self):
        self.counter += 1
        if self.is_in_increase_range() and self.check_for_blind_increase():
            self.small_blind = self.next_blinds()

    def is_in_increase_range(self):
        return self.counter >= self.INCREASE_VARIANCE - self.INCREASE_FREQUENCY

    def check_for_blind_increase(self):
        return randint(0, self.INCREASE_VARIANCE + self.INCREASE_FREQUENCY - self.counter) == 0

    def next_blinds(self):
        self.increases += 1
        if self.increases > len(self.INITIAL_BLINDS):
            self.small_blind *= 2
            return self.small_blind
        else:
            return self.INITIAL_BLIND[self.increases]

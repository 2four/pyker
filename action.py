class Action:

    def __str__(self):
        return type(self).__name__

    @classmethod
    def index(cls):
        return cls._index


class Fold(Action):
    _index = 0


class CheckCall(Action):
    _index = 1


class Raise(Action):
    _index = 2

    def __init__(self, amount):
        self.amount = amount

    def __str__(self):
        return "{} {}".format(type(self).__name__, self.amount)

class Action:

    def __str__(self):
        return type(self).__name__


class Fold(Action):
    pass


class CheckCall(Action):
    pass


class Raise(Action):

    def __init__(self, amount):
        self.amount = amount

    def __str__(self):
        return "{} {}".format(type(self).__name__, self.amount)

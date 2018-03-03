class Action:
    pass


class Fold(Action):
    pass


class Check(Action):
    pass


class Call(Action):
    pass


class Raise(Action):

    def __init__(self, amount):
        self.amount = amount

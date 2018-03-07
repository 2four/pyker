import click
import re

from poker import Player
from action import *


class HumanPlayer(Player):

    _raise_pattern = re.compile("raise\s+(\d+)\s*")

    def __init__(self, index):
        self.index = index

    def supply_state(self, card_1, card_2, game_state):
        self.card_1 = card_1
        self.card_2 = card_2
        self.game_state = game_state

    def get_action(self):
        print("Player number  : {}".format(self.index))
        print("Hole cards     : {} {}".format(self.card_1, self.card_2))
        print("Table cards    : {}".format(" ".join(str(card) for card in self.game_state.cards)))
        print("Current bet    : {}".format(self.game_state.current_bet))
        print("Pot            : {}".format(self.game_state.pot))
        print("Player chips   : {}".format(list(self.game_state.player_chips)))
        print("Turn indicator : {}".format(list(self.game_state.turn_indicator)))
        print("Folded         : {}".format(list(self.game_state.folded)))
        print("Last action    : {}".format(self.game_state.last_action))

        raisable = self.game_state.player_chips[0]

        while True:
            value = click.prompt("Action [Fold, Check, Call, Raise (n)]", type=str)

            if not value:
                print("Please enter a string")
                continue

            value = value.lower().strip()
            if value == "fold":
                return Fold()
            if value == "check":
                return CheckCall()
            if value == "call":
                return CheckCall()
            if value == "raise":
                return self.get_raise(raisable)

            raise_object = self.get_one_line_raise(value, raisable)
            if raise_object:
                return raise_object

            if not any(s in value for s in ["fold", "check", "call", "raise"]):
                print("Must be one of [Fold, Check, Call, Raise (n)]")

    def get_one_line_raise(self, value, raisable):
        match = self._raise_pattern.match(value)
        if match:
            amount = int(match.group(1))
            if self.check_raise_value(amount, raisable):
                return Raise(amount)

        return None

    def get_raise(self, raisable):
        while True:
            value = click.prompt("Raise amount", type=int)

            if not self.check_raise_value(value, raisable):
                continue

            return Raise(value)

    def check_raise_value(self, value, raisable):
        if not value:
            print("Must be an int")
            return False

        if not value % 25 == 0:
            print("Must be a multiple of 25")
            return False

        if value > raisable:
            print("Must be less than {}".format(raisable))
            return False

        return True

    def give_reward(self, reward):
        print("Player {} rewarded {:.2f}!".format(self.index, reward))

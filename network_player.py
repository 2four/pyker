from itertools import chain
from numpy import argmax
import _MultiNEAT as NEAT
import logging

from player import Player
from action import *


_table_cards_length = 85


def _concatenate(iterable, function):
    return list(chain.from_iterable(function(item) for item in iterable))


def _zero_pad_to_length(vector, length):
    return vector + [0] * (length - len(vector))


class NetworkPlayer(Player):

    LOGGER = logging.getLogger(name="NetworkPlayer")

    def __init__(self, genome, money_vector_size, table_size, min_denomination, genome_index=None):
        self.genome = genome
        self.network = NEAT.NeuralNetwork()
        self.genome.BuildPhenotype(self.network)

        self.money_vector_size = money_vector_size
        self.table_size = table_size
        self.min_denomination = min_denomination
        self.disqualified = False
        self.genome_index = genome_index

    def supply_state(self, card_1, card_2, bet, game_state):
        self.current_bet = game_state.current_bet
        self.LOGGER.debug("{}, {}".format(self.index, list(game_state.player_chips)))
        self.chips = game_state.player_chips[0]

        input_vector = (
            self.card_to_vector(card_1) +
            self.card_to_vector(card_2) +
            self.money_to_vector(bet) +
            self.table_cards_to_vector(game_state.cards) +
            self.money_to_vector(game_state.pot) +
            self.money_to_vector(game_state.current_bet) +
            self.player_chips_to_vector(game_state.player_chips) +
            self.indicator_to_vector(game_state.turn_indicator) +
            self.indicator_to_vector(game_state.folded) +
            self.action_to_vector(game_state.last_action)
        )

        self.network.Input(input_vector)
        self.network.Activate()

    def get_action(self):
        if self.disqualified:
            return Fold()

        output_vector = self.network.Output()
        action_index = argmax(output_vector[:3])

        if action_index == Fold.index():
            return Fold()
        elif action_index == CheckCall.index():
            return CheckCall()
        else:
            return self.deal_with_raise(output_vector)

    def give_reward(self, reward):
        fitness = self.genome.GetFitness()
        self.LOGGER.info("Player {} got rewarded {}".format(self.index, reward))
        self.genome.SetFitness(fitness + reward)

    def card_to_vector(self, card):
        suit = [0] * 4
        suit[card.suit.int_value] = 1

        number = [0] * 13
        number[card.number.int_value] = 1

        return suit + number

    def table_cards_to_vector(self, table_cards):
        table_card_vector = _concatenate(table_cards, self.card_to_vector)
        return _zero_pad_to_length(table_card_vector, _table_cards_length)

    def money_to_vector(self, amount):
        amount //= self.min_denomination
        binary_list = [int(bit) for bit in bin(amount)[2:]]
        return binary_list + [0] * (self.money_vector_size - len(binary_list))

    def player_chips_to_vector(self, table_chips):
        player_chips_vector = _concatenate(table_chips, self.money_to_vector)
        pad_length = self.table_size * self.money_vector_size
        return _zero_pad_to_length(player_chips_vector, pad_length)

    def indicator_to_vector(self, indicator):
        return _zero_pad_to_length(list(indicator), self.table_size)

    def action_to_vector(self, action):
        action_indicator = [0] * 3
        if action:
            action_indicator[action.index()] = 1

        if isinstance(action, Raise):
            money = action.amount
        else:
            money = 0

        money_vector = self.money_to_vector(money)
        return action_indicator + money_vector

    def vector_to_money(self, vector):
        money = 0
        int_vector = [0 if x < 0.5 else 1 for x in vector]

        for bit in int_vector:
            money = (money << 1) | bit
        return money * self.min_denomination

    def deal_with_raise(self, output_vector):
        amount = self.vector_to_money(output_vector[3:])
        self.LOGGER.debug("{} {} {}".format(amount, self.current_bet, self.chips))

        if self.chips == 0:
            self.LOGGER.info(
                "Player {} disqualified due to raising {} with 0 chips".format(
                    self.index,
                    amount
                )
            )

            self.disqualified = True
            return Fold()

        if self.chips < self.current_bet:
            self.LOGGER.info(
                "Player {} disqualified due to raising when current bet {} was higher than their chips {}".format(
                    self.index,
                    self.current_bet,
                    self.chips
                )
            )

            self.disqualified = True
            return Fold()

        if amount < self.current_bet and amount < self.chips:
            self.LOGGER.info(
                "Player {} disqualified due to raising {} (Minimum {}, Chips {})".format(
                    self.index,
                    amount,
                    self.current_bet,
                    self.chips
                )
            )

            self.disqualified = True
            return Fold()

        return Raise(amount)

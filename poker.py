from collections import deque
import logging

from seat import Seat
from poker_round import Round
from blinds import Blinds


class Table:

    LOGGER = logging.getLogger(name="Table")

    def __init__(self, players, buy_in, min_denomination):
        self.seats = deque()
        self.min_denomination = min_denomination
        self.player_positions = []
        self.blind_structure = Blinds(buy_in)

        self.player_indices = range(len(players))

        for player, index in zip(players, self.player_indices):
            seat = Seat(player, index, buy_in)
            self.seats.append(seat)

    def play(self):
        self.LOGGER.info("NEW TABLE")
        while len(self.seats) > 1:
            small_blind = self.blind_structure.next_round()
            poker_round = Round(self.seats, small_blind, self.min_denomination)
            self.seats, gone_out = poker_round.play()

            if gone_out:
                self.player_positions.append(gone_out)

            self.seats.rotate(-1)

        self.player_positions.append(list(self.seats))
        self.distribute_rewards()

    def distribute_rewards(self):
        reward_normalizer = sum(i * i for i in self.player_indices)
        ungrouped_rewards = [i * i / reward_normalizer for i in self.player_indices]
        ungrouped_rewards.reverse()

        for position_group in self.player_positions:
            reward_sum = 0

            for seat in position_group:
                reward_sum += ungrouped_rewards.pop()

            reward = reward_sum / len(position_group)

            for seat in position_group:
                seat.give_reward(reward)

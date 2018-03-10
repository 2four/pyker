import logging

from collections import deque


class Turn:

    LOGGER = logging.getLogger("Turn")

    def __init__(self, seats, filtered_seats, cards, current_bet, last_action):
        self.seats = seats
        self.filtered_seats = filtered_seats
        self.cards = cards
        self.current_bet = current_bet
        self.last_action = last_action

    def play(self):
        self.LOGGER.debug("Player {}'s go".format(self.seats[0].index))
        self.supply_state_to_seats()
        return self.get_action()

    def get_action(self):
        seat = self.filtered_seats[0]
        return seat.get_action()

    def supply_state_to_seats(self):
        pot = sum(seat.pot + seat.bet for seat in self.seats)

        player_chips = deque(seat.chips for seat in self.seats)
        turn_indicator = deque([1] + [0] * (len(self.seats) - 1))
        folded = deque([1 if seat not in self.filtered_seats else 0 for seat in self.seats])

        for seat in self.seats:
            seat.supply_state(GameState(
                self.cards,
                self.current_bet,
                self.last_action,
                pot,
                player_chips,
                turn_indicator,
                folded,
            ))

            player_chips.rotate(-1)
            turn_indicator.rotate(-1)
            folded.rotate(-1)

    def get_turn_indicator(self, seat):
        turn_indicator = [False] * len(self.seats)
        turn_indicator[(seat.index - self.seats[0].index) % len(self.seats)] = True
        return turn_indicator


class GameState:

    def __init__(self, cards, current_bet, last_action, pot, player_chips, turn_indicator, folded):
        self.cards = cards
        self.current_bet = current_bet
        self.last_action = last_action
        self.pot = pot
        self.player_chips = player_chips
        self.turn_indicator = turn_indicator
        self.folded = folded

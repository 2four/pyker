from turn import Turn
from action import *


class BettingRound:

    def __init__(self, seats, remaining_seats, cards, min_raise, bet=0):
        self.seats = seats
        self.remaining_seats = remaining_seats
        self.filtered_seats = deque(remaining_seats)
        self.cards = cards
        self.min_raise = min_raise

        self.current_bet = bet
        self.end_seat = seats[-1]

    def play(self):
        self.last_action = None

        while True:
            seat = self.filtered_seats[0]

            turn = Turn(
                self.seats,
                self.filtered_seats,
                self.cards,
                self.last_action,
                self.current_bet,
                self.min_raise
            )

            turn.supply_state_to_seats()
            last_action = turn.get_action()
            self.resolve_action(seat, last_action)

            if len(self.filtered_seats == 1):
                return self.filtered_seats[0:1]

            if seat == end_seat:
                # bets have been called
                return [seat for seat in self.remaining_seats if seat in self.filtered_seats]

            self.filtered_seats.rotate(-1)

    def resolve_action(self, seat, action):
        if isinstance(action, Fold):
            del self.filtered_seats[0]
        elif isinstance(action, Check):
            pass
        elif isinstance(action, Call):
            seat.move_chips_into_pot(self.current_bet)
        elif isinstance(action, Raise):
            self.end_seat = self.filtered_seats[-1]
            self.current_bet += action.amount
            seat.move_chips_into_pot(action.amount)

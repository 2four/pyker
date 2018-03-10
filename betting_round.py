from collections import deque
import logging

from turn import Turn
from action import *
from exception import IllegalActionException


class BettingRound:

    LOGGER = logging.getLogger(name="BettingRound")

    def __init__(self, seats, remaining_seats, cards, bet=0):
        self.LOGGER.debug("NEW BETTING ROUND")
        self.seats = deque(seats)
        self.remaining_seats = remaining_seats
        self.filtered_seats = deque(remaining_seats)
        self.cards = cards
        self.current_bet = bet

    def play(self):
        last_action = None
        self.end_seat = self.filtered_seats[-1]
        self.align_seat_deques()

        while True:
            seat = self.filtered_seats[0]

            turn = Turn(
                self.seats,
                self.filtered_seats,
                self.cards,
                self.current_bet,
                last_action,
            )

            last_action = turn.play()
            self.resolve_action(seat, last_action)

            if len(self.filtered_seats) == 1:
                self.LOGGER.debug("Player {} wins".format(self.filtered_seats[0].index))
                self.move_all_bets_to_pots()
                return list(self.filtered_seats)

            if seat is self.end_seat:
                # bets have been called
                self.move_all_bets_to_pots()
                return [seat for seat in self.remaining_seats if seat in self.filtered_seats]

            self.filtered_seats.rotate(-1)
            self.align_seat_deques()

    def align_seat_deques(self):
        while self.seats[0] != self.filtered_seats[0]:
            self.seats.rotate(-1)

    def move_all_bets_to_pots(self):
        for seat in self.seats:
            seat.move_bet_to_pot()

    def resolve_action(self, seat, action):
        if isinstance(action, Fold):
            del self.filtered_seats[0]
            self.filtered_seats.rotate()
            self.LOGGER.debug("Player {} folds".format(seat.index))
        elif isinstance(action, CheckCall):
            call_amount = self.current_bet - seat.bet
            call_amount = seat.bet_chips(call_amount)

            if call_amount == 0:
                self.LOGGER.debug("Player {} checks".format(seat.index))
            else:
                self.LOGGER.debug("Player {} calls, putting in {}".format(seat.index, call_amount))
        elif isinstance(action, Raise):
            self.LOGGER.debug("Player {} attempts to raise {}".format(seat.index, action.amount))

            if seat.chips == 0:
                raise IllegalActionException(
                    "Seat {} cannot raise with 0 chips".format(seat.index)
                )

            if seat.chips < self.current_bet:
                raise IllegalActionException(
                    "Seat {} cannot raise with {} chips when bet is {}".format(
                        seat.index,
                        seat.chips,
                        self.current_bet
                    )
                )

            if action.amount < self.current_bet and action.amount < seat.chips:
                raise IllegalActionException(
                    "Seat {}, chips {} - Must raise at least current bet ({})".format(
                        seat.index,
                        seat.chips,
                        self.current_bet
                    )
                )

            self.end_seat = self.filtered_seats[-1]

            call_amount = self.current_bet - seat.bet
            seat.bet_chips(call_amount)

            raise_amount = seat.bet_chips(action.amount)
            self.current_bet += raise_amount

            self.LOGGER.debug("Player {} raises {}".format(seat.index, raise_amount))


class PreFlop(BettingRound):

    def __init__(self, seats, remaining_seats, cards, big_blind):
        super().__init__(seats, remaining_seats, cards, big_blind)

    def play(self):
        # start left of small blind
        self.filtered_seats.rotate(-3)
        return super().play()

import logging

from poker import Seat
from card import Deck, get_best_hand
from collections import deque
from betting_round import BettingRound


class Round:

    def __init__(self, seats, small_blind, min_denomination):
        logging.info("NEW ROUND")
        self.seats = seats
        self.small_blind = small_blind
        self.min_denomination = min_denomination
        self.cards = []

    def play(self):
        self.shuffle_and_deal()
        self.put_in_blinds()
        min_raise = self.small_blind
        starting_bet = self.small_blind * 2
        remaining_seats = self.seats

        first_betting_round = BettingRound(self.seats, remaining_seats, self.cards, min_raise, starting_bet)
        remaining_seats = first_betting_round.play()

        if len(remaining_seats) == 1:
            self.distribute_winnings(remaining_seats)
            return self.get_seat_statuses()

        self.deal_flop()
        logging.info("Flop  {}".format(" ".join(str(card) for card in self.cards)))

        if self.players_can_bet(remaining_seats):
            second_betting_round = BettingRound(self.seats, remaining_seats, self.cards, min_raise)
            remaining_seats = second_betting_round.play()

        if len(remaining_seats) == 1:
            self.distribute_winnings(remaining_seats)
            return self.get_seat_statuses()

        self.deal_turn()
        logging.info("Turn  {}".format(" ".join(str(card) for card in self.cards)))

        if self.players_can_bet(remaining_seats):
            third_betting_round = BettingRound(self.seats, remaining_seats, self.cards, min_raise)
            remaining_seats = third_betting_round.play()

        if len(remaining_seats) == 1:
            self.distribute_winnings(remaining_seats)
            return self.get_seat_statuses()

        self.deal_river()
        logging.info("River {}".format(" ".join(str(card) for card in self.cards)))

        if self.players_can_bet(remaining_seats):
            final_betting_round = BettingRound(self.seats, remaining_seats, self.cards, min_raise)
            remaining_seats = final_betting_round.play()

        if len(remaining_seats) == 1:
            self.distribute_winnings(remaining_seats)
            return self.get_seat_statuses()

        winners = self.winners_from_remaining(remaining_seats)

        winner_string = ", ".join(str(winner.index) for winner in winners)
        logging.info("Winning player(s): {}".format(winner_string))

        self.distribute_winnings(winners)

        return self.get_seat_statuses()

    def players_can_bet(self, remaining_seats):
        can_bet = sum(1 for seat in remaining_seats if seat.chips > 0)
        return can_bet > 1

    def get_seat_statuses(self):
        still_in = deque(seat for seat in self.seats if seat.chips > 0)
        gone_out = [seat for seat in self.seats if seat.chips == 0]

        return still_in, gone_out

    def shuffle_and_deal(self):
        self.deck = Deck()
        self.deck.shuffle()

        for seat in self.seats:
            seat.set_card_1(self.deck.deal())

        for seat in self.seats:
            seat.set_card_2(self.deck.deal())

    def put_in_blinds(self):
        small_blind = self.small_blind
        big_blind = self.small_blind * 2

        self.seats[1].bet_chips(small_blind)
        self.seats[2 % len(self.seats)].bet_chips(big_blind)

    def deal_flop(self):
        # burn card
        self.deck.deal()

        # deal three cards as the flop
        for _ in range(3):
            self.cards.append(self.deck.deal())

    def deal_turn(self):
        # burn card
        self.deck.deal()

        # deal turn
        self.cards.append(self.deck.deal())

    def deal_river(self):
        # burn card
        self.deck.deal()

        # deal turn
        self.cards.append(self.deck.deal())

    def winners_from_remaining(self, remaining_seats):
        hands = []

        for seat in remaining_seats:
            hand = get_best_hand(seat.get_cards(), self.cards)
            hands.append((seat, hand))

        best_hand = max(hands, key=lambda seat_hand_pair: seat_hand_pair[1])
        return [seat_hand_pair[0] for seat_hand_pair in hands if seat_hand_pair[1] == best_hand[1]]

    def distribute_winnings(self, winners):
        winners.sort(key=lambda seat: seat.pot)
        winners_by_deal_order = [seat for seat in self.seats if seat in winners]

        while len(winners) > 0:
            winner = winners[0]
            winnings = 0
            winnings_cap = winner.pot

            # create a side pot
            for seat in self.seats:
                winnings += seat.get_chips_from_pot(winnings_cap)

            # split that side pot
            normalized_winnings = winnings // self.min_denomination
            quotient = (normalized_winnings // len(winners)) * \
                self.min_denomination
            remainders = normalized_winnings % len(winners)

            for winner in winners:
                winner.take_winnings(quotient)

            for index in range(remainders):
                winners_by_deal_order[index].take_winnings(
                    self.min_denomination)

            del winners[0]

        for seat in self.seats:
            seat.reclaim_remaining_pot()

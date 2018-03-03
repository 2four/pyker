from poker import Seat
from card import Deck, get_best_hand
from collections import deque
from betting_round import BettingRound


class Round:

    def __init__(self, seats, blinds, min_denomination):
        self.seats = seats
        self.blinds = blinds
        self.min_denomination = min_denomination

    def shuffle_and_deal(self):
        self.deck = Deck()
        self.deck.shuffle()

        for seat in self.seats:
            seat.set_card_1(self.deck.deal())

        for seat in self.seats:
            seat.set_card_2(self.deck.deal())

    def put_in_blinds(self):
        self.seats[1].move_chips_into_pot(self.blinds.small_blind)
        self.seats[2 % len(self.seats)].move_chips_into_pot(self.blinds.big_blind)

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

    def play(self):
        self.shuffle_and_deal()
        min_raise = self.blinds[1]
        remaining_seats = self.seats

        first_betting_round = BettingRound(remaining_seats, self.cards, min_raise, min_raise)
        remaining_seats = first_betting_round.play()

        if len(remaining_seats) == 1:
            self.distribute_winnings(remaining_seats)
            return

        self.play_flop()

        second_betting_round = BettingRound(remaining_seats, self.cards, min_raise)
        remaining_seats = second_betting_round.play()

        if len(remaining_seats) == 1:
            self.distribute_winnings(remaining_seats)
            return

        self.play_turn()

        third_betting_round = BettingRound(remaining_seats, self.cards, min_raise)
        remaining_seats = third_betting_round.play()

        if len(remaining_seats) == 1:
            self.distribute_winnings(remaining_seats)
            return

        self.play_flop()

        final_betting_round = BettingRound(remaining_seats, self.cards, min_raise)
        remaining_seats = final_betting_round.play()

        if len(remaining_seats) == 1:
            self.distribute_winnings(remaining_seats)
            return

        winners = self.winners_from_remaining()
        self.distribute_winnings(winners)
        return deque(seat for seat in self.seats if seat.chips > 0)

    def winners_from_remaining(self):
        hands = []

        for seat in self.seats:
            hand = get_best_hand(seat)
            hands.append((seat, hand))

        best_hand = max(hands, key=lambda seat_hand_pair: seat_hand_pair[1])
        return [seat_hand_pair for seat_hand_pair in hands if seat_hand_pair[1] == best_hand[1]]

    def distribute_winnings(self, winners):
        winners.sort(key=Seat.pot)
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
            quotient = (normalized_winnings // len(winners)) * self.min_denomination
            remainders = normalized_winnings % len(winners)

            for winner in winners:
                winner.take_winnings(quotient)

            for index in range(remainders):
                winners_by_deal_order[index].take_winnings(self.min_denomination)

            del winners[0]

        for seat in self.seats:
            seat.reclaim_remaining_pot()

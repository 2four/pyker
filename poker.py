from action import *
from itertools import chain, repeat
from collections import deque

from seat import Seat
from blinds import Blinds


def _ncycles(iterable, n):
    "Returns the sequence elements n times"
    return chain.from_iterable(repeat(tuple(iterable), n))


class Table:

    def __init__(self, players, buy_in):
        # constant over entire game
        self.player_indices = range(len(players))
        self.num_players
        self.seats = deque(Seat(player, index, buy_in) for player, index in zip(players, player_indices))
        self.blind_structure = Blinds(self.num_players, buy_in)

        # reset each round
        self.button_position = self.num_players
        self.cards = []

        # reset each betting round
        self.last_action = None
        self.last_raise_index = None
        self.current_bet = 0

        # reset each turn
        self.seat_order = self.seats

    def get_seat_order(self, index):
        # increase index to starting index
        index = (index + 1) % self.num_players

        # get cyclic list from index, e.g. for 8 players, 3 -> [3, 4, 5, 6, 7, 0, 1, 2]
        double_seat_list = list(_ncycles(self.player_indices, 2))
        return double_seat_list[index:index + self.num_players]

    # def filter_by_still_in(self, seat_order):
    #     return [i for i in seat_order if self.seats[i].still_in()]

    # def filter_by_folded(self, seat_order):
    #     return [i for i in seat_order if not self.seats[i].folded]

    # def filter_by_active(self, seat_order):
    #     return [i for i in seat_order if self.seats[i].can_perform_action()]

    # def get_round_winner(self):
    #     seat_order = get_seat_order(self.turn_indicator)
    #     seat_order = filter_by_still_in(seat_order)
    #     seat_order = filter_by_folded(seat_order)
    #     if len(still_in) == 1:
    #         return still_in[0]

    def next_turn(self):
        seat_order = get_seat_order(self.turn_indicator)
        seat_order = filter_by_still_in(seat_order)
        seat_order = filter_by_folded(seat_order)
        seat_order = filter_by_active(seat_order)

        self.seat_order = seat_order
        self.turn_indicator = seat_order[0]

    def get_turn_indicator(self, seat_index):
        turn_indicator = [False] * self.num_players
        turn_indicator[(seat_index - self.turn_indicator) % self.num_players] = True
        return turn_indicator

    # def supply_state_to_seats(self, seat_order):
    #     pot = sum([seats[i].pot for i in seat_order])
    #     player_pots = [seats[i].chips for i in seat_order]

    #     for seat_index in seat_order:
    #         seat = self.seats[seat_index]
    #         seat.supply_state(GameState(
    #             self.cards,
    #             self.current_bet,
    #             pot,
    #             player_pots,
    #             self.get_turn_indicator(seat_index),
    #             self.last_action
    #         ))

    # def get_action(self):
    #     seat = self.seats[self.turn_indicator]
    #     self.last_action = seat.get_action()

    # def resolve_action(self, seat, action):
    #     seat = self.seats[self.turn_indicator]
    #     action = self.last_action

    #     if isinstance(action, Fold):
    #         seat.folded = True
    #     elif isinstance(action, Check):
    #         pass
    #     elif isinstance(action, Call):
    #         seat.move_chips_into_pot(self.current_bet)
    #     elif isinstance(action, Raise):
    #         self.last_raise_index = self.turn_indicator
    #         self.current_bet += action.amount
    #         seat.move_chips_into_pot(action.amount)

    def play_turn(self):
        next_turn()
        supply_state_to_seats()
        get_action()
        resolve_action()

    # betting round

    # def new_betting_round(self):
    #     self.last_action = None
    #     self.last_raise_index = None
    #     self.current_bet = 0

    # def reached_last_raise_index():
    #     return self.last_raise_index == self.turn_indicator

    # def play_betting_round(self):
    #     new_betting_round()

    #     round_winner = None
    #     reached_last_raise_index = False

    #     while not round_winner or reached_last_raise_index:
    #         play_turn()
    #         round_winner = get_round_winner()
    #         reached_last_raise_index = reached_last_raise_index()

    #     if round_winner:
    #         return round_winner


    # round

    def move_button_forward(self):
        seat_order = get_seat_order(self.button_position)
        seat_order = filter_by_still_in(seat_order)

        self.seat_order = seat_order
        self.button_position = seat_order[0]
        self.turn_indicator = (self.button_position + 2) % self.num_players

    # def shuffle_and_deal():
    #     self.deck = Deck()
    #     self.deck.shuffle()

    #     seat_order = get_seat_order(self.button_position)
    #     seat_order = filter_by_still_in(seat_order)

    #     for seat in seat_order:
    #         seat = self.seats[i]
    #         seat.set_card_1(deck.deal())

    #     for seat in seat_order:
    #         seat = self.seats[i]
    #         seat.set_card_2(deck.deal())

    # def put_in_blinds():
    #     small_blind_index = self.seat_order[1]
    #     big_blind_index = self.seat_order[2]

    #     small_blind = self.blind_structure.small_blind()
    #     big_blind = self.blind_structure.big_blind()

    #     self.seats[small_blind_index].move_chips_into_pot(small_blind)
    #     self.seats[big_blind_index].move_chips_into_pot(big_blind)

    # def deal_flop():
    #     # burn card
    #     self.deck.deal()

    #     # deal three cards as the flop
    #     for _ in range(3):
    #         self.cards.append(self.deck.deal())

    # def deal_turn():
    #     # burn card
    #     self.deck.deal()

    #     # deal turn
    #     self.cards.append(self.deck.deal())

    # def deal_river():
    #     # burn card
    #     self.deck.deal()

    #     # deal turn
    #     self.cards.append(self.deck.deal())

    # def new_round(self):
    #     self.current_bet = 0
    #     self.cards = None
    #     self.last_action = None

    #     for seat in self.seats:
    #         seat.refresh()

    #     self.move_button_forward()
    #     self.shuffle_and_deal()
    #     self.blind_structure.next_round()

    # def play_round(self):
    #     new_round()
    #     put_in_blinds()
    #     deal_flop()


class GameState:

    def __init__(self, cards, current_bet, folded, pot, player_chips, turn_indicator, last_action):
        self.cards = cards
        self.current_bet = current_bet
        self.last_action = last_action
        self.pot = pot
        self.player_chips = player_chips
        self.turn_indicator = turn_indicator
        self.folded = folded


class Player:

    def supply_state(self, card_1, card_2, game_state):
        raise NotImplementedError()

    def get_action(self):
        raise NotImplementedError()


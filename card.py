from enum import Enum, IntEnum
from itertools import combinations
from random import shuffle


class Card:

    NUMBERS = range(1, 14)

    def __init__(self, suit, number):
        self.suit = suit
        self.number = number

    def __str__(self):
        return "{} of {}".format(self.number.name, self.suit.name)

    def __lt__(self, other):
        return self.number < other.number


class Suit(Enum):
    SPADES = 0
    HEARTS = 1
    DIAMONDS = 2
    CLUBS = 3


class Number(IntEnum):
    ACE_LOW = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Deck:

    def __init__(self):
        self.cards = []
        for suit in Suit:
            for number in Number:
                if number == Number.ACE_LOW:
                    continue
                card = Card(suit, number)
                self.cards.append(card)

    def shuffle(self):
        shuffle(self.cards)

    def deal(self):
        return self.cards.pop()


class Hand:

    def __lt__(self, other):
        if self.rank() == other.rank():
            return self.less_than(other)
        else:
            return self.rank() < other.rank()

    def __eq__(self, other):
        return not self < other and not other < self

    def less_than(self, other):
        raise NotImplementedError()

    @classmethod
    def rank(cls):
        return cls._rank


class RoyalFlush(Hand):

    _rank = 9


class StraightFlush(Hand):

    _rank = 8

    def __init__(self, highest_card):
        self.highest_card = highest_card

    def less_than(self, other):
        return self.highest_card < other.highest_card


class FourOfAKind(Hand):

    _rank = 7

    def __init__(self, four):
        self.four = four

    def less_than(self, other):
        return self.four < other.four


class FullHouse(Hand):

    _rank = 6

    def __init__(self, three):
        self.three = three

    def less_than(self, other):
        return self.three < other.three


class Flush(Hand):

    _rank = 5

    def __init__(self, cards):
        self.cards = HighCards(cards)

    def less_than(self, other):
        return self.cards.less_than(other.cards)


class Straight(Hand):

    _rank = 4

    def __init__(self, highest_card):
        self.highest_card = highest_card

    def less_than(self, other):
        return self.highest_card < other.highest_card


class ThreeOfAKind(Hand):

    _rank = 3

    def __init__(self, three):
        self.three = three

    def less_than(self, other):
        return self.three < other.three


class TwoPair(Hand):

    _rank = 2

    def __init__(self, high_pair, low_pair, single):
        self.high_pair = high_pair
        self.low_pair = low_pair
        self.single = single

    def less_than(self, other):
        if self.high_pair < other.high_pair:
            return True

        if self.high_pair > other.high_pair:
            return False

        if self.low_pair < other.low_pair:
            return True

        if self.low_pair > other.low_pair:
            return False

        if self.single < other.single:
            return True

        return False


class OnePair(Hand):

    _rank = 1

    def __init__(self, pair, cards):
        self.pair = pair
        self.high_cards = HighCards(cards)

    def less_than(self, other):
        if self.pair < other.pair:
            return True

        if self.pair > other.pair:
            return False

        return self.high_cards.less_than(other.high_cards)


class HighCards(Hand):

    _rank = 0

    def __init__(self, cards):
        self.cards = cards

    def less_than(self, other):
        for card_1, card_2 in zip(self.cards, other.cards):
            if card_1 < card_2:
                return True
            if card_1 > card_2:
                return False

        return False


def get_best_hand(hole_cards, community_cards):
    cards = [*hole_cards, *community_cards]
    card_combinations = [list(card_set) for card_set in combinations(cards, 5)]

    hand = get_hand(card_combinations[0])
    for card_set in card_combinations[1:]:
        new_hand = get_hand(card_set)
        hand = max(hand, new_hand)

    return hand


def get_hand(card_set):
    card_set.sort(reverse=True)

    number_counts = get_number_distribution(card_set)

    four_of_a_kind = get_four_of_a_kind(number_counts)
    if four_of_a_kind:
        return four_of_a_kind

    full_house = get_full_house(number_counts)
    if full_house:
        return full_house

    three_of_a_kind = get_three_of_a_kind(number_counts)
    if three_of_a_kind:
        return three_of_a_kind

    two_pairs = get_two_pairs(number_counts)
    if two_pairs:
        return two_pairs

    pair = get_pair(number_counts)
    if pair:
        return pair

    flush = get_flush(card_set)
    straight = get_straight(card_set)

    if flush and straight and card_set[0].number == Number.ACE:
        return RoyalFlush()

    if flush and straight:
        return StraightFlush(straight.highest_card)

    if flush:
        return flush

    if straight:
        return straight

    return HighCards([card.number for card in card_set])


def get_number_distribution(card_set):
    number_counts = dict()

    for card in card_set:
        try:
            number_counts[card.number] += 1
        except KeyError:
            number_counts[card.number] = 1

    return number_counts


def get_four_of_a_kind(number_counts):
    for number, count in number_counts.items():
        if count == 4:
            return FourOfAKind(number)

    return None


def get_full_house(number_counts):
    if 2 in number_counts.values() and 3 in number_counts.values():
        triple, = [number for number, count in number_counts.items() if count == 3]
        return FullHouse(triple)

    return None


def get_three_of_a_kind(number_counts):
    if 3 in number_counts.values():
        triple, = [number for number, count in number_counts.items() if count == 3]
        return ThreeOfAKind(triple)

    return None


def get_two_pairs(number_counts):
    pairs = [number for number, count in number_counts.items() if count == 2]

    if len(pairs) == 2:
        high_pair = max(pairs)
        low_pair = min(pairs)
        single, = [number for number, count in number_counts.items() if count == 1]

        return TwoPair(high_pair, low_pair, single)

    return None


def get_pair(number_counts):
    pairs = [number for number, count in number_counts.items() if count == 2]

    if len(pairs) == 1:
        pair, = pairs
        numbers = [number for number, count in number_counts.items() if count == 1]

        return OnePair(pair, numbers)

    return None


def get_flush(card_set):
    suits = set(card.suit for card in card_set)
    if len(suits) == 1:
        numbers = [cards.number for cards in card_set]

        return Flush(numbers)


def get_straight(card_set):
    numbers = [card.number for card in card_set]

    if numbers == [Number.ACE, Number.FIVE, Number.FOUR, Number.THREE, Number.TWO]:
        return Straight(Number.FIVE)

    if all(number_1 - number_2 == 1 for number_1, number_2 in zip(numbers[:-1], numbers[1:])):
        return Straight(numbers[0])

    return None

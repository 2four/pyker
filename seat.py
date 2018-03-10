import logging


class Seat:

    LOGGER = logging.getLogger(name="Seat")

    def __init__(self, player, index, chips):
        self.player = player
        self.index = index
        self.chips = chips
        self.bet = 0
        self.pot = 0
        self.folded = False

        self.player.set_index(index)

    def set_card_1(self, card_1):
        self.card_1 = card_1

    def set_card_2(self, card_2):
        self.card_2 = card_2

    def get_cards(self):
        return self.card_1, self.card_2

    def supply_state(self, game_state):
        self.player.supply_state(self.card_1, self.card_2, self.bet, game_state)

    def get_action(self):
        return self.player.get_action()

    def refresh(self):
        self.folded = False
        self.card_1 = None
        self.card_2 = None

    def bet_chips(self, num_chips):
        bet = min(self.chips, num_chips)
        self.LOGGER.debug("Player {} puts {} chips in".format(self.index, bet))
        self.chips -= bet
        self.bet += bet

        return bet

    def move_bet_to_pot(self):
        self.pot += self.bet
        self.bet = 0

    def get_chips_from_pot(self, num_chips):
        taken = min(self.pot, num_chips)
        self.pot -= taken
        return taken

    def reclaim_remaining_pot(self):
        self.chips += self.pot
        self.pot = 0

    def take_winnings(self, winnings):
        self.chips += winnings

    def still_in(self):
        return self.chips + self.pot > 0

    def can_perform_action(self):
        return self.chips > 0

    def give_reward(self, reward):
        self.player.give_reward(reward)

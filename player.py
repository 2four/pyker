class Player:

    def supply_state(self, card_1, card_2, bet, game_state):
        raise NotImplementedError()

    def get_action(self):
        raise NotImplementedError()

    def give_reward(self, reward):
        raise NotImplementedError()

    def set_index(self, index):
        self.index = index

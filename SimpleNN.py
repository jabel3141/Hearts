from Player import Player
from play_nn import play_nn


class SimpleNN(Player):
    def __init__(self, name):
        super().__init__(name)
        self.play_policy = play_nn()
        # pass_policy = pass_nn()

    def select_play_card(self, game_state):
        return self.play_policy.predict(game_state)

    def select_pass_card(self):
        return self.hand.getRandomCard()

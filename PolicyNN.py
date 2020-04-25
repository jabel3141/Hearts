from Player import Player
from PolicyGradientModel import Agent


class PolicyNN(Player):
    def __init__(self, name):
        super().__init__(name)
        self.play_policy = Agent(lr=0.005, numActions=52, layer1Size=256, layer2Size=128, inputSize=64)

    def select_play_card(self, game_state):
        plays = self.legal_plays(game_state)
        return self.play_policy.choose_action(game_state, plays)

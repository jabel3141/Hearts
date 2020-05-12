from Player import Player
from PolicyGradientModel import PolicyGradientModel
import random
from Deck import Deck


class PolicyNN(Player):
    def __init__(self, name, models=None):
        super().__init__(name)
        self.play_policy = PolicyGradientModel(lr=5e-5, gamma=0.9, numActions=52, layer1Size=512, layer2Size=256,
                                               layer3Size=128, inputSize=169, models=models)

    def select_play_card(self, game_state):
        plays = self.legal_plays(game_state)
        return self.play_policy.choose_action(game_state, plays)

    def select_pass_card(self):  # Copied from SimpleAI
        all_cards = self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts
        return sorted(all_cards, key=Deck.card_rank_to_sort_val)[-1]

    def store_transition(self, state, action, reward):
        self.play_policy.store_transition(state, action, reward)

    def store_reward(self, reward):
        self.play_policy.store_reward(reward)

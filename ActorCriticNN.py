from Player import Player
from PolicyGradientModel import Agent
import random
from Deck import Deck


class ActorCriticNN(Player):
    def __init__(self, name):
        super().__init__(name)
        self.play_policy = Agent(lr=0.001, numActions=52, layer1Size=256, layer2Size=128, inputSize=64)

    def select_play_card(self, game_state):
        plays = self.legal_plays(game_state)
        return self.play_policy.choose_action(game_state, plays)

    # def select_pass_card(self):
    #     return random.choice(self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts)

    def select_pass_card(self):
        all_cards = self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts
        return sorted(all_cards, key=Deck.card_rank_to_sort_val)[-1]

    def store_transition(self, state, action, reward):
        self.play_policy.store_transition(state, action, reward)

    def store_reward(self, reward):
        self.play_policy.store_reward(reward)
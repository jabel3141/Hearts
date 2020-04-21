from Player import Player
import random


class RandomAI(Player):
    def __init__(self, name):
        super().__init__(name)

    def select_pass_card(self):
        return random.choice(self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts)

    def select_play_card(self, game_state):
        return random.choice(self.legal_plays(game_state))

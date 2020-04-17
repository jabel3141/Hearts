from Player import Player

class RandomAI(Player):
    def __init__(self, name):
        super().__init__(name)

    def select_pass_card(self):
        return self.hand.getRandomCard()

    def select_play_card(self):
        return self.hand.getRandomCard()
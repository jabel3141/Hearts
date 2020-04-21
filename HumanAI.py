from Player import Player

class HumanAI(Player):
    def __init__(self, name):
        super().__init__(name)

    def select_pass_card(self):
        while True:
            card = self.getInput("pass")
            if not self.hand.hasCard(card):
                print("Enter valid card")
            else:
                return card

    def select_play_card(self, heartsBroken=False, trick_num=0, game_info=None):
        while True:
            card = self.getInput("play")
            if not self.hand.hasCard(card):
                print("Enter valid card")
            else:
                return card

from Player import Player

class HumanAI(Player):
    def __init__(self, name):
        super().__init__(name)

    def select_pass_card(self):
        while True:
            card_str = self.getInput("pass")
            card = self.hand.str_to_card(card_str)
            if card is None:
                print("Enter valid card")
            else:
                return card

    def select_play_card(self):
        while True:
            card_str = self.getInput("play")
            card = self.hand.str_to_card(card_str)
            if card is None:
                print("Enter valid card")
            else:
                return card
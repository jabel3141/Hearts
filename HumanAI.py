from Player import Player


class HumanAI(Player):
    def __init__(self, name):
        super().__init__(name)

    def select_pass_card(self):
        while True:
            card = self.get_input("pass")
            if not self.hand.hasCard(card):
                print("Enter valid card")
            else:
                return card

    def select_play_card(self, game_state):
        legal = self.legal_plays(game_state)
        print(legal)
        while True:
            card = self.get_input("play")
            if not self.hand.hasCard(card):
                print("Enter valid card")
            elif card not in legal:
                print("Not a legal play")
            else:
                return card

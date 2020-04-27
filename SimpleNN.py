import random
from Player import Player
from play_nn import play_nn
import numpy as np

class SimpleNN(Player):
    def __init__(self, name):
        super().__init__(name)
        self.play_policy = play_nn()
        # pass_policy = pass_nn()

    def from_card_to_target(self, card):
        suit = card[-1:]
        rank = card[:-1]

        suit_num = 0
        if suit == 'c':
            suit_num = 0
        elif suit == 'd':
            suit_num = 1
        elif suit == 's':
            suit_num = 2
        elif suit == 'h':
            suit_num = 3


        if rank == "J":
            rank_num = 11
        elif rank == "Q":
            rank_num = 12
        elif rank == "K":
            rank_num = 13
        elif rank == "A":
            rank_num = 14
        else:
            rank_num = int(rank)

        target_val = suit_num*13 + rank_num-2

        return target_val


    def select_play_card(self, game_state):

        # # make a random play (explore)
        # if np.random.random() < self.play_policy.odds_explore:
        #     # sets up the network and puts the game state into the network
        #     card = self.play_policy.predict(game_state)
        #     card = random.choice(self.legal_plays(game_state))
        # # exploit
        # else:
        #     card = self.play_policy.predict(game_state)

        card = self.play_policy.predict(game_state)
        legal_moves = self.legal_plays(game_state)
        if card not in self.legal_plays(game_state):
            card = random.choice(legal_moves)
            self.play_policy.target = self.from_card_to_target(card)


        return card

    def select_pass_card(self):
        return random.choice(self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts)

    def train(self, reward):
        target = self.play_policy.target
        target_vec = np.squeeze(self.play_policy.train_predict(self.play_policy.game_state)[0])

        target_vec = np.multiply(target_vec, self.play_policy.legal_loss_play)
        target_vec[target] = reward
        target_vec = np.expand_dims(target_vec,axis=0)
        model_input = np.expand_dims(self.play_policy.last_input, axis=0)
        # legal = self.play_policy.last_legal
        self.play_policy.model.fit(model_input, target_vec, epochs=1, verbose=0)


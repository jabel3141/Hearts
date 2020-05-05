from keras.models import Sequential, Model
from keras.layers import Dense, Input, Maximum
from keras.backend import argmax
from keras.optimizers import SGD, Adam
import numpy as np

from Deck import Deck


def from_card_to_target(card):
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

    target_val = suit_num * 13 + rank_num - 1

    return target_val


class play_nn():

    def __init__(self):
        # TODO fix input shape to be the correct size and paly with netowrk shape
        self.basic_input = Input((164,))
        self.x = Dense(256, activation='relu')(self.basic_input)
        self.x = Dense(128, activation='relu')(self.x)
        self.learn_legal = Dense(52, activation='relu', name='learn_legal')(self.x)

        # self.legal_moves = Dense(52, name='legal_moves', use_bias=False)(self.learn_legal)

        self.model = Model(self.basic_input, self.learn_legal)

        # don't really know when this should happen

        self.model.compile(loss='mse', optimizer='adam')

        try:
            self.model.load_weights('models/qlearn/q_model.h5')
        except:
            print("either no file or wrong network structure, should be good next time")

        # store to run again for the loss
        self.last_input = None
        self.last_legal = None
        self.game_state = None
        self.target = 0
        # chance of exploring a random pick
        self.odds_explore = .5
        self.decay_factor = .999

        # used to store inputs for the model so we can do batch learning
        self.inputs = []

        # can use if we want not completely needed
        self.legal_loss_play = []

    @staticmethod
    def rotate(players, num_rotate):
        np_players = np.array(players)

        np_players = np.roll(np_players, -1 * num_rotate)

        players = np_players.tolist()

        return players

    def make_input(self, game_info):
        nn_input = np.zeros((164,))

        # rotate us so we are player 0
        players = game_info.players
        player_pos = game_info.playerPos
        players = self.rotate(players, player_pos)

        me = players[0]
        my_hand = me.hand
        player_1 = players[1]
        player_2 = players[2]
        player_3 = players[3]
        passed_to = me.passedCards[3] - player_pos

        if passed_to < 0:
            passed_to += 4

        a_deck = Deck().deck

        # one hot instead keeping it simple first
        # [1 0 0] we have the card
        # [0 1 0] the card has been played
        # [0 0 1] the card is on the table
        # [0 0 0] we don't know where the card is
        trick = game_info.trick

        for i, a_card in enumerate(a_deck):

            if my_hand.hasCard(a_card):
                nn_input[i * 3] = 1
            elif a_card in trick.trick:
                nn_input[i * 3 + 2] = 1
            elif player_1.has_played(a_card) or player_2.has_played(a_card) or player_3.has_played(a_card)\
                    or me.has_played(a_card):
                nn_input[i * 3 + 1] = 1


        # elements 0-51 represent one card in the deck, the value represents where the card is
        # for i, a_card in enumerate(a_deck):
        #     # 1 if the card is in our hand
        #     suit = a_card[-1:]
        #     rank = a_card[:-1]
        #     if my_hand.hasCard(a_card):
        #         nn_input[i] = 1
        #
        #     # 2 we played it
        #     elif me.has_played(a_card):
        #         nn_input[i] = 2
        #
        #     # 3 passed to player 1
        #     elif me.has_passed(a_card):
        #         if passed_to == 1:
        #             nn_input[i] = 3
        #
        #     # 4 player 1 played
        #     elif player_1.has_played(a_card):
        #         nn_input[i] = 4
        #
        #     # 5 passed to player 2
        #     elif me.has_passed(a_card):
        #         if passed_to == 2:
        #             nn_input[i] = 5
        #
        #     # 6 player 2 played
        #     elif player_2.has_played(a_card):
        #         nn_input[i] = 6
        #
        #     # 7 passed to player 3
        #     elif me.has_passed(a_card):
        #         if passed_to == 3:
        #             nn_input[i] = 7
        #
        #     # 8 player 3 played
        #     elif player_3.has_played(a_card):
        #         nn_input[i] = 8
        #
        #     # 0 have not seen the card
        #     else:
        #         nn_input[i] = 0

        # make all numbers between 0 and 1
        # nn_input = np.true_divide(nn_input, 8)


        # fill in what the trick looks like so far, 0 it has not been played, value is the card value
        # for i in range(4):
        #     try:
        #         card_played = trick.trick[i]
        #         card_val = from_card_to_target(card_played) / 52
        #         nn_input[i + 104] = card_val
        #     except:
        #         nn_input[i + 104] = 0

        # fill in the score for each player in the game
        for i in range(4):
            # total score
            nn_input[i + 156] = players[i].score
            nn_input[i + 160] = players[i].currentScore

        return nn_input

    def make_legal_layer(self, me, game_state):
        # diagonal matrix: 1 if legal 0 if not
        legal_plays = np.zeros((1, 52, 52))

        # 1 if legal 0 if not
        loss_legal_plays = np.zeros((52,))

        a_deck = Deck().deck

        legal = me.legal_plays(game_state)
        for i, a_card in enumerate(a_deck):
            if a_card in legal:
                legal_plays[0, i, i] = 10
                loss_legal_plays[i] = 10
            else:
                legal_plays[0, i, i] = .01
                loss_legal_plays[i] = .01
        # store values for later loss
        self.last_legal = loss_legal_plays
        self.legal_loss_play = loss_legal_plays
        return legal_plays

    def convert_prediction_to_card(self, prediction):
        prediction = prediction[0].flatten()
        prediction = np.multiply(prediction, self.legal_loss_play)
        one_pred = argmax(prediction)
        self.target = one_pred
        suit = int(one_pred / 13)
        rank = int((one_pred % 13))
        return Deck.index_to_rank(rank) + Deck.index_to_suit(suit)

    # game_info is of class AIInfo
    def predict(self, game_state):
        nn_input = self.make_input(game_state)

        self.game_state = game_state.__copy__()
        self.last_input = nn_input
        me = game_state.players[game_state.playerPos]
        # layer = self.model.get_layer('legal_moves')
        legal_weights = self.make_legal_layer(me, game_state)

        # layer.set_weights(legal_weights)
        nn_input = nn_input.reshape(1, 164)
        prediction = self.model.predict(nn_input)

        return self.convert_prediction_to_card(prediction)

    def train_predict(self, game_state):
        nn_input = self.make_input(game_state)

        # me = game_state.players[game_state.playerPos]
        # layer = self.model.get_layer('legal_moves')
        # legal_weights = self.make_legal_layer(me, game_state)
        #
        # layer.set_weights(legal_weights)
        nn_input = nn_input.reshape(1, 164)
        prediction = self.model.predict(nn_input)

        return prediction

    # not sure how we are going to connect score from game to the network to keep gradient
    def train(self, scores):
        # best score is 0 so temporarily make list as long as scores of zeros
        y_opt = np.zeros_like(scores)

        # currently won't work because we cannot update the legal_moves set to the correct weights
        self.model.fit(self.inputs, [y_opt, self.legal_loss_plays],
                       batch_size=13,
                       epochs=1)

        # save the new weights to folder to bring up again

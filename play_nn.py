from keras.models import Sequential, Model
from keras.layers import Dense, Input, Maximum
from keras.backend import argmax
from keras.optimizers import SGD, Adam
import numpy as np
import AIInfo
from Card import Card
from collections import deque

from Deck import Deck


class play_nn():

    def __init__(self):
        # TODO fix input shape to be the correct size and paly with netowrk shape
        self.basic_input = Input((64,))
        self.x = Dense(256, activation='sigmoid')(self.basic_input)
        self.x = Dense(128, activation='sigmoid')(self.x)
        self.learn_legal = Dense(52, activation='sigmoid', name='learn_legal')(self.x)

        self.legal_moves = Dense(52, name='legal_moves', use_bias=False)(self.learn_legal)

        self.model = Model(self.basic_input, [self.legal_moves, self.learn_legal])

        # don't really know when this should happen

        self.model.compile(loss='mse', optimizer='adam')

        try:
            self.model.load_weights('simple_play_weights.h5')
        except:
            print("weights do not exist")

        # used to store inputs for the model so we can do batch learning
        self.inputs = []

        # can use if we want not completely needed
        self.legal_loss_plays = []

    @staticmethod
    def rotate(players, num_rotate):
        np_players = np.array(players)

        np_players = np.roll(np_players, -1 * num_rotate)

        players = np_players.tolist()

        return players

    def make_input(self, game_info):
        nn_input = np.zeros((64,))

        # rotate us so we are player 0
        players = game_info.players
        player_pos = game_info.playerPos
        players = self.rotate(players, player_pos)

        me = players[0]
        my_hand = me.hand
        i_played = me.cardsPlayed
        i_passed = me.passedCards[:3]
        player_1 = players[1]
        player_2 = players[2]
        player_3 = players[3]
        passed_to = me.passedCards[3] - player_pos

        if passed_to < 0:
            passed_to += 4

        a_deck = Deck().deck

        # elements 0-51 represent one card in the deck, the value represents where the card is
        for i, a_card in enumerate(a_deck):
            # 1 if the card is in our hand
            if my_hand.hasCard(a_card.rank.rank, a_card.suit.iden):
                nn_input[i] = 1

            # 2 we played it
            elif me.hasPlayed(a_card.rank.rank, a_card.suit.iden):
                nn_input[i] = 2

            # 3 passed to player 1
            elif me.hasPassed(a_card.rank.rank, a_card.suit.iden):
                if passed_to == 1:
                    nn_input[i] = 3

            # 4 player 1 played
            elif player_1.hasPlayed(a_card.rank.rank, a_card.suit.iden):
                nn_input[i] = 4

            # 5 passed to player 2
            elif me.hasPassed(a_card.rank.rank, a_card.suit.iden):
                if passed_to == 2:
                    nn_input[i] = 5

            # 6 player 2 played
            elif player_2.hasPlayed(a_card.rank.rank, a_card.suit.iden):
                nn_input[i] = 6

            # 7 passed to player 3
            elif me.hasPassed(a_card.rank.rank, a_card.suit.iden):
                if passed_to == 3:
                    nn_input[i] = 7

            # 8 player 3 played
            elif player_3.hasPlayed(a_card.rank.rank, a_card.suit.iden):
                nn_input[i] = 8

            # 0 have not seen the card
            else:
                nn_input[i] = 0

        # make all numbers between 0 and 1
        nn_input = np.true_divide(nn_input, 8)

        trick = game_info.currentTrick.trick

        # fill in what the trick looks like so far, 0 it has not been played, value is the card value
        for i in range(4):
            try:
                card_played = trick[i]
                card_val = (4 * card_played.suit + 13 * card_played.rank) / 52
                nn_input[i + 52] = card_val
            except:
                nn_input[i + 52] = 0

        # fill in the score for each player in the game
        for i in range(4):
            # total score
            nn_input[i + 56] = players[i].score
            nn_input[i + 60] = players[i].currentScore

        return nn_input

    def make_legal_layer(self, me, hb, tn, suit_lead):

        # diagnol matrix: 1 if legal 0 if not
        legal_plays = np.zeros((1, 52, 52))

        # 1 if legal 0 if not
        loss_legal_plays = np.zeros((52,))

        a_deck = Deck().deck

        my_hand = me.hand
        for i, a_card in enumerate(a_deck):
            suit = a_card.suit
            rank = a_card.rank.rank
            # we have the 2 of clubs
            if my_hand.hasCard(2, 0) and (rank == 2) and suit == 0:
                legal_plays[0, i, i] = 1
                loss_legal_plays[i] = 1
            # we don't have the 2 of clubs
            else:
                try:
                    # we have the suit that was lead
                    if me.hasSuit(suit_lead):
                        if my_hand.hasCard(rank, suit.iden) and suit == suit_lead:
                            legal_plays[0, i, i] = 1
                            loss_legal_plays[i] = 1

                    # we don't have the suit lead
                    else:
                        # it's the first trick we cannot play hearts
                        if tn == 0:
                            if my_hand.hasCard(rank, suit.iden) and suit.iden != 3:
                                legal_plays[0, i, i] = 1
                                loss_legal_plays[i] = 1
                        else:
                            if my_hand.hasCard(rank, suit.iden):
                                legal_plays[0, i, i] = 1
                                loss_legal_plays[i] = 1
                # we are leading
                except:
                    if my_hand.hasCard(rank, suit.iden):
                        # leading hearts
                        if suit.iden != 3 or hb:
                            legal_plays[0, i, i] = 1
                            loss_legal_plays[i] = 1
        # store values for later loss
        self.legal_loss_plays = loss_legal_plays
        return legal_plays

    @staticmethod
    def convert_prediction_to_card(prediction):
        prediction = prediction[0].flatten()
        one_pred = argmax(prediction)
        suit = int(one_pred / 13)
        rank = int((one_pred % 13) + 2)

        return Card(rank, suit)

    # game_info is of class AIInfo
    def predict(self, heartsBroken = False, trick_num=0, game_info=None):
        nn_input = self.make_input(game_info)

        self.inputs.append(nn_input)
        # TODO make sure that this is the correct hand
        me = game_info.players[game_info.playerPos]
        layer = self.model.get_layer('legal_moves')
        legal_weights = self.make_legal_layer(me, heartsBroken, trick_num,  game_info.currentTrick.suit)
        layer.set_weights(legal_weights)
        nn_input = nn_input.reshape(1,64)
        prediction = self.model.predict(nn_input)

        return self.convert_prediction_to_card(prediction)

    # not sure how we are going to connect score from game to the network to keep gradient
    def train(self, scores):
        # best score is 0 so temporarily make list as long as scores of zeros
        y_opt = np.zeros_like(scores)

        # currently won't work because we cannot update the legal_moves set to the correct weights
        self.model.fit(self.inputs, [y_opt, self.legal_loss_plays],
                       batch_size=13,
                       epochs=1)

        # save the new weights to folder to bring up again
        self.model.sample_weights('simple_play_weights.h5')

import keras
from keras.layers import Dense, Input, Conv1D
from keras.models import Model
from keras.optimizers import Adam
import keras.backend as K
import numpy as np
import os
from Deck import Deck


class PolicyGradientModel(object):
    def __init__(self, lr, gamma=0.99, numActions=52, layer1Size = 512, layer2Size=256, layer3Size=128, inputSize=164, fname='models/policy/policy.h5'):
        self.gamma = gamma
        self.lr = lr
        self.G = 0  #discouted sum of rewards over each timestep
        self.input_dims = inputSize
        self.fc1_dim = layer1Size
        self.fc2_dim = layer2Size
        self.fc3_dim = layer3Size
        self.numActions = numActions
        self.state_memory = []
        self.action_memory = []
        self.reward_memory = []

        self.loss_policy = []

        self.policy, self.predict = self.build_policy_network()
        self.action_space = [i for i in range(numActions)]
        self.model_file = fname
        if os.path.exists(self.model_file):
            print("loading model")
            self.load_model()

    def build_policy_network(self):
        card_input = Input(shape=(self.input_dims - 13, 1))
        card_conv = Conv1D(filters=1, kernel_size=3, strides=3)(card_input)
        other_input = Input(shape=(13, 1))
        advantages = Input(shape=[1])
        x = keras.layers.concatenate([card_conv, other_input], axis=1)
        f = keras.layers.Flatten()(x)
        layer1 = Dense(512, activation='relu')(f)
        layer2 = Dense(256, activation='relu')(layer1)
        layer3 = Dense(256, activation='relu')(layer2)
        layer4 = Dense(128, activation='relu')(layer3)
        skip_layer = keras.layers.concatenate([f, layer4])
        layer5 = Dense(128, activation='sigmoid')(skip_layer)
        # layer6 = Dense(self.fc2_dim, activation='relu')(layer5)
        outputLayer = Dense(self.numActions, activation='softmax')(layer5)

        def customLoss(y_true, y_pred):
            out = K.clip(y_pred, 1e-8, 1-1e-8)
            log_lik = y_true * K.log(out)

            return K.sum(-log_lik * advantages)

        policy = Model(input=[card_input, other_input, advantages], output=[outputLayer])
        policy.compile(optimizer=Adam(lr=self.lr), loss=customLoss)

        prediction = Model(input=[card_input, other_input], output=[outputLayer])

        return policy, prediction

    def choose_action(self, game_state, legal_plays):
        # reformat the input and predict the probabilities of each action
        state = self.make_input(game_state)
        card_input = state[0].reshape((1, -1, 1))
        other_input = state[1].reshape((1, -1, 1))
        #save the state
        self.state_memory.append(state)

        #predict the probabilities of each action
        probabilities = self.predict.predict([card_input, other_input])[0]


        #get rid of probabilites that arent in our hand
        plays = self.convert_card_to_num(legal_plays)
        for i in range(len(probabilities)):
            if i not in plays:
                probabilities[i] = 0

        playProbs = probabilities[plays]
        minProb = np.min(playProbs)

        #for legal plays with probability of 0 initially
        #add a very small amount to they could theoretically be choosen
        #handles cases where all legal plays are 0 for whatever reason...
        if(minProb == 0):
            size = np.nonzero(playProbs)
            if(len(size[0]) > 0):
                minProb = np.min(playProbs[np.nonzero(playProbs)]) / 100000
                probabilities[plays] += minProb
            else:
                probabilities[plays] += (1 / len(plays))
                print("no guess")


        # remap the probabilities based on legal_plays
        sum = np.sum(probabilities)
        probabilities = probabilities / sum

        # print(probabilities)


        #chooses a random action based on the probabilities of the prediction
        #allows for exploration
        action = np.random.choice(self.action_space, p=probabilities)

        #save the action
        self.action_memory.append(action)

        #converts choice to the given card
        suit = int(action / 13)
        rank = int((action % 13))
        card = Deck.index_to_rank(rank) + Deck.index_to_suit(suit)

        #return the chosen card
        return card

    #store the states, actions and rewards
    def store_transition(self, state, action, reward):
        self.action_memory.append(action)
        self.state_memory.append(state)
        self.reward_memory.append(reward)

    def store_reward(self, reward):
        self.reward_memory.append(reward)

    def learn(self):
        state_memory = np.array(self.state_memory)
        action_memory = np.array(self.action_memory)
        reward_memory = np.array(self.reward_memory)

        #Creates a one hot encoding of the actions
        actions = np.zeros([len(action_memory), self.numActions])
        actions[np.arange(len(action_memory)), action_memory] = 1

        #get the sum rewards based off the reward memory
        G = np.zeros_like(reward_memory)
        for t in range(len(reward_memory)):
            G_sum = 0
            discount = 1

            for k in range(t, len(reward_memory)):
                G_sum += reward_memory[k] * discount
                discount *= self.gamma

            G[t] = G_sum

        #update G
        # mean = np.mean(G)
        # std = np.std(G) if np.std(G) > 0 else 1
        # self.G = (G - mean)/std
        self.G = G
        # print(self.G)

        cost = self.policy.train_on_batch([np.concatenate(state_memory[:, 0]).reshape((-1, 156, 1)),
                                           np.concatenate(state_memory[:, 1]).reshape((-1, 13, 1)),
                                           self.G], actions)
        self.loss_policy.append(cost)

        self.state_memory = []
        self.action_memory = []
        self.reward_memory = []

    def save_model(self):
        self.policy.save_weights(self.model_file)

    def load_model(self):
        self.policy.load_weights(self.model_file)

    def convert_card_to_num(self, legal_plays):
        legal_plays_index = []
        for card in legal_plays:
            # 1 if the card is in our hand
            suit = card[-1:]
            rank = card[:-1]

            suitNum = Deck.suit_index(suit)
            rankNum = Deck.rank_index(rank)

            index = (suitNum * 13) + rankNum

            legal_plays_index.append(index)

        return legal_plays_index

    def make_input(self, game_info):
        card_input = np.zeros((156,))
        other_input = np.zeros((13,))

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
                card_input[i * 3] = 1
            elif a_card in trick.trick:
                card_input[i * 3 + 2] = 1
            elif player_1.has_played(a_card) or player_2.has_played(a_card) or player_3.has_played(a_card) \
                    or me.has_played(a_card):
                card_input[i * 3 + 1] = 1

        # fill in the score for each player in the game
        for i in range(4):
            # total score
            other_input[2 * i] = players[i].score
            other_input[2 * i + 1] = players[i].currentScore

        # encode leading suit
        if trick.suit == 'x':
            other_input[8] = 1
        else:
            other_input[9 + Deck.suit_index(trick.suit)] = 1

        return card_input, other_input

    @staticmethod
    def rotate(players, num_rotate):
        np_players = np.array(players)

        np_players = np.roll(np_players, -1 * num_rotate)

        players = np_players.tolist()

        return players

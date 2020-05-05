from keras.layers import Dense, Activation, Input
from keras.models import Model, load_model
from keras.optimizers import Adam
import keras.backend as K
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



class Agent(object):
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


    def build_policy_network(self):
        input = Input(shape=(self.input_dims,))
        advantages = Input(shape=[1])
        layer1 = Dense(self.fc1_dim, activation='relu')(input)
        layer2 = Dense(self.fc1_dim, activation='sigmoid')(layer1)
        layer3 = Dense(self.fc2_dim, activation='relu')(layer2)
        layer4 = Dense(self.fc2_dim, activation='sigmoid')(layer3)
        layer5 = Dense(self.fc3_dim, activation='relu')(layer4)
        # layer6 = Dense(self.fc2_dim, activation='relu')(layer5)
        outputLayer = Dense(self.numActions, activation='softmax')(layer5)

        def customLoss(y_true, y_pred):
            out = K.clip(y_pred, 1e-8, 1-1e-8)
            log_lik = y_true * K.log(out)

            return K.sum(-log_lik * advantages)

        policy = Model(input=[input, advantages], output=[outputLayer])
        policy.compile(optimizer=Adam(lr=self.lr), loss=customLoss)

        prediction = Model(input=[input], output=[outputLayer])

        return policy, prediction

    def choose_action(self, game_state, legal_plays):
        # reformat the input and predict the probabilities of each action
        state = self.make_input(game_state)
        nn_input = state[np.newaxis, :]

        #save the state
        self.state_memory.append(state)

        #predict the probabilities of each action
        probabilities = self.predict.predict(nn_input)[0]


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

    #TODO dont know where to have the model learn based on what we have rn
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


        cost = self.policy.train_on_batch([state_memory, self.G], actions)
        self.loss_policy.append(cost)

        self.state_memory = []
        self.action_memory = []
        self.reward_memory = []

    def save_model(self):
        self.policy.save(self.model_file)

    def load_model(self):
        self.policy = load_model(self.model_file)


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

    # def make_input(self, game_info):
    #     nn_input = np.zeros((64,))
    #
    #     # rotate us so we are player 0
    #     players = game_info.players
    #     player_pos = game_info.playerPos
    #     players = self.rotate(players, player_pos)
    #
    #     me = players[0]
    #     my_hand = me.hand
    #     i_played = me.cardsPlayed
    #     i_passed = me.passedCards[:3]
    #     player_1 = players[1]
    #     player_2 = players[2]
    #     player_3 = players[3]
    #     passed_to = me.passedCards[3] - player_pos
    #
    #     if passed_to < 0:
    #         passed_to += 4
    #
    #     a_deck = Deck().deck
    #
    #     # elements 0-51 represent one card in the deck, the value represents where the card is
    #     for i, a_card in enumerate(a_deck):
    #         # 1 if the card is in our hand
    #         suit = a_card[-1:]
    #         rank = a_card[:-1]
    #         if my_hand.hasCard(a_card):
    #             nn_input[i] = 1
    #
    #         # 2 we played it
    #         elif me.has_played(a_card):
    #             nn_input[i] = 2
    #
    #         # 3 passed to player 1
    #         elif me.has_passed(a_card):
    #             if passed_to == 1:
    #                 nn_input[i] = 3
    #
    #         # 4 player 1 played
    #         elif player_1.has_played(a_card):
    #             nn_input[i] = 4
    #
    #         # 5 passed to player 2
    #         elif me.has_passed(a_card):
    #             if passed_to == 2:
    #                 nn_input[i] = 5
    #
    #         # 6 player 2 played
    #         elif player_2.has_played(a_card):
    #             nn_input[i] = 6
    #
    #         # 7 passed to player 3
    #         elif me.has_passed(a_card):
    #             if passed_to == 3:
    #                 nn_input[i] = 7
    #
    #         # 8 player 3 played
    #         elif player_3.has_played(a_card):
    #             nn_input[i] = 8
    #
    #         # 0 have not seen the card
    #         else:
    #             nn_input[i] = 0
    #
    #     # make all numbers between 0 and 1
    #     nn_input = np.true_divide(nn_input, 8)
    #
    #     trick = game_info.trick
    #
    #     # fill in what the trick looks like so far, 0 it has not been played, value is the card value
    #     for i in range(4):
    #         try:
    #             card_played = trick[i]
    #             card_val = (4 * card_played.suit + 13 * card_played.rank) / 52
    #             nn_input[i + 52] = card_val
    #         except:
    #             nn_input[i + 52] = 0
    #
    #     # fill in the score for each player in the game
    #     for i in range(4):
    #         # total score
    #         nn_input[i + 56] = players[i].score
    #         nn_input[i + 60] = players[i].currentScore
    #
    #     return nn_input

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
            elif player_1.has_played(a_card) or player_2.has_played(a_card) or player_3.has_played(a_card) \
                    or me.has_played(a_card):
                nn_input[i * 3 + 1] = 1

        # fill in the score for each player in the game
        for i in range(4):
            # total score
            nn_input[i + 156] = players[i].score
            nn_input[i + 160] = players[i].currentScore

        return nn_input

    @staticmethod
    def rotate(players, num_rotate):
        np_players = np.array(players)

        np_players = np.roll(np_players, -1 * num_rotate)

        players = np_players.tolist()

        return players

from keras.layers import Dense, Activation, Input, Lambda
from keras.models import Model, load_model
from keras.optimizers import Adam
import keras.backend as K
import numpy as np
from Deck import Deck


COUNT = 0
num_cards = 52

def renormalize_function(params):
    probas, legal_plays = params

    # Kill illegal plays
    probas = (probas + 1e-5) * legal_plays


    return probas / (K.sum(probas))
    
# sampled_enc = Lambda(renormalize_function, output_shape = (enc_out, ))((mean, log_var))


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

def get_card_ix(card):
    return from_card_to_target(card) - 1

class Agent(object):
    def __init__(self, lr, gamma=0.99, numActions=52, layer1Size = 256, layer2Size=128, inputSize=num_cards * 3 + 8, fnames=['models/actor_critic/actor.h5', 'models/actor_critic/critic.h5']):
        self.gamma = gamma
        self.lr = lr
        self.G = 0  #discouted sum of rewards over each timestep
        self.input_dims = inputSize
        self.fc1_dim = layer1Size
        self.fc2_dim = layer2Size
        self.numActions = numActions
        self.state_memory = []
        self.action_memory = []
        self.reward_memory = []
        self.values_memory = []
        self.legal_plays = []

        self.loss_actor = []
        self.loss_critic = []


        self.actor, self.actor_trainer, self.critic = self.build_policy_network()
        self.action_space = [i for i in range(numActions)]
        self.model_file = fnames


    def build_policy_network(self):
        input = Input(shape=(self.input_dims,), name="Input_nn")
        advantages = Input(shape=[1], name="Advantages")
        legal_plays = Input(shape=[num_cards,], name="Legal_plays")
        
        actor_1 = Dense(self.fc1_dim, activation='relu', name="actor_dense_1")(input)
        actor_2 = Dense(self.fc1_dim, activation='relu', name="actor_dense_2")(actor_1)
        actor_pre = Dense(self.numActions, activation='softmax', name="actor_dense_3_soft")(actor_2)
        actor_out = Lambda(renormalize_function, output_shape = (self.numActions, ))([actor_pre, legal_plays])


        critic_1 = Dense(self.fc1_dim, activation='relu')(input)
        critic_2 = Dense(self.fc1_dim, activation='relu')(critic_1)
        critic_out = Dense(1, activation='linear')(critic_2)


        def customLoss_actor(y_true, y_pred):
            out = K.clip(y_pred, 1e-8, 1-1e-8)
            log_lik = y_true * K.log(out)

            return K.sum(- log_lik * advantages)

        actor = Model(input=[input, legal_plays], output=[actor_out])
        actor.compile(optimizer=Adam(lr=self.lr), loss=customLoss_actor)

        actor_trainer = Model(input=[input, legal_plays, advantages], output=[actor_out])
        actor_trainer.compile(optimizer=Adam(lr=self.lr), loss=customLoss_actor)


        critic = Model(input=[input], output=[critic_out])
        critic.compile(optimizer=Adam(lr=self.lr), loss="mean_squared_error")

        return actor, actor_trainer, critic

    def choose_action(self, game_state, legal_plays):
        # reformat the input and predict the probabilities of each action
        legal_plays = self.convert_legal_plays_to_array(legal_plays)

        state = self.make_input(game_state)
        nn_input = state[np.newaxis, :]

        #save the state
        self.state_memory.append(state)
        self.legal_plays.append(legal_plays)
        legal_plays = legal_plays.reshape(1, -1)
        #predict the probabilities of each action
        probabilities = self.actor.predict([nn_input, legal_plays])[0]
        value = self.critic.predict(nn_input)[0]
        self.values_memory.append(value)


        #chooses a random action based on the probabilities of the prediction
        #allows for exploration
        try :
            action = np.random.choice(self.action_space, p=probabilities)
        except ValueError:
            print(probabilities)
            print(legal_plays)
            exit()
        #save the action
        self.action_memory.append(action)

        #converts choice to the given card
        suit = int(action / 13)
        rank = int((action % 13))
        card = Deck.index_to_rank(rank) + Deck.index_to_suit(suit)

        #return the chosen card
        return card

    #store the states, actions and rewards
    def store_transition(self, state, action, reward, value):
        self.action_memory.append(action)
        self.state_memory.append(state)
        self.reward_memory.append(reward)
        self.values_memory.appnd(value)

    def store_reward(self, reward):
        self.reward_memory.append(reward)

    #TODO dont know where to have the model learn based on what we have rn
    def learn(self):
        state_memory = np.array(self.state_memory)
        action_memory = np.array(self.action_memory)
        reward_memory = np.array(self.reward_memory)
        values_memory = np.array(self.values_memory)
        legal_plays_memory = np.array(self.legal_plays)

        final_Q_value = 26 - (state_memory[-1][3*num_cards + 4] + reward_memory[-1]) #My score

        if np.any(reward_memory < 0):
            print("Negative", reward_memory)
            exit()

        #Creates a one hot encoding of the actions
        actions = np.zeros([len(action_memory), self.numActions])
        actions[:, action_memory] = 1

        #get the sum rewards based off the reward memory
        Q_values = np.zeros_like(values_memory) ## Ground truth
        Q_val = final_Q_value
        for t in reversed(range(len(reward_memory))):
            Q_val = reward_memory[t] + self.gamma * Q_val
            Q_values[t] = Q_val


        advantages = Q_values - values_memory

        #Normalize advantages
        mean = np.mean(advantages)
        std = np.std(advantages) if np.std(advantages) > 0 else 1
        self.advantages = (advantages - mean)/std

        # Train actor
        loss_actor = self.actor_trainer.train_on_batch([state_memory, legal_plays_memory, self.advantages], actions)
        self.loss_actor.append(loss_actor)
        # Train critic
        loss_critic = self.critic.train_on_batch([state_memory], Q_values)
        self.loss_critic.append(loss_critic)


        self.state_memory = []
        self.action_memory = []
        self.reward_memory = []
        self.values_memory = []
        self.legal_plays = []

    def save_model(self):
        self.actor.save(self.model_file[0])
        self.critic.save(self.model_file[1])

    def load_model(self):
        self.actor = load_model(self.model_file[0])
        self.critic = load_model(self.model_file[1])


    def convert_legal_plays_to_array(self, legal_plays):

        legal_plays_index = []
        for card in legal_plays:
            # 1 if the card is in our hand
            suit = card[-1:]
            rank = card[:-1]

            suitNum = Deck.suit_index(suit)
            rankNum = Deck.rank_index(rank)

            index = (suitNum * 13) + rankNum

            legal_plays_index.append(index)
    
        legal_plays_array = np.zeros(num_cards)
        legal_plays_array[legal_plays_index] = 1

        return legal_plays_array

    def make_input(self, game_info):

        # rotate us so we are player 0
        players = game_info.players
        player_pos = game_info.playerPos
        players = self.rotate(players, player_pos)

        me = players[0]
        my_hand = me.hand
        player_1 = players[1]
        player_2 = players[2]
        player_3 = players[3]

        a_deck = Deck().deck

        # one hot instead keeping it simple first
        hand = np.zeros(num_cards)
        played_cards = np.zeros(num_cards)
        cards_on_board = np.zeros(num_cards)

        for i, a_card in enumerate(a_deck):

            if my_hand.hasCard(a_card):
                hand[i] = 1
            elif player_1.has_played(a_card) or player_2.has_played(a_card) or player_3.has_played(a_card):
                played_cards[i] = 1

        trick = game_info.trick

        # fill in what the trick looks like so far, 0 it has not been played, value is the card value
        for i in range(4):
            if trick.trick[i] == 0:
                continue
            card_ix = get_card_ix(trick.trick[i])
            cards_on_board[card_ix] = 1

        # fill in the score for each player in the game
        scores = [pl.score for pl in players] + [pl.currentScore for pl in players]

        nn_input = np.concatenate((played_cards, hand, cards_on_board, scores))

        return nn_input

    @staticmethod
    def rotate(players, num_rotate):
        np_players = np.array(players)

        np_players = np.roll(np_players, -1 * num_rotate)

        players = np_players.tolist()

        return players

import numpy as np

num_cards = 4 * 3
ILLICIT_PLAY_PENALTY = -10
VALID_PLAY_REWARD = 0

def pad(array):
    return np.append(array, np.zeros(4) - 1)[:4]
class ActionSpace():
    def __init__(self):
        self.n = num_cards

class Game():
    def __init__(self, num_cards=num_cards):
        self.reset()
        self.observation_space = np.zeros(3 * num_cards)
        self.action_space = ActionSpace()
    
    def reset(self):
        self.cards_played = np.zeros((num_cards))
        self.hand = np.zeros((num_cards))

        choose_hand = np.random.choice(num_cards, int(num_cards / 4), replace=False)
        self.hand[choose_hand] = 1

        self.cards_on_board = np.array([k for k in range(np.random.randint(1, 4))])
        self.cards_on_board = self.choose_card_on_board()

        return self.env()

    def env(self):
        return np.concatenate([self.cards_played, self.hand, self.hot_hand()])

    def choose_card_on_board(self):
        possible_board = self.get_possible_moves_others()

        board =  np.random.choice(possible_board, size = (self.cards_on_board.shape[0] + 1)%4, replace=False)
        self.cards_played[board] = 1
        return board


    def get_possible_moves_others(self):
        indices_not_played = set(np.where(self.cards_played== 0)[0])
        hand = set(np.where(self.hand==1)[0])

        return list(indices_not_played.difference(hand))

    def step(self, card_ix):
        return self.play(card_ix)

    def hot_hand(self):
        res = np.zeros(num_cards)
        res[self.cards_on_board] = 1

        return res

    def play(self, card_ix):
        if not self.hand[card_ix]:
            return np.concatenate([self.cards_played, self.hand, self.hot_hand()]), ILLICIT_PLAY_PENALTY, False, 0 # IDK what the last parameter is in the gym library
        
        self.hand[card_ix] = 0
        self.cards_played[card_ix] = 1

        for _ in range(3 - self.cards_on_board.shape[0]):
            other_player_choice = np.random.choice(self.get_possible_moves_others(), size=1)
            self.cards_played[other_player_choice] = 1
        
        done = self.cards_played.sum() == num_cards

        if not done:
            self.cards_on_board = self.choose_card_on_board()

        reward = self.get_reward() # Returns random values

        return np.concatenate([self.cards_played, self.hand, self.hot_hand()]), reward, done, 0

    def get_reward(self):
        return VALID_PLAY_REWARD #np.random.randint(-10, 0) To learn how to play without mistakes


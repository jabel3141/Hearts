from Hand import Hand
from Deck import Deck


class Player:
    def __init__(self, name):
        if type(self) == Player:
            raise Exception("Player is an abstract class.")

        self.name = name
        self.hand = Hand()
        self.score = 0
        self.tricksWon = []
        self.currentScore = 0
        self.cardsPlayed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.passedCards = [0, 0, 0, 0]  # last one is which player it was passed to

    def reset(self):
        self.score = 0
        self.tricksWon = []
        self.currentScore = 0
        self.cardsPlayed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.passedCards = [0, 0, 0, 0]  # last one is which player it was passed to

    def add_card(self, card):
        self.hand.add_card(card)

    def get_input(self, option):
        card = None
        while card is None:
            card = input(self.name + ", select a card to " + option + ": ")
        return card

    def pass_cards(self, pass_distance, num_passed):
        self.passedCards[3] = pass_distance
        card = self.select_pass_card()
        self.passedCards[num_passed] = card
        return card

    def select_pass_card(self):
        pass

    def play(self, game_state, c=None):
        if c is None:
            card = self.select_play_card(game_state)
        else:
            card = c

        self.cardsPlayed[game_state.trick.trick_num] = card
        return card

    def train(self, reward):
        pass

    def learn(self):
        pass

    def store_reward(self, reward):
        pass

    def select_play_card(self, game_state):
        pass

    def legal_plays(self, game_state):
        if game_state.trick.suit == 'x':
            if game_state.trick.trick_num == 0:  # first trick has not started
                if self.hand.hasCard('2c'):
                    return ['2c']
                print('You are going first but don\'t have the 2 of clubs?')
                return []
            elif not game_state.hearts_broken:
                legal = self.hand.clubs + self.hand.diamonds + self.hand.spades  # All but hearts if possible
                if len(legal) > 0:
                    return legal
                else:
                    return self.hand.hearts
            else:
                return self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts  # all cards
        elif self.has_suit(game_state.trick.suit):
            return self.hand.hand[Deck.suit_index(game_state.trick.suit)]  # Cards of the trick's suit
        elif game_state.trick.trick_num == 0:
            legal = self.hand.clubs + self.hand.diamonds + self.hand.spades
            if 'Qs' in legal:
                legal.remove('Qs')
            if len(legal) > 0:
                return legal  # no points on the first hand if possible
            else:
                return self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts  # all cards
        else:
            return self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts  # all cards

    def trickWon(self, trick):
        self.currentScore += trick.points

    def has_suit(self, suit):
        if suit == 'x':
            return False
        else:
            return len(self.hand.hand[Deck.suit_index(suit)]) > 0

    def removeCard(self, card):
        self.hand.remove_card(card)

    def clearCurrentScore(self):
        self.currentScore = 0

    def discardTricks(self):
        self.tricksWon = []

    def hasOnlyHearts(self):
        return self.hand.hasOnlyHearts()

    def has_played(self, played_card):
        played_suit = played_card[-1:]
        played_rank = played_card[:-1]
        for card in self.cardsPlayed:
            if not type(card) == int:
                suit = card[-1:]
                rank = card[:-1]
                if rank == played_rank and suit == played_suit:
                    return True
        return False

    def has_passed(self, played_card):
        played_suit = played_card[-1:]
        played_rank = played_card[:-1]
        for card in self.passedCards[:-1]:
            suit = card[-1:]
            rank = card[:-1]
            if rank == played_rank and suit == played_suit:
                return True
        return False

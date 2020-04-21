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
		self.passedCards = [0, 0, 0, 0] # last one is which player it was passed to

	def addCard(self, card):
		self.hand.addCard(card)

	def getInput(self, option):
		card = None
		while (card is None):
			card = input(self.name + ", select a card to " + option + ": ")
		return card

	def pass_cards(self, pass_distance, num_passed):
		self.passedCards[3] = pass_distance
		card = self.select_pass_card()
		self.passedCards[num_passed] = card
		return card

	def select_pass_card(self):
		pass

	def play(self, c=None, heartsBroken = False, trick_num=0, game_info=None):
		if c is None:
			card = self.select_play_card(heartsBroken, trick_num, game_info)
		else:
			card = c

		self.cardsPlayed[trick_num] = card
		return card

	def select_play_card(self, heartsBroken = False, trick_num=0, game_info=None):
		pass

	def trickWon(self, trick):
		self.currentScore += trick.points

	def has_suit(self, suit):
		return len(self.hand.hand[Deck.suit_index(suit)]) > 0

	def removeCard(self, card):
		self.hand.removeCard(card)

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
				rank = suit[:-1]
				if rank == played_rank and suit == played_suit:
					return True
		return False

	def has_passed(self, played_card):
		played_suit = played_card[-1:]
		played_rank = played_card[:-1]
		for card in self.passedCards[:-1]:
			suit = card[-1:]
			rank = suit[:-1]
			if rank == played_rank and suit == played_suit:
				return True
		return False

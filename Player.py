from Hand import Hand


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
			card = self.hand.str_to_card(card)

		self.cardsPlayed[trick_num] = card
		return card

	def select_play_card(self, heartsBroken = False, trick_num=0, game_info=None):
		pass

	def trickWon(self, trick):
		self.currentScore += trick.points

	def hasSuit(self, suit):
		return len(self.hand.hand[suit.iden]) > 0

	def removeCard(self, card):
		self.hand.removeCard(card)

	def clearCurrentScore(self):
		self.currentScore = 0

	def discardTricks(self):
		self.tricksWon = []

	def hasOnlyHearts(self):
		return self.hand.hasOnlyHearts()

	def hasPlayed(self, cardRank, suitIden):
		for card in self.cardsPlayed:
			if not type(card) == int:
				if (card.rank.rank == cardRank) and (card.suit.iden == suitIden):
					return True
		return False

	def hasPassed(self, cardRank, suitIden):
		for card in self.passedCards[:-1]:
			if (card.rank.rank == cardRank) and (card.suit.iden == suitIden):
				return True
		return False
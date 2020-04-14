from Hand import Hand


class Player:
	def __init__(self, name, auto=False):
		self.name = name
		self.hand = Hand()
		self.score = 0
		self.tricksWon = []
		self.cardsPlayed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		self.passedCards = [0, 0, 0, 0] # last one is which player it was passed to

	def addCard(self, card):
		self.hand.addCard(card)

	def getInput(self, option):
		card = None
		while (card is None):
			card = input(self.name + ", select a card to " + option + ": ")
		return card

	def play(self, option='play', c=None, auto=False, trickNum=0, passDistance=0, numPassed=0):
		if (auto):
			card = self.hand.getRandomCard()
		elif (c is None):
			card = self.getInput(option)
		else:
			card = c
		if (not auto):
			card = self.hand.playCard(card)

		self.cardsPlayed[trickNum] = card

		if option == 'pass':
			self.passedCards[3] = passDistance
			self.passedCards[numPassed] = card

		return card

	def trickWon(self, trick):
		self.score += trick.points

	def hasSuit(self, suit):
		return len(self.hand.hand[suit.iden]) > 0

	def removeCard(self, card):
		self.hand.removeCard(card)

	def discardTricks(self):
		self.tricksWon = []

	def hasOnlyHearts(self):
		return self.hand.hasOnlyHearts()

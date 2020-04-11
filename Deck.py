import random as rand
from Card import Card

numSuits = 4
minRank = 2
maxRank = 14

class Deck:
	def __init__(self):
		self.deck = []
		for suit in range(0,numSuits):
			for rank in range(minRank,maxRank+1):
				self.deck.append(Card(rank, suit))


	def shuffle(self):
		rand.shuffle(self.deck, rand.random)


	def deal(self):
		return self.deck.pop(0)


	def sort(self):
		self.deck.sort()


	def size(self):
		return len(self.deck)


	def __str__(self):
		deckStr = ''
		for card in self.deck:
			deckStr += card.__str__() + '\n'
		return deckStr
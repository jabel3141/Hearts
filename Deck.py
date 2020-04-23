import random as rand

allSuits = ['c', 'd', 's', 'h']
allRanks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Deck:
	def __init__(self):
		self.deck = []
		for suit in allSuits:
			for rank in allRanks:
				self.deck.append(rank+suit)

	def shuffle(self):
		rand.shuffle(self.deck, rand.random)

	def deal(self):
		return self.deck.pop(0)

	def sort(self):
		self.deck.sort(key=Deck.card_to_sort_val)

	def size(self):
		return len(self.deck)

	def __str__(self):
		deck_str = ''
		for card in self.deck:
			deck_str += card + '\n'
		return deck_str

	@staticmethod
	def suit_index(suit):
		if suit in allSuits:
			return allSuits.index(suit)
		else:
			return None

	@staticmethod
	def index_to_suit(idx):
		return allSuits[idx]

	@staticmethod
	def rank_index(rank):
		if rank in allRanks:
			return allRanks.index(rank)
		else:
			return None

	@staticmethod
	def index_to_rank(idx):
		return allRanks[idx]

	@staticmethod
	def card_to_sort_val(card):
		suit = card[-1:]
		rank = card[:-1]
		val = 0
		val += 100 * Deck.suit_index(suit)
		return val + Deck.rank_index(rank)

	@staticmethod
	def card_rank_to_sort_val(card):
		rank = card[:-1]
		return Deck.rank_index(rank)

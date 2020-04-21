from Deck import Deck

hearts = 3  # the corresponding index to the suit hearts
spades = 2
queen = 12


class Trick:
	def __init__(self):
		self.trick = [0, 0, 0, 0]
		self.suit = 'x'
		self.cardsInTrick = 0
		self.points = 0
		self.highest = None  # rank of the high trump suit card in hand
		self.winner = -1

	def reset(self):
		self.trick = [0, 0, 0, 0]
		self.suit = -1
		self.cardsInTrick = 0
		self.points = 0
		self.highest = 0
		self.winner = -1

	def set_trick_suit(self, card):
		self.suit = card[-1:]

	def add_card(self, card, index):
		suit = card[-1:]
		rank = card[:-1]
		if self.cardsInTrick == 0:  # if this is the first card added, set the trick suit
			self.suit = suit
			print('Current trick suit:', self.suit)
		
		self.trick[index] = card
		self.cardsInTrick += 1

		if suit == 'h':
			self.points += 1
		elif rank == 'Q' and suit == 's':
			self.points += 13

		if suit == self.suit:
			if self.highest is None or self.compare_ranks(rank, self.highest):
				self.highest = rank
				self.winner = index

	@staticmethod
	def compare_ranks(rank1, rank2):
		return Deck.rank_index(rank1) > Deck.rank_index(rank2)

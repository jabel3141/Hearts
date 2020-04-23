from random import randint
from Deck import Deck

clubs = 0
diamonds = 1
spades = 2
hearts = 3
suits = ['c', 'd', 's', 'h']


class Hand:
	def __init__(self):
		self.clubs = []
		self.diamonds = []
		self.spades = []
		self.hearts = []
		
		# create hand of cards split up by suit
		self.hand = [self.clubs, self.diamonds, self.spades, self.hearts]

	def size(self):
		return len(self.clubs) + len(self.diamonds) + len(self.spades) + len(self.hearts)

	def add_card(self, card):
		suit = card[-1:]
		rank = card[:-1]
		if suit == 'c':
			self.clubs.append(card)
		elif suit == 'd':
			self.diamonds.append(card)
		elif suit == 's':
			self.spades.append(card)
		elif suit == 'h':
			self.hearts.append(card)
		else:
			print('Invalid card')

		if self.size() == 13:
			for suit in self.hand:
				suit.sort(key=Deck.card_to_sort_val)

	def getRandomCard(self):
		suit = randint(0,3)
		suit = self.hand[suit]
		while(len(suit) == 0):
			suit = randint(0,3)
			suit = self.hand[suit] 
		index = randint(0, len(suit)-1)

		return suit[index]

	def hasCard(self, played_card):
		suit = played_card[-1:]
		rank = played_card[:-1]
		for card in self.hand[Deck.suit_index(suit)]:
			if card[:-1] == rank:
				return True
		return False

	def remove_card(self, card):
		suit = card[-1:]

		suit_index = Deck.suit_index(suit)
		if suit_index is None:
			print('Invalid Suit')
			return None

		for c in self.hand[suit_index]:
			if c == card:
				self.hand[suit_index].remove(c)

	def hasOnlyHearts(self):
		return len(self.hearts) == self.size()

	def __str__(self):
		hand_str = ''
		for suit in self.hand:
			for card in suit:
				hand_str += card.__str__() + ' '
		return hand_str

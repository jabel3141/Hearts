from Deck import Deck
from RandomAI import RandomAI
from HumanAI import HumanAI
from Trick import Trick
from AIInfo import AIInfo
from SimpleNN import SimpleNN

'''
Change auto to False if you would like to play the game manually.
This allows you to make all passes, and plays for all four players.
When auto is True, passing is disabled and the computer plays the
game by "guess and check", randomly trying moves until it finds a
valid one.
'''
totalTricks = 13
maxScore = 100
queen = 12
noSuit = 0
spades = 2
hearts = 3
cardsToPass = 3


class Hearts:
	def __init__(self):
		self.roundNum = 0
		self.trickNum = 0  # initialization value such that first round is round 0
		self.dealer = -1  # so that first dealer is 0
		self.passes = [1, -1, 2, 0]  # left, right, across, no pass
		self.currentTrick = Trick()
		self.trickWinner = -1
		self.heartsBroken = False
		self.losingPlayer = None
		self.passingCards = [[], [], [], []]
		# the score of the game
		self.scoreboard = [0, 0, 0, 0]

		# Make four players
		self.players = [RandomAI("Jason"), SimpleNN("Jack"), RandomAI("Sam"), RandomAI("JB")]

		'''
		Player physical locations:
		Game runs clockwise
			p3
		p2		p4
			p1
		'''

		# Generate a full deck of cards and shuffle it
		self.newRound()

	def handleScoring(self):
		p, highestScore = None, 0
		print("\n=====Scores=====")

		tempScores = []

		for aPlayer in self.players:
			tempScores.append(aPlayer.currentScore)

		if 26 in tempScores:
			player_shoot = tempScores.index(26)
			for i, player in enumerate(self.players):
				if i != player_shoot:
					player.score += 26
		else:
			for a_player in self.players:
				a_player.score += a_player.currentScore


		for i, player in enumerate(self.players):
			print(player.name + ": " + str(player.score))
			self.scoreboard[i] = player.score
			if player.score > highestScore:
				p = player
				highestScore = player.score
			self.losingPlayer = p

	def newRound(self):
		self.deck = Deck()
		self.deck.shuffle()
		self.dealCards()
		self.roundNum += 1
		self.trickNum = 0
		self.trickWinner = -1
		self.heartsBroken = False
		self.dealer = (self.dealer + 1) % len(self.players)
		self.currentTrick = Trick()
		self.passingCards = [[], [], [], []]
		for p in self.players:
			p.discardTricks()
			p.clearCurrentScore()

	def dealCards(self):
		i = 0
		while self.deck.size() > 0:
			self.players[i % len(self.players)].addCard(self.deck.deal())
			i += 1

	def passCards(self, index):
		passTo = self.passes[(self.roundNum - 1) % 4]  # how far to pass cards
		passTo = (index + passTo) % len(self.players)  # the index to which cards are passed

		for i in range(cardsToPass):
			passCard = None
			while passCard is None:  # make sure string passed is valid
				passCard = self.players[index].pass_cards(passTo, i)
				if passCard is not None:
					# remove card from player hand and add to passed cards
					self.passingCards[passTo].append(passCard)
					self.players[index].removeCard(passCard)

		print(self.players[index].name + " is passing " + self.printPassingCards(passTo) + " to " + self.players[
			passTo].name)

	def distributePassedCards(self):
		for i, passed in enumerate(self.passingCards):
			for card in passed:
				self.players[i].addCard(card)

	def printPassingCards(self, playerIndex):
		out = "[ "
		for card in self.passingCards[playerIndex]:
			out += card.__str__() + " "
		out += "]"
		return out

	def playersPassCards(self):
		if self.roundNum % 4 != 0:  # Don't pass on round 4
			print("All player's hands before passing")
			self.printPlayers()

			for i in range(0, len(self.players)):
				print()  # spacing
				curPlayer = self.players[i]
				print(curPlayer.name + "'s hand: " + str(curPlayer.hand))
				self.passCards(i)

			self.distributePassedCards()
			print()
			print("All player's hands after passing")
			self.printPlayers()

	def getFirstTrickStarter(self):
		for i, p in enumerate(self.players):
			if p.hand.hasCard('2c'):
				self.trickWinner = i

	def evaluateTrick(self):
		self.trickWinner = self.currentTrick.winner
		p = self.players[self.trickWinner]
		p.trickWon(self.currentTrick)
		self.printCurrentTrick()
		print(p.name + " won the trick.")
		# print 'Making new trick'
		self.currentTrick = Trick()
		print()

	def getWinner(self):
		minScore = 200  # impossibly high
		winner = []
		for p in self.players:
			if p.score < minScore:
				winner = []
				winner.append(p)
				minScore = p.score
			elif p.score == minScore:
				winner.append(p)
		return winner

	def playTrick(self, start):
		shift = 0
		if self.trickNum == 0:
			startPlayer = self.players[start]
			played_card = startPlayer.play(c='2c')
			print(played_card)
			startPlayer.removeCard(played_card)

			self.currentTrick.add_card(played_card, start)

			shift = 1  # alert game that first player has already played

		# have each player take their turn
		for i in range(start + shift, start + len(self.players)):

			self.printCurrentTrick()
			curPlayerIndex = i % len(self.players)
			curPlayer = self.players[curPlayerIndex]
			print(curPlayer.name + "'s hand: " + str(curPlayer.hand))
			played_card = None

			important_info = AIInfo(curPlayerIndex, self.currentTrick, self.players)

			while played_card is None:  # wait until a valid card is passed

				played_card = curPlayer.play(trick_num=self.trickNum, game_info=important_info)
				suit = played_card[-1:]
				rank = played_card[:-1]

				# the rules for what cards can be played
				# card set to None if it is found to be invalid
				if played_card is not None:

					# if it is not the first trick and no cards have been played,
					# set the first card played as the trick suit if it is not a heart
					# or if hearts have been broken
					if self.trickNum != 0 and self.currentTrick.cardsInTrick == 0:
						if suit == 'h' and not self.heartsBroken:
							# if player only has hearts but hearts have not been broken,
							# player can play hearts
							if not curPlayer.hasOnlyHearts():
								print("Hearts have not been broken.")
								played_card = None
							else:
								self.currentTrick.set_trick_suit(played_card)
						else:
							self.currentTrick.set_trick_suit(played_card)

					# check if card played in first trick is not a heart or qs
					if self.trickNum == 0:
						if played_card is not None:
							if suit == 'h':
								print("Hearts cannot be played on the first hand.")
								played_card = None
							elif suit == 's' and rank == 'Q':
								print("The queen of spades cannot be played on the first hand.")
								played_card = None

					# player tries to play off suit but has trick suit
					if played_card is not None and suit != self.currentTrick.suit:
						if curPlayer.has_suit(self.currentTrick.suit):
							print("Must play the suit of the current trick.")
							played_card = None
						elif suit == 'h':
							self.heartsBroken = True

					if played_card is not None:
						if rank == 'Q' and suit == 's':
							self.heartsBroken = True
						curPlayer.removeCard(played_card)

			self.currentTrick.add_card(played_card, curPlayerIndex)

		self.evaluateTrick()
		self.trickNum += 1

	# print all players' hands
	def printPlayers(self):
		for p in self.players:
			print(p.name + ": " + str(p.hand))

	# show cards played in current trick
	def printCurrentTrick(self):
		if self.currentTrick.cardsInTrick == 4:
			trickStr = '\n=====Final Trick=====\n'
		else:
			trickStr = '\n=====Current Trick=====\n'
		trickStr += "Trick suit: " + self.currentTrick.suit.__str__() + "\n"
		for i, card in enumerate(self.currentTrick.trick):
			if self.currentTrick.trick[i] is not 0:
				trickStr += self.players[i].name + ": " + str(card) + "\n"
			else:
				trickStr += self.players[i].name + ": None\n"
		print(trickStr)


def main():
	hearts = Hearts()

	# play until someone loses
	while hearts.losingPlayer is None or hearts.losingPlayer.score < maxScore:
		print("====================Round " + str(hearts.roundNum) + "====================")

		while hearts.trickNum < totalTricks:
			if hearts.trickNum == 0:
				hearts.playersPassCards()
				hearts.getFirstTrickStarter()
			print('\n==========Trick number ' + str(hearts.trickNum + 1) + '==========')
			hearts.playTrick(hearts.trickWinner)

		# tally scores
		hearts.handleScoring()
		print()

		# new round if no one has lost
		if (hearts.losingPlayer.score < maxScore):
			hearts.newRound()

	print()  # spacing
	winners = hearts.getWinner()
	winnerString = ""
	for w in winners:
		winnerString += w.name + " "
	print(winnerString + "wins!")


if __name__ == '__main__':
	main()

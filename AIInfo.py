import Hand
import Card
import Trick


class AIInfo:

    def __init__(self, scoreboard, playerPos, currentTrick, players):
        self.scoreboard = scoreboard  # the score of the game
        self.playerPos = playerPos  # player who's turn it currently is
        self.currentTrick = currentTrick  # what the trick looks like on the board so far
        self.players = players  # all of the players in the game

    def getPlayerHand(self):
        return self.players[self.playerPos].hand

    def getCurrentScore(self):
        tempScores = []

        for aPlayer in self.players:
            tempScores.append(aPlayer.handScore)

        return tempScores
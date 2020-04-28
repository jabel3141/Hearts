class GameState:
    def __init__(self, player_pos, trick, hearts_broken, players):
        self.playerPos = player_pos  # player who's turn it currently is
        self.trick = trick  # current trick
        self.players = players  # all of the players in the game
        self.hearts_broken = hearts_broken

    def getCurrentScore(self):
        tempScores = []

        for aPlayer in self.players:
            tempScores.append(aPlayer.currentScore)

        return tempScores
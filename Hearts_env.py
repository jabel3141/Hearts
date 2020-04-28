from Hearts import Hearts
from Trick import Trick

max_score = 100
total_tricks = 13
epochs = 100000


class Hearts_env:

    def __init__(self):
        self.hearts_game = Hearts()
        os.makedirs('models/qlearn', exist_ok=True)

    def get_reward(self, player_pos):
        score = self.hearts_game.players[player_pos].currentScore
        if score == 26:
            return 78
        opp_score = 0
        for i, p in enumerate(self.hearts_game.players):
            if p.currentScore == 26:
                return -52
            if i != player_pos:
                opp_score += p.currentScore

        reward = score * -4 + opp_score
        return reward


def main():
    trainer = Hearts_env()
    tot_wins = 0
    sam_wins = 0
    current_odds = .5
    trainer.hearts_game = Hearts()
    for i in range(epochs):

        current_odds *= trainer.hearts_game.players[1].play_policy.decay_factor
        trainer.hearts_game.players[1].play_policy.odds_explore = current_odds
        # play until someone loses
        while trainer.hearts_game.losingPlayer is None or trainer.hearts_game.losingPlayer.score < max_score:

            while trainer.hearts_game.trick_num < total_tricks:
                if trainer.hearts_game.trick_num == 0:
                    trainer.hearts_game.playersPassCards()
                    trainer.hearts_game.getFirstTrickStarter()

                trainer.hearts_game.playTrick(trainer.hearts_game.trickWinner)

                # train anybody that needs to be trained
                for j, a_palyer in enumerate(trainer.hearts_game.players):
                    q_reward = trainer.get_reward(j)

                    a_palyer.train(q_reward)

                trainer.hearts_game.currentTrick = Trick(trainer.hearts_game.trick_num)
            # tally scores
            trainer.hearts_game.handleScoring()

            # new round if no one has lost
            if trainer.hearts_game.losingPlayer.score < max_score:
                trainer.hearts_game.newRound()

        winners = trainer.hearts_game.getWinner()
        winnerString = ""
        for w in winners:
            winnerString += w.name + " "
            if w.name == "Jack":
                tot_wins += 1
            if w.name == "Sam":
                sam_wins += 1

        if i % 25 == 0:
            print()
            for a, player in enumerate(trainer.hearts_game.players):
                print(player.name + ": " + str(player.score))
            print("Jack wins: ", tot_wins)
            print("Sam wins: ", sam_wins)
            print("num games: ", i)
            print(winnerString + "wins!")

        if i % 50 == 0:
            for player in trainer.hearts_game.players:
                try:
                    player.play_policy.save_model()
                except:
                    pass

        trainer.hearts_game.reset()


if __name__ == '__main__':
    main()

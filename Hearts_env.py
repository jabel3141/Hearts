from Hearts import Hearts

max_score = 100
total_tricks = 13
epochs = 100000


class Hearts_env:

    def __init__(self):
        self.hearts_game = Hearts()

    def get_reward(self, player_pos):
        # Todo build a better reward function

        player_won = self.hearts_game.currentTrick.winner

        # player won the trick and adds the score they got
        if player_pos == player_won:
            # player shot the moon
            if self.hearts_game.players[player_won].currentScore == 26:
                reward = 26

            else:
                reward = (13 - self.hearts_game.currentTrick.points)

        # player lost the trick, but the winner shot the moon
        elif self.hearts_game.players[player_won].currentScore == 26:
            reward = 0

        # player lost the trick they scored zero
        else:
            reward = 13

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

            # tally scores
            trainer.hearts_game.handleScoring()

            # new round if no one has lost
            if trainer.hearts_game.losingPlayer.score < max_score:
                trainer.hearts_game.newRound()

        print()
        for a, player in enumerate(trainer.hearts_game.players):
            print(player.name + ": " + str(player.score))
        # spacing
        winners = trainer.hearts_game.getWinner()
        winnerString = ""
        for w in winners:
            winnerString += w.name + " "
            if w.name == "Jack":
                tot_wins += 1
            if w.name == "Sam":
                sam_wins += 1
        print("Jack wins: ", tot_wins)
        print("Sam wins: ", sam_wins)
        print("num games: ", i)
        print(winnerString + "wins!")

        for i, player in enumerate(trainer.hearts_game.players):
            try:
                player.play_policy.model.save_weights("q_model.h5")
            except:
                pass

        trainer.hearts_game.reset()

if __name__ == '__main__':
    main()

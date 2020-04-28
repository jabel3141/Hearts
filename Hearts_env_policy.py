from Hearts import Hearts
from Trick import Trick
import sys

max_score = 100
total_tricks = 13
epochs = 100000


class Hearts_env:

    def __init__(self):
        self.hearts_game = Hearts()

    def get_reward(self, player_pos):
        # Todo build a better reward function
        # 4 if no points taken
        # -num points if points taken
        #+/- 52 for shooting the moon

        player_won = self.hearts_game.currentTrick.winner

        # player won the trick and adds the score they got
        if player_pos == player_won:
            # player shot the moon
            if self.hearts_game.players[player_won].currentScore == 26:
                reward = 52
            elif self.hearts_game.currentTrick.points > 0:
                reward = (-self.hearts_game.currentTrick.points)
            else:
                reward = 4

        # player lost the trick, but the winner shot the moon
        elif self.hearts_game.players[player_won].currentScore == 26:
            reward = -52

        # player lost the trick they scored zero
        else:
            reward = 4

        return reward


def main():
    trainer = Hearts_env()
    tot_wins = 0
    sam_wins = 0
    jb_wins = 0
    current_odds = .5
    trainer.hearts_game = Hearts()
    for i in range(epochs):


        # play until someone loses
        while trainer.hearts_game.losingPlayer is None or trainer.hearts_game.losingPlayer.score < max_score:

            while trainer.hearts_game.trick_num < total_tricks:
                # print("Round: ", trainer.hearts_game.trick_num)
                if trainer.hearts_game.trick_num == 0:
                    trainer.hearts_game.playersPassCards()
                    trainer.hearts_game.getFirstTrickStarter()

                # print(trainer.hearts_game.players[1].hand)

                trainer.hearts_game.playTrick(trainer.hearts_game.trickWinner)

                # add reward to the model for this timestep
                for j, a_palyer in enumerate(trainer.hearts_game.players):
                    q_reward = trainer.get_reward(j)

                    a_palyer.store_reward(q_reward)

                trainer.hearts_game.currentTrick = Trick(trainer.hearts_game.trick_num)

            # tally scores
            trainer.hearts_game.handleScoring()

            #Learn based off the past round
            trainer.hearts_game.players[1].play_policy.learn()

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
            if w.name == "JB":
                jb_wins += 1
        print("Jack wins: ", tot_wins)
        print("Sam wins: ", sam_wins)
        print("JB wins: ", jb_wins)
        print("num games: ", i)
        print(winnerString + "wins!")

        for i, player in enumerate(trainer.hearts_game.players):
            try:
                player.play_policy.save_model()
            except:
                pass

        trainer.hearts_game.reset()

if __name__ == '__main__':
    main()

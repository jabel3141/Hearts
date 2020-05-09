from Hearts import Hearts
from Trick import Trick
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

max_score = 100
total_tricks = 13
epochs = 10000
train = False

physical_save_epochs = 500
display_stats_epochs = 1000


class Hearts_env_policy:

    def __init__(self):
        self.hearts_game = Hearts()
        os.makedirs('models/policy', exist_ok=True)

    #If they got points, 0 otherwise 1
    def get_reward_simple(self, player_pos):
        trickPoints = self.hearts_game.currentTrick.points
        if (self.hearts_game.trickWinner == player_pos) and (trickPoints > 0):
            reward = 0
        else:
            reward = 1

        return reward

    def get_reward_simple_v2(self, player_pos):
        trickPoints = self.hearts_game.currentTrick.points
        if (self.hearts_game.trickWinner == player_pos) and (trickPoints > 0):
            reward = 0
        else:
            reward = trickPoints / 4

        return reward

    def get_reward(self, player_pos):
        score = self.hearts_game.players[player_pos].currentScore
        if score == 26:
            return 78
        opp_score = 0
        for i, p in enumerate(self.hearts_game.players):
            if p.currentScore == 26:
                return -56
            if i != player_pos:
                opp_score += p.currentScore

        reward = (score * -4) + opp_score
        return reward


def main():
    trainer = Hearts_env_policy()
    player0_win = []
    player1_win = []
    player2_win = []
    player3_win = []
    player0_scores = []
    player1_scores = []
    player2_scores = []
    player3_scores = []

    for i in range(epochs):
        # play until someone loses
        while trainer.hearts_game.losingPlayer is None or trainer.hearts_game.losingPlayer.score < max_score:
            while trainer.hearts_game.trick_num < total_tricks:
                # print("Round: ", trainer.hearts_game.trick_num)
                if trainer.hearts_game.trick_num == 0:
                    trainer.hearts_game.playersPassCards()
                    trainer.hearts_game.getFirstTrickStarter()

                trainer.hearts_game.playTrick(trainer.hearts_game.trickWinner)

                # add reward to the model for this timestep
                for j, a_player in enumerate(trainer.hearts_game.players):
                    q_reward = trainer.get_reward(j)
                    # q_reward = trainer.get_reward_simple(j)
                    # q_reward = trainer.get_reward_simple_v2(j)
                    a_player.store_reward(q_reward)

                trainer.hearts_game.currentTrick = Trick(trainer.hearts_game.trick_num)

            # tally scores
            trainer.hearts_game.handleScoring()

            #Learn based off the past round
            if train:
                trainer.hearts_game.players[1].play_policy.learn()

            # new round if no one has lost
            if trainer.hearts_game.losingPlayer.score < max_score:
                trainer.hearts_game.newRound()

        player0_scores.append(trainer.hearts_game.players[0].score)
        player1_scores.append(trainer.hearts_game.players[1].score)
        player2_scores.append(trainer.hearts_game.players[2].score)
        player3_scores.append(trainer.hearts_game.players[3].score)

        winners = trainer.hearts_game.getWinner()
        winnerString = ""
        won0 = False
        won1 = False
        won2 = False
        won3 = False
        for w in winners:
            winnerString += w.name + " "
            if w.name == "Jason":
                won0 = True
            elif w.name == "Jack":
                won1 = True
            elif w.name == "Sam":
                won2 = True
            elif w.name == "JB":
                won3 = True
        if won0:
            player0_win.append(1)
        else:
            player0_win.append(0)
        if won1:
            player1_win.append(1)
        else:
            player1_win.append(0)
        if won2:
            player2_win.append(1)
        else:
            player2_win.append(0)
        if won3:
            player3_win.append(1)
        else:
            player3_win.append(0)

        if i % display_stats_epochs == (display_stats_epochs - 1):  # Console output
            print()
            for a, player in enumerate(trainer.hearts_game.players):
                print(player.name + ": " + str(player.score))
            print(winnerString + "wins!")
            print("--------------------------------------")
            # print("Jack last 200 games wins: ", np.sum(player1_win[-200:]))
            # print("Jack last 200 games avg score: ", np.sum(player1_scores[-200:]) / len(player1_scores[-200:]))
            print("Player 0 wins:", np.sum(player0_win))
            print("Player 1 wins:", np.sum(player1_win))
            print("Player 2 wins:", np.sum(player2_win))
            print("Player 3 wins:", np.sum(player3_win))
            print("Player 0 avg. score:", np.mean(player0_scores))
            print("Player 1 avg. score:", np.mean(player1_scores))
            print("Player 2 avg. score:", np.mean(player2_scores))
            print("Player 3 avg. score:", np.mean(player3_scores))
            print("num games: ", i + 1)

        if train and i % physical_save_epochs == (physical_save_epochs - 1):  # Physical save
            jack = [pl for pl in trainer.hearts_game.players if pl.name == 'Jack'][0]

            plot_records(player1_scores, "Final score", "models/policy/Scores.png")
            plot_records(jack.play_policy.loss_policy, "Loss Actor", "models/policy/loss.png")

            for player in trainer.hearts_game.players:
                try:
                    player.play_policy.save_model()
                except:
                    pass

        trainer.hearts_game.reset()

    jack = [pl for pl in trainer.hearts_game.players if pl.name == 'Jack'][0]

    if train:
        plot_records(player1_scores, "Final score", "models/policy/Scores.png")
        plot_records(jack.play_policy.loss_policy, "Loss Actor", "models/policy/loss.png")

def plot_records(records, metric, filename):
    smoothed_records = pd.Series.rolling(pd.Series(records), 10).mean()

    plt.plot(records)
    plt.plot(smoothed_records)
    plt.xlabel("Number games")
    plt.ylabel(metric)
    plt.savefig(filename)
    # plt.show()
    plt.clf()

if __name__ == '__main__':
    main()

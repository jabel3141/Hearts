from Hearts import Hearts
from Trick import Trick
from PolicyNN import PolicyNN
from SimpleAI import SimpleAI
from RandomAI import RandomAI
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

max_score = 100
total_tricks = 13
epochs = 10000
batch_size = 5
train = True
play_self = False

physical_save_epochs = 500
display_stats_epochs = 200

track = [True, False, False, False]
randomize_players = []


class Hearts_env_policy:
    def __init__(self):
        self.hearts_game = Hearts()
        os.makedirs('models/policy', exist_ok=True)

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
    player0_win = np.array([])
    player1_win = np.array([])
    player2_win = np.array([])
    player3_win = np.array([])
    player0_scores = np.array([])
    player1_scores = np.array([])
    player2_scores = np.array([])
    player3_scores = np.array([])
    num_hands = 0

    if play_self:
        policy1 = PolicyNN("Sam")
        models = policy1.play_policy.policy, policy1.play_policy.predict
        policy2 = PolicyNN("Jack", models=models)
        policy3 = PolicyNN("Jason", models=models)
        policy4 = PolicyNN("JB", models=models)
        trainer.hearts_game.players = [policy1, policy2, policy3, policy4]
        trainer.hearts_game.reset()

    for i in range(epochs):
        # play until someone loses
        while trainer.hearts_game.losingPlayer is None or trainer.hearts_game.losingPlayer.score < max_score:
            while trainer.hearts_game.trick_num < total_tricks:
                if trainer.hearts_game.trick_num == 0:
                    trainer.hearts_game.playersPassCards()
                    trainer.hearts_game.getFirstTrickStarter()

                trainer.hearts_game.playTrick(trainer.hearts_game.trickWinner)

                # add reward to the model for this timestep
                for j, a_player in enumerate(trainer.hearts_game.players):
                    # reward = trainer.get_reward(j)
                    # reward = trainer.get_reward_simple(j)
                    reward = trainer.get_reward_simple_v2(j)
                    a_player.store_reward(reward)

                trainer.hearts_game.currentTrick = Trick(trainer.hearts_game.trick_num)

            # tally scores
            trainer.hearts_game.handleScoring()

            # Learn based off the past round
            if train:
                num_hands += 1
                if num_hands == batch_size:
                    for j, player in enumerate(trainer.hearts_game.players):
                        if type(player) is PolicyNN:
                                player.play_policy.learn(batch_size)
                    num_hands = 0

            # new round if no one has lost
            if trainer.hearts_game.losingPlayer.score < max_score:
                trainer.hearts_game.newRound()

        if track[0]:
            player0_scores = np.append(player0_scores, trainer.hearts_game.players[0].score)
        if track[1]:
            player1_scores = np.append(player1_scores, trainer.hearts_game.players[1].score)
        if track[2]:
            player2_scores = np.append(player2_scores, trainer.hearts_game.players[2].score)
        if track[3]:
            player3_scores = np.append(player3_scores, trainer.hearts_game.players[3].score)

        winners = trainer.hearts_game.getWinner()
        winnerString = ""
        won = [False, False, False, False]
        for w in winners:
            winnerString += w.name + " "
            if w.name == trainer.hearts_game.players[0].name:
                won[0] = True
            elif w.name == trainer.hearts_game.players[1].name:
                won[1] = True
            elif w.name == trainer.hearts_game.players[2].name:
                won[2] = True
            elif w.name == trainer.hearts_game.players[3].name:
                won[3] = True

        if track[0]:
            if won[0]:
                player0_win = np.append(player0_win, 1)
            else:
                player0_win = np.append(player0_win, 0)
        if track[1]:
            if won[1]:
                player1_win = np.append(player1_win, 1)
            else:
                player1_win = np.append(player1_win, 0)
        if track[2]:
            if won[2]:
                player2_win = np.append(player2_win, 1)
            else:
                player2_win = np.append(player2_win, 0)
        if track[3]:
            if won[3]:
                player3_win = np.append(player3_win, 1)
            else:
                player3_win = np.append(player3_win, 0)

        if i % display_stats_epochs == (display_stats_epochs - 1):  # Console output
            print()
            for a, player in enumerate(trainer.hearts_game.players):
                print(player.name + ": " + str(player.score))
            print(winnerString + "wins!")
            print("--------------------------------------")
            if track[0]:
                print("Player 0 wins:", np.sum(player0_win))
                print("Player 0 avg. score:", np.mean(player0_scores))
            if track[1]:
                print("Player 1 wins:", np.sum(player1_win))
                print("Player 1 avg. score:", np.mean(player1_scores))
            if track[2]:
                print("Player 2 wins:", np.sum(player2_win))
                print("Player 2 avg. score:", np.mean(player2_scores))
            if track[3]:
                print("Player 3 wins:", np.sum(player3_win))
                print("Player 3 avg. score:", np.mean(player3_scores))
            print("num games: ", i + 1)

        if train and i % physical_save_epochs == (physical_save_epochs - 1):  # Physical save
            print("Saving model")
            for player in trainer.hearts_game.players:
                plot_records(player0_scores, "Final score", "models/policy/Scores.png")
                if type(player) is PolicyNN:
                    plot_records(player.play_policy.loss_policy, "Loss Actor", "models/policy/loss_" + player.name + ".png")

                    try:
                        player.play_policy.save_model()
                    except:
                        pass

        # Change players and reset
        if i % 10 == 9:
            for j in randomize_players:
                rand = np.random.randint(10)
                if rand == 9:
                    trainer.hearts_game.players[j] = RandomAI("rand" + str(j))
                else:
                    trainer.hearts_game.players[j] = SimpleAI("simple" + str(j))
        trainer.hearts_game.reset()

    if train:
        for i, player in enumerate(trainer.hearts_game.players):
            plot_records(player0_scores, "Final score", "models/policy/Scores.png")
            if type(player) is PolicyNN:
                plot_records(player.play_policy.loss_policy, "Loss Actor", "models/policy/loss_" + player.name + ".png")


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

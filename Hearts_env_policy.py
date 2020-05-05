from Hearts import Hearts
from Trick import Trick
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

max_score = 100
total_tricks = 13
epochs = 20000


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
            reward = trickPoints

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
    tot_wins = 0
    last200Wins = []
    last200scores = []
    record_final_score = []
    jason_wins = 0
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

                    # q_reward = trainer.get_reward(j)
                    q_reward = trainer.get_reward_simple(j)
                    # q_reward = trainer.get_reward_simple_v2(j)

                    a_palyer.store_reward(q_reward)

                trainer.hearts_game.currentTrick = Trick(trainer.hearts_game.trick_num)

            # tally scores
            trainer.hearts_game.handleScoring()

            #Learn based off the past round
            trainer.hearts_game.players[1].play_policy.learn()

            # new round if no one has lost
            if trainer.hearts_game.losingPlayer.score < max_score:
                trainer.hearts_game.newRound()

        record_final_score.append(trainer.hearts_game.players[1].score)

        # trainer.hearts_game.players[1].play_policy.learn()

        winners = trainer.hearts_game.getWinner()
        winnerString = ""
        if len(last200Wins) == 200:
            last200Wins.pop(0)
        if len(last200scores) == 200:
            last200scores.pop(0)

        modelWon = False
        for w in winners:
            winnerString += w.name + " "
            if w.name == "Jack":
                tot_wins += 1
                modelWon = True
            elif w.name == "Jason":
                jason_wins += 1
            elif w.name == "Sam":
                sam_wins += 1
            elif w.name == "JB":
                jb_wins += 1
        if modelWon:
            last200Wins.append(1)
        else:
            last200Wins.append(0)
        last200scores.append(trainer.hearts_game.players[1].score)

        if i % 200 == 0:
            print()
            for a, player in enumerate(trainer.hearts_game.players):
                print(player.name + ": " + str(player.score))
            print(winnerString + "wins!")
            # print(trainer.hearts_game.players[1].play_policy.G)
            print("--------------------------------------")
            print("Jack last 200 games wins: ", np.sum(last200Wins))
            print("Jack last 200 games avg score: ", np.sum(last200scores) / len(last200scores))
            print("Jack wins: ", tot_wins)
            print("Jason wins: ", jason_wins)
            print("Sam wins: ", sam_wins)
            print("JB wins: ", jb_wins)
            print("num games: ", i)

            jack = [pl for pl in trainer.hearts_game.players if pl.name == 'Jack'][0]

            plot_records(record_final_score, "Final score", "models/policy/Scores.png")
            plot_records(jack.play_policy.loss_policy, "Loss Actor", "models/policy/loss.png")


        if i % 200 == 0:
            for player in trainer.hearts_game.players:
                try:
                    player.play_policy.save_model()
                except:
                    pass


        trainer.hearts_game.reset()

    jack = [pl for pl in trainer.hearts_game.players if pl.name == 'Jack'][0]

    plot_records(record_final_score, "Final score", "models/policy/Scores.png")
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

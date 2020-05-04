from Hearts import Hearts
from Trick import Trick
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

max_score = 100
total_tricks = 13
epochs = 1000


WORST_TRICK = 16 ## 16 is the worst case, QS + 3 H
class Hearts_env_policy:

    def __init__(self):
        self.hearts_game = Hearts()
        os.makedirs('models/actor_critic', exist_ok=True)

    def get_reward(self, player_pos, previous_scores):
        ## TODO Must be the reward of doing an action given a state,
        ## this should not be an absolute value.
        score = self.hearts_game.players[player_pos].currentScore
        previous_score = previous_scores[player_pos]

        points_gained = score - previous_score
        
        return WORST_TRICK - points_gained 
 


        ## Advantage based
        # avg_opp_score = 0
        # for i, p in enumerate(self.hearts_game.players):
        #     if i != player_pos:
        #         avg_opp_score += p.currentScore
        
        # avg_opp_score /= 3.0

        # disadvantage_over_opp = score - avg_opp_score
        # return - disadvantage_over_opp
        
        ## PREVIOUS
        # if score == 26:
        #     return 78
        # opp_score = 0
        # for i, p in enumerate(self.hearts_game.players):
        #     if p.currentScore == 26:
        #         return -52
        #     if i != player_pos:
        #         opp_score += p.currentScore

        # reward = score * -4 + opp_score
        # return reward


def main():
    trainer = Hearts_env_policy()
    tot_wins = 0
    tot_loss = 0
    last200Wins = []
    last200Loss = []
    jason_wins = 0
    sam_wins = 0
    jb_wins = 0
    jason_loss = 0
    sam_loss = 0
    jb_loss = 0    
    current_odds = .5
    trainer.hearts_game = Hearts()

    record_final_score = []

    for i in range(epochs):


        # play until someone loses
        while trainer.hearts_game.losingPlayer is None or trainer.hearts_game.losingPlayer.score < max_score:

            while trainer.hearts_game.trick_num < total_tricks:
                # print("Round: ", trainer.hearts_game.trick_num)
                if trainer.hearts_game.trick_num == 0:
                    trainer.hearts_game.playersPassCards()
                    trainer.hearts_game.getFirstTrickStarter()

                # print(trainer.hearts_game.players[1].hand)

                previous_scores = [pl.currentScore for pl in trainer.hearts_game.players]

                trainer.hearts_game.playTrick(trainer.hearts_game.trickWinner)

                # add reward to the model for this timestep
                for j, a_palyer in enumerate(trainer.hearts_game.players):

                    q_reward = trainer.get_reward(j, previous_scores)

                    a_palyer.store_reward(q_reward)

                trainer.hearts_game.currentTrick = Trick(trainer.hearts_game.trick_num)

            # tally scores
            trainer.hearts_game.handleScoring()


            #Learn based off the past round
            trainer.hearts_game.players[1].play_policy.learn()

            # new round if no one has lost
            if trainer.hearts_game.losingPlayer.score < max_score:
                trainer.hearts_game.newRound()


        # Record Jack's final score
        record_final_score.append(trainer.hearts_game.players[1].score)

        winners = trainer.hearts_game.getWinner()
        winnerString = ""
        for w in winners:
            winnerString += w.name + " "
            if len(last200Wins) == 200:
                last200Wins.pop(0)

            if w.name == "Jack":
                tot_wins += 1
                last200Wins.append(1)
            else:
                last200Wins.append(0)
            if w.name == "Jason":
                jason_wins += 1
            if w.name == "Sam":
                sam_wins += 1
            if w.name == "JB":
                jb_wins += 1

        if i % 25 == 0:
            print()
            for a, player in enumerate(trainer.hearts_game.players):
                print(player.name + ": " + str(player.score))
            print(winnerString + "wins!")
            print("--------------------------------------")
            print("Jack last 200 games wins: ", np.sum(last200Wins))
            print("Jack wins: ", tot_wins)
            print("Jason wins: ", jason_wins)
            print("Sam wins: ", sam_wins)
            print("JB wins: ", jb_wins)
            print("num games: ", i)

        
        losers = trainer.hearts_game.getLosers()
        losersString = ""


        if len(last200Loss) == 200:
            last200Loss.pop(0)
        if 'Jack' in [l.name for l in losers]:
            last200Loss.append(1)
        else:
            last200Loss.append(0)



        for w in losers:
            losersString += w.name + " "
            if w.name == "Jack":
                tot_loss += 1

            if w.name == "Jason":
                jason_loss += 1
            if w.name == "Sam":
                sam_loss += 1
            if w.name == "JB":
                jb_loss += 1

        if i % 25 == 0:
            print("\n")
            for a, player in enumerate(trainer.hearts_game.players):
                print(player.name + ": " + str(player.score))
            print(losersString + "lose.")
            print("--------------------------------------")
            print("Jack last 200 games losses: %d  (%.2f%%)" %(np.sum(last200Loss), 100 * np.sum(last200Loss) / len(last200Loss)))
            print("       Average final score: %.2f" % (np.sum(record_final_score[-200:]) / len(record_final_score[-200:])))
            print("Jack losses: ", tot_loss)
            print("Jason losses: ", jason_loss)
            print("Sam losses: ", sam_loss)
            print("JB losses: ", jb_loss)
            print("num games: ", i)

        


        if i % 50 == 0:
            for player in trainer.hearts_game.players:
                try:
                    player.play_policy.save_model()
                except Exception as E:
                    pass

        trainer.hearts_game.reset()

    plot_records(record_final_score, "Final score")

    jack = [pl for pl in trainer.hearts_game.players if pl.name =="Jack"][0]

    plot_records(jack.play_policy.loss_actor, "Loss Actor")
    plot_records(np.log(jack.play_policy.loss_critic), "Log-loss Critic")

def plot_records(records, metric):
    smoothed_records = pd.Series.rolling(pd.Series(records), 10).mean()
    
    plt.plot(records)
    plt.plot(smoothed_records)
    plt.xlabel("Number games")
    plt.ylabel(metric)
    plt.show()

if __name__ == '__main__':
    main()

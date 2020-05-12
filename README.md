# Hearts

A Python implementation of Hearts. This project is a work in progress.

# Objective
Win all the hearts and the queen of spades, or none of these cards. Get as few points as possbile.

# Rules
* Each of the four players is dealt 13 cards.

* Before the round starts, all four players pass three cards. The direction cycles between left, right, across, and no pass.

* The player with the two of clubs leads the first trick.

* A player must play a card with the suit as the card that lead the trick, if possible. Otherwise, any card may be played.

* The player with the high ranked card of the suit that lead wins the trick (aces are high).

* A player may not play hearts or the queen of spades on the first hand (except if that is all of their cards).

* After all 13 tricks have been played, points are tallied for each player.

* A player receives one point per heart and 13 points for the queen of spades.

* If a player has all of the points, he or she has "shot the moon" and receives 0 points instead. All other players get 26 points.

* The game ends when the first player gets to 100 points. The winner is the player with the fewest points.

# Implementation
Players can be changed at the top of the `Hearts.py` file by changing between the different Player subclasses. HumanAI
waits for input so a person can play. RandomAI passes and plays random legal cards. SimpleAI will attempt to play cards
that will not win the trick. SimpleNN is Q-learning based, PolicyNN uses the policy gradient method, and ActorCriticNN
is based on the Actor-critic method.

# Model Training
To train a model, run the corresponding training file. `Hearts_env_policy.py` is used to train the PolicyNN's model.
Most of our time was spent there, so there are many hyperparameters to play with. `Hearts_env.py` is used to train the
SimpleNN's model, but has a lot of outdated code. `actor_critic.py` was created to train the ActorCriticNN's model, but there may be some bugs as we
did not get good results before dropping that architecture.

# Final model
The model architecture in `PolicyGradientModel.py` is the one we used to train our final model. We trained against 3
SimpleAI for about 1 million games, and now win 35% of games. Given more training time or other additions, we think this
number could be improved. The trained model is saved as `final_model.h5`

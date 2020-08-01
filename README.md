# pandemic_ai_bot

This repository trains a reinforcement learning algorithm to play the board game pandemic. It is written in Python. A human can play a text based version of the game by running the game.py file. To train the bot, run the game_env.py file. 

Note that the game does not have event cards or roles.

A quick overview of the files:

* bot_game.py – the version of the game for the bot (e.g. no user input, vector state representation of the game). The bot is not trained in this file. 
* card_decks.py – classes for all the card decks, including the infection card deck and the player card deck. Essentially, wrappers around a list of card with added functionality for drawing the bottom or shuffling.


# pandemic_ai_bot

This repository trains a reinforcement learning algorithm to play the board game pandemic. It is written in Python. A human can play a text based version of the game by running the game.py file. To train the bot, run the game_env.py file. 

Note that the game does not have event cards or roles.

The main files are in src. A quick overview of the files:

* bot_game.py – the version of the game for the bot (e.g. no user input, vector state representation of the game). The bot is not trained in this file. 
* card_decks.py – classes for all the card decks, including the infection card deck and the player card deck. Essentially, wrappers around a list of card with added functionality for drawing the bottom or shuffling.
* cards.py – classes for all the types of cards, including epidemic cards, infection card, and player cards. Most cards contain a name, an object (e.g. a city or an epidemic), and some specialized functions (e.g. infect or cause_epidemic).
* city.py – class for a city. Cities have a name, a disease, neighbors, disease cubes, and a research station. Cities can be infected, disinfected, etc.
* city_adj_list.txt – list of all cities with their color and their neighbors
* code_development.ipynb – notebook for scratch work while writing code
* constants.py – list of constants in the code. Including the maximum number of disease cubes and a city, the size limit of a player’s hand, total number of disease cubes of each color, etc.
* disease.py – class for a disease. A disease has a number of cubes left (on side of the board), a color, and can be cured. A disease can infect, disinfect, and be cured. Also tracks how many diseases have been cured.
* epidemic.py – class for causing an epidemic. Takes care of incrememnting the infection rate and dealing with the infection card decks.
* game.py – takes care of running the game. Creates all the cities, cards, card decks, players, etc. Administers turns and delegates actions to appropriate objects. Makes a text based version of the game for humans.
* game_env.py – interface between the pandemic game and the reinforcement learning bot. Trains the bot to play the game.
* infection_rate.py – tracks the infection level and rate
* outbreak_counter.py – tracks the number of outbreaks
* player.py – class for creating a player. A player has a name, a city, and a hand of cards. A player may move to an adjacent city, use their cards to move, treat diseases, add/get rid of cards, etc.
* player_hand.py – class for a player hand. A player hand has a list of cards and a discarded deck to discard into. Player hands can add/discard cards, check to see what cards they contain, etc.

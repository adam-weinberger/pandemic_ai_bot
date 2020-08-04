import constants
from collections import OrderedDict
from player import Player
from disease import Disease
from city import City
from cards import EpidemicCard, PlayerCityCard, InfectionCard
from card_decks import (
    InfectionCardDeck,
    InfectionCardDiscardDeck,
    PlayerCardDeck,
    PlayerCardDiscardDeck
)
from infection_rate import InfectionRate
import logging
import random
import pdb


class Game(object):
    def __init__(self, num_players, num_epidemics):

        # initialize game object. Game has players, epidemics, diseases. it takes care of managing each turn

        # initialize random seed to ensure reproducibility for testing. set number of players an numbered epidemics
        
        self.num_players = num_players
        self.num_epidemics = num_epidemics
        self.disease_dict = {color: Disease(color) for color in constants.DISEASE_COLORS}

        
        # create board,player cards, decks, players
        random.seed(235)
        self.create_cities()
        self.create_decks()
        self.create_players()
        
        # create logger
        logging.basicConfig(level=logging.INFO, filename='../logs/game.log', filemode='w')

    def play_game(self):

        #in charge of the game. manages the game turn by turn, and checks if the game has been won or lost.

        logging.info("play_game")

        self.game_is_finished = False

        while not self.game_is_finished:
            try:
                self.player_actions()
                self.player_draw_cards()
                self.infect_cities()
                self.next_player()
            except Exception as e:
                print(e)

                # check to see if game is won or lost
                if len(e.args) > 1:
                    self.game_is_finished = e.args[constants.GAME_RESULT_ARG_IND]

        self.play_again()

    def player_actions(self):

        # continue playing actions until player has none left

        logging.info("play_actions")

        for i in range(constants.NUM_ACTIONS):
            print("Action {} of {}".format(i + 1, constants.NUM_ACTIONS))
            self._play_action()

    def _play_action(self):

        
        # tell player the current city and their current hand
        print("You are in: {}".format(self.current_player.current_city))
        print("Current hand: {}".format(self.current_player.hand_to_string()))

        action_name = self._choose_action()
        action_function = getattr(self.current_player, action_name)

        option_choice = self._choose_arg(action_name)

        # the player might have to choose a city,another player, or a disease.if they have to choose an city,they might have to choose a city from their own hand or any city from the board.
        try:
            
            action_function(option_choice)

        except Exception as e:
            print(e)
            self._play_action()

            
    def _choose_action(self):

        # ask player which action to do
        action_prompt = "What action would you like to do?"
        # list actions for player
        action_list = self.current_player.list_actions()
        action_name = self._option_list_prompt(action_prompt, action_list)
        
        return action_name

    def _choose_arg(self, action_name):
        
        # prompt user for arguments to action, try to perform action with arguments given
        option_prompt = "Provide arguments: "
        option_list = self._action_arguments(action_name)
        option_choice = self._option_list_prompt(option_prompt, option_list)

        return option_choice


    def _option_list_prompt(self, prompt, option_list):

        # given a prompt and a list of options prompt the user for a decision.keep asking until the user gives a valid answer
        option_invalid = True

        while option_invalid:

            # options are numbered0 through n
            options_str = ["{}) {}".format(i, option_list[i]) for i in range(len(option_list))]
            option_choice_num = int(input("{} {}".format(prompt, options_str)))

            if option_choice_num < 0 or option_choice_num >= len(option_list):
                print("Option choice invalid. Please try again")
                continue

            option_choice = option_list[option_choice_num]
            undo = input("You chose {}. Type -1 to undo. Type enter to continue.".format(option_choice))

            # if option is -1then undo action choice
            if undo == -1:
                print("Undo choice {}".format(option_choice))
                continue
            
            option_invalid = False

        return option_choice

    def _action_arguments(self, action_name):

        # give list(available options depending on the action choice)
        options = None
        if action_name == "drive_ferry":
            options = self.current_player.current_city.neighbors
        elif action_name == "direct_flight":
            options = [card.city for card in self.current_player.player_hand.hand]
        elif action_name == "charter_flight":
            options = [*self.city_dict.values()]
        elif action_name == "shuttle_flight":
            city_list = [*self.city_dict.values()]
            options = list(filter(lambda city: city.has_research_station, city_list))
        elif action_name == "build_research_station":
            options = [self.current_player.current_city]
        elif action_name == "treat_disease":
            options = [*self.disease_dict.values()]
        elif action_name == "discover_cure":
            options = [*self.disease_dict.values()]
        elif action_name == "give_knowledge":
            options = [*self.player_dict.values()]
            options = list(filter(lambda player: player != self.current_player, options))
        elif action_name == "take_knowledge":
            options = [*self.player_dict.values()]
            options = list(filter(lambda player: player != self.current_player, options))
        elif action_name == "discard_card":
            options = self.current_player.cards()

        return options

    def player_draw_cards(self):

        logging.info("player_draw_cards")

        # for each card to draw
        for _ in range(constants.NUM_PLAYER_CARDS_DRAW):
            card = self.player_card_deck.draw()
            print("Card drawn: {}".format(card))

            if isinstance(card, EpidemicCard):
                card.cause_epidemic()
                continue

            # try to add card
            try:
                self.current_player.add_card(card)

            # hand may be full
            except Exception as e:

                if str(e) == constants.PLAYER_HAND_FULL_ERROR:

                    action_name = "discard_card"
                    option_list = self._action_arguments(action_name)
                    option_list.append(card) #card will have failed to be added, so needs to be an option to discard
                    prompt = "Hand full, discard card:"
                    card = self._option_list_prompt(prompt, option_list)

                    self.current_player.discard_card(card)


    def infect_cities(self):

        logging.info("infect_cities")

        for _ in range(InfectionRate.get_infection_rate()):
            card = self.infection_card_deck.draw()
            card.infect()
            self.infection_card_discard_deck.add(card)

    def next_player(self):

        logging.info("next_player")
        self.current_player_ind += 1
        self.current_player_ind = self.current_player_ind % self.num_players
        next_player_name = list(self.player_dict.keys())[self.current_player_ind]
        self.current_player = self.player_dict[next_player_name]
        print("Player: {}'s turn".format(self.current_player.name))

    def play_again(self):
        pass

    def create_cities(self):

        print('create_cities')

        # create cities
        f = open("city_adj_list.txt")

        # list of cities
        self.city_dict = {}
        for line in f:
            line = line.split()
            color = line[0]
            city_name = line[1]
            self.city_dict[city_name] = City(city_name, self.disease_dict[color])

        f.close()

        # city neighbor list
        f = open("city_adj_list.txt")

        # add neighbors
        for line in f:
            line = line.split()
            city = line[1]
            city = self.city_dict[city]
            city.neighbors = []
            neighbors = line[2:]
            for neighbor in neighbors:

                neighbor = self.city_dict[neighbor]
                city.add_neighbor(neighbor)

        # start city has a research station
        City.research_station_counter = 0
        if constants.START_CITY_HAS_RESEARCH_STATION:
            self.city_dict[constants.START_CITY].add_research_station()

            
        f.close()

    def create_decks(self):

        print('create_decks')
        random.seed(235)

        # assign player card decks
        self.player_card_deck = PlayerCardDeck()
        self.player_card_discard_deck = PlayerCardDiscardDeck()

        # create player city cards
        [self.player_card_deck.add(PlayerCityCard(city)) for city in self.city_dict.values()]
        self.player_card_dict = {card.name: card for card in self.player_card_deck.card_list} # needed for bot_game
        self.player_card_deck.shuffle()

        # create starting card deck to give players cards before the game begin
        self.starting_card_deck = PlayerCardDeck()
        self.starting_card_deck_size = (
            constants.NUM_START_CARDS[self.num_players] * self.num_players
        )

        for _ in range(self.starting_card_deck_size):
            self.starting_card_deck.add(self.player_card_deck.draw())

        # assign infection card add discard decks
        self.infection_card_deck = InfectionCardDeck()
        self.infection_card_discard_deck = InfectionCardDiscardDeck()

        # create infection cards
        [self.infection_card_deck.add(InfectionCard(city)) for city in self.city_dict.values()]
        self.infection_card_dict = {card.name: card for card in self.infection_card_deck.card_list} # needed for bot_game
        self.infection_card_deck.shuffle()

        # add epidemics to player card deck, should be evenly spaced but is not
        [self.player_card_deck.add(EpidemicCard(i, self.player_card_discard_deck, self.infection_card_deck, self.infection_card_discard_deck)) for i in range(self.num_epidemics)]
        self.player_card_deck.shuffle()

        # infect cities
        for i in range(len(constants.INITIAL_CITY_INFECTION_AMOUNTS)):
            num_cubes = constants.INITIAL_CITY_INFECTION_AMOUNTS[i]
            infection_card = self.infection_card_deck.draw()
            infection_card.infect(num_cubes)
            self.infection_card_discard_deck.add(infection_card)

        # TODO create event cards

    def create_players(self):

        print('create_players')

        # create players,each player has a player name and a starting city. each player starts with cards in their hand
        self.player_dict = OrderedDict()

        for i in range(self.num_players):
            player_name = "player {}".format(i)
            start_city = self.city_dict[constants.START_CITY]
            temp_player = Player(player_name, start_city, self.player_card_discard_deck)

            for j in range(constants.NUM_START_CARDS[self.num_players]):
                card = self.starting_card_deck.draw()
                temp_player.add_card(card)

            self.player_dict[player_name] = temp_player

        # set starting player
        self.current_player_ind = 0
        current_player_key = list(self.player_dict.keys())[self.current_player_ind]
        self.current_player = self.player_dict[current_player_key]
        print("Player: {}'s turn".format(self.current_player.name))

        
if __name__ == "__main__":

    g = Game(2, 4)
    g.play_game()

from game import Game
from disease import Disease
import constants
from cards import EpidemicCard
import pandas as pd
from infection_rate import InfectionRate
from outbreak_counter import OutbreakCounter
from collections import Counter, OrderedDict
import random
from gym import spaces
import numpy as np
from city import City
import logging
import pdb
import math
from infection_rate import InfectionRate
from outbreak_counter import OutbreakCounter


class BotGame(Game):

    def __init__(self, num_players, num_epidemics):

        super().__init__(num_players, num_epidemics)
        
        # create look up list from action name to action obd
        self.create_action_dict()

        self.state_dict = None
        self.invalid_response = False
        
        # track the step the game is in
        self.create_game_steps()
        
        # set the initial reward level and state data frame
        self.reward_level = 0
        _, _ = self.game_state_reward_small()

        self.info = {}


    def reset(self):

        status_str = "Beginning game"
        print(status_str)
        logging.info(status_str)

        self.disease_dict = {color: Disease(color) for color in constants.DISEASE_COLORS}
        InfectionRate.infection_level = 0
        OutbreakCounter.outbreak_level = 0
        Disease.diseases_cured = 0

        # create board,player cards, decks, players
        random.seed(235)
        self.create_cities()
        self.create_decks()
        self.create_players()

        # create look up list from action name to action obd
        self.create_action_dict()

        self.state_df = None
        self.invalid_response = False

        # track the step the game is in
        self.create_game_steps()


        # set the initial reward level and state data frame
        self.reward_level = 0
        observation, _ = self.game_state_reward_small()

        self.info = {}

        return observation

    def create_action_dict(self):

        # used for looking up action objects from their name
        self.action_dict = {}

        # add actions
        for action in constants.GAME_ACTION_LIST:
            self.action_dict[action] = getattr(self.current_player, action)  # what about players with special actions

        # add cities
        for city_name, city_obj in self.city_dict.items():
            self.action_dict[city_name] = city_obj

        # add player cards
        for card_name, card_obj in self.player_card_dict.items():
            card_key = 'card_{}'.format(card_name)
            self.action_dict[card_key] = card_obj

        # add players
        for player_name, player in self.player_dict.items():
            self.action_dict[player_name] = player

        # add diseases
        for disease_name, disease in self.disease_dict.items():
            self.action_dict[disease_name] = disease

    def create_game_steps(self):
        
        # game steps track where the game is so the bar and the game know what actions are valid
        # game steps are player actions 1-4, player arg 1-4,draw cards
        self.game_step_list = []
        for i in range(constants.NUM_ACTIONS):
            self.game_step_list.append("player action {}".format(i+1))
            self.game_step_list.append("player arg {}".format(i+1))
        self.game_step_list.append("draw cards")
        self.game_step_ind = 0
        self.game_step = self.game_step_list[self.game_step_ind]
        self.turn_num = 0

        if "action 1" in self.game_step:
            status_str = "Turn: {}".format(self.turn_num)
            print(status_str)
            logging.info(status_str)
            status_str = "You are in: {}".format(self.current_player.current_city)
            print(status_str)
            logging.info(status_str)
            status_str = "Current hand: {}".format(self.current_player.hand_to_string())
            print(status_str)
            logging.info(status_str)

    def create_observation_space(self):

        obs_space = spaces.Box(low=0, high=1, shape=(len(self.state_dict),), dtype=np.float32)

        return obs_space #spaces.Dict(obs_space) #spaces.MultiDiscrete(game_bot_obs_space)

    def game_state_reward_small(self):
        state_dict = {}
        new_reward_level = 0.0

        #card decks, cards, player cards (deck, p0 hand, p1 hand, discard), infection cards (deck, discarded)
        for color in constants.DISEASE_COLORS:
            key = 'player_card_{}_in_deck'.format(color)
            state_dict[key] = 0

            for player in [*self.player_dict.values()]:
                key = 'player_card_{}_in_{}_hand'.format(color, player.name)
                state_dict[key] = 0

        for card in self.player_card_deck.card_list:
            if isinstance(card, EpidemicCard):
                continue

            key = 'player_card_{}_in_deck'.format(card.color)
            if key in state_dict:
                state_dict[key] += np.array([1 / 12]).astype(np.float32) #FIXME 12 hard coded

        for player in [*self.player_dict.values()]:
            for card in player.player_hand.hand:
                key = 'player_card_{}_in_{}_hand'.format(card.color, player.name)
                state_dict[key] += np.array([1 / 12]).astype(np.float32) #FIXME 12 hard coded

        num_player_cards_discarded = len(self.player_card_discard_deck.card_list)
        state_dict['num_player_cards_discarded'] = num_player_cards_discarded
        # new_reward_level -= (num_cards_discarded * 2)

        for card in [*self.infection_card_dict.values()]:
            key = 'infection_card_{}_in_deck'.format(card.city.disease.color)
            if key in state_dict:
                state_dict[key] += np.array([1 / 12]).astype(np.float32) #FIXME 12 hard coded
            else:
                state_dict[key] = 0

        for color, disease in self.disease_dict.items():
            key = 'cubes_left_{}'.format(color)
            state_dict[key] = np.array([disease.num_cubes / constants.NUM_CUBES]).astype(np.float32) 

            key = 'is_cured_{}'.format(color)
            state_dict[key] = int(disease.is_cured)

            # new_reward_level += int(disease.is_cured) * 24

        key = 'total_diseases_cured'
        state_dict[key] = np.array([Disease.diseases_cured / len(constants.DISEASE_COLORS)]).astype(np.float32)

        #infection rate
        key = 'infection_rate'
        cur_infection_rate = InfectionRate.infection_rate[InfectionRate.infection_level]
        max_infection_rate = max(constants.INFECTION_RATE)
        state_dict[key] = np.array([cur_infection_rate / max_infection_rate]).astype(np.float32)

        #outbreak counter
        key = 'outbreak_level'
        state_dict[key] = np.array([ OutbreakCounter.outbreak_level / constants.MAX_OUTBREAKS]).astype(np.float32)
        # new_reward_level -= OutbreakCounter.outbreak_level * 12

        dist_factor = 8
        for player in [*self.player_dict.values()]:
            city_dist = self.shortest_paths(player.current_city)
            for city_name, dist in city_dist.items():
                key = "{}_dist_{}".format(player.name, city_name)
                state_dict[key] = np.array([ dist / dist_factor ]).astype(np.float32) #probably couldn't be higher than 5 but 8 is safe

        #Distance to cubes for reward
        for city in self.city_dict.values():
            num_cubes = city.total_disease_cubes()
            key ="num_cubes_in_{}".format(city.name)
            state_dict[key] = np.array([num_cubes / 6]).astype(np.float32) #FIXME 6 hard coded
            new_reward_level -= [0, .03, .6, 2][num_cubes]

            for player in [*self.player_dict.values()]:
                key = "{}_dist_{}".format(player.name, city.name)
                dist = state_dict[key][0] * dist_factor

                priority = (num_cubes * (3 - dist) / 9) ** 3
                new_reward_level += priority

        #which player's turn, dont need last player because it is implied by all zeros
        player_list_wo_last = [*self.player_dict.values()][:-1]
        for player in player_list_wo_last:
            key = "{}'s_turn".format(player.name)
            if player == self.current_player:
                state_dict[key] = 1
            else:
                state_dict[key] = 0


        #state of game info TODO 1:1 with which actions are valid
        for game_step in self.game_step_list[:-1]:
            if game_step == self.game_step:
                state_dict[game_step] =  1
            else:
                state_dict[game_step] = 0

        # # +[0, 0, 5, 10, 15, 20, 20, ...] for [0, 1, 2, 3, 4, 5, 6, ...] of the same color cards in a single player's hand
        # color_rewards = [0, 0, 5, 10, 15, 20] + [20] * (constants.HAND_SIZE_LIMIT - 5)
        # for player in [*self.player_dict.values()]:
        #     card_colors = [card.color for card in player.cards()]
        #     card_colors = Counter(card_colors)
        #     new_reward_level += sum([color_rewards[count] for count in card_colors.values()])

        if self.invalid_response:
            new_reward_level -= .01 #there are a lot of possible response so this punishment can build up quickly
            self.invalid_response = False

        state_dict = OrderedDict(sorted(state_dict.items(), key=lambda t: t[0]))
        state_df = pd.DataFrame(state_dict, index=[0])
        state_df = state_df.sort_index(axis=1)
        state_np = state_df.to_numpy()
        state_np = np.resize(state_np, (len(state_dict),))

        new_reward_level = new_reward_level / constants.REWARD_LEVEL_SCALE
        reward = new_reward_level - self.reward_level

        self.reward_level = new_reward_level

        self.state_dict = state_dict

        return state_np, reward


    def game_state_reward(self):

        state_dict = {}
        new_reward_level = 0.0
        #card decks, cards, player cards (deck, p0 hand, p1 hand, discard), infection cards (deck, discarded)
        for card in self.player_card_deck.card_list:
            key = 'player_card_{}_in_deck'.format(card.name)
            state_dict[key] = 1

            for player in [*self.player_dict.values()]:
                key = 'player_card_{}_in_{}_hand'.format(card.name, player.name)
                state_dict[key] = 0

        for player in [*self.player_dict.values()]:
            for card in player.player_hand.hand:
                key = 'player_card_{}_in_{}_hand'.format(card.name, player.name)
                state_dict[key] = 1

                for other_player in [*self.player_dict.values()]:
                    if other_player != player:
                        key = 'player_card_{}_in_{}_hand'.format(card.name, other_player.name)
                        state_dict[key] = 0

                key = 'player_card_{}_in_deck'.format(card.name)
                state_dict[key] = 0

        for card in self.player_card_discard_deck.card_list:
            key = 'player_card_{}_in_deck'.format(card.name)
            state_dict[key] = 0

            for player in [*self.player_dict.values()]:
                key = 'player_card_{}_in_{}_hand'.format(card.name, player.name)
                state_dict[key] = 0

        num_cards_discarded = len(self.player_card_discard_deck.card_list)
        # new_reward_level -= (num_cards_discarded * 2)

        for card in [*self.infection_card_dict.values()]:
            key = 'infection_card_{}_in_deck'.format(card.name)
            state_dict[key] = 1

        for card in self.infection_card_discard_deck.card_list:
            key = 'infection_card_{}_in_deck'.format(card.name)
            state_dict[key] = 0

        #city (could also add information about each color of disease cube, what color the city is )
        for city_name, city_obj in self.city_dict.items():
            num_cubes = city_obj.disease_cubes[city_obj.disease.color]
            has_research_station = city_obj.has_research_station

            key = 'num_cubes_{}'.format(city_name)
            state_dict[key] = np.array([num_cubes / 6]).astype(np.float32) #in theory it could be as high as 12 but in practice it would rarely ever get above 4 let alone six

            key = 'research_station_{}'.format(city_name)
            state_dict[key] = int(has_research_station)

            new_reward_level -= num_cubes
            new_reward_level += int(has_research_station)
            

        #diseases (could also add is eradicated)
        for color, disease in self.disease_dict.items():
            key = 'cubes_left_{}'.format(color)
            state_dict[key] = np.array([disease.num_cubes / constants.NUM_CUBES]).astype(np.float32) 

            key = 'is_cured_{}'.format(color)
            state_dict[key] = int(disease.is_cured)

            # new_reward_level += int(disease.is_cured) * 24


        key = 'total_diseases_cured'
        state_dict[key] = np.array([Disease.diseases_cured / len(constants.DISEASE_COLORS)]).astype(np.float32)

        #infection rate
        key = 'infection_rate'
        cur_infection_rate = InfectionRate.infection_rate[InfectionRate.infection_level]
        max_infection_rate = max(constants.INFECTION_RATE)
        state_dict[key] = np.array([cur_infection_rate / max_infection_rate]).astype(np.float32)


        #outbreak counter
        key = 'outbreak_level'
        state_dict[key] = np.array([ OutbreakCounter.outbreak_level / constants.MAX_OUTBREAKS]).astype(np.float32)
        # new_reward_level -= OutbreakCounter.outbreak_level * 12
        

        #player add shortest paths, TODO to add to action space
        dist_factor = 8
        for player in [*self.player_dict.values()]:
            city_dist = self.shortest_paths(player.current_city)
            for city_name, dist in city_dist.items():
                key = "{}_dist_{}".format(player.name, city_name)
                state_dict[key] = np.array([ dist / dist_factor ]).astype(np.float32) #probably couldn't be higher than 5 but 8 is safe

        #Distance to cubes for reward
        for city in self.city_dict.values():
            num_cubes = city.total_disease_cubes()

            for player in [*self.player_dict.values()]:
                key = "{}_dist_{}".format(player.name, city.name)
                dist = state_dict[key][0] * dist_factor
                new_reward_level += num_cubes * (3 - dist) / 9
        # TODO distance to research station
        #player location
        for player_name, player_obj in self.player_dict.items():
            for city_name, city_obj in self.city_dict.items():
                key = '{}_in_city_{}'.format(player_name, city_name)
                state_dict[key] = int(player_obj.current_city == city_obj)

        #which player's turn
        for player in self.player_dict.values():
            key = "{}'s_turn".format(player.name)
            if player == self.current_player:
                state_dict[key] = 1
            else:
                state_dict[key] = 0


        #state of game info TODO 1:1 with which actions are valid
        for game_step in self.game_step_list:
            if game_step == self.game_step:
                state_dict[game_step] =  1
            else:
                state_dict[game_step] = 0

        #convert to pandas and np
        state_dict = OrderedDict(sorted(state_dict.items(), key=lambda t: t[0]))
        state_df = pd.DataFrame(state_dict, index=[0])
        state_df = state_df.sort_index(axis=1)
        state_np = state_df.to_numpy()
        state_np = np.resize(state_np, (len(state_dict),))

        # # +[0, 0, 5, 10, 15, 20, 20, ...] for [0, 1, 2, 3, 4, 5, 6, ...] of the same color cards in a single player's hand
        # color_rewards = [0, 0, 5, 10, 15, 20] + [20] * (constants.HAND_SIZE_LIMIT - 5)
        # for player in [*self.player_dict.values()]:
        #     card_colors = [card.color for card in player.cards()]
        #     card_colors = Counter(card_colors)
        #     new_reward_level += sum([color_rewards[count] for count in card_colors.values()])

        if self.invalid_response:
            new_reward_level -= .01 #there are a lot of possible response so this punishment can build up quickly
            self.invalid_response = False

        new_reward_level = new_reward_level / constants.REWARD_LEVEL_SCALE
        reward = new_reward_level - self.reward_level

        self.reward_level = new_reward_level

        self.state_dict = state_dict

        return state_np, reward

    def check_done(self):
        
        done = False

        if Disease.diseases_cured == len(constants.DISEASE_COLORS):
            done = True

        if OutbreakCounter.outbreak_level == 8:
            done = True

        for disease in [*self.disease_dict.values()]:
            if disease.num_cubes <= 0:
                done = True

        if len(self.player_card_deck.card_list) == 0 and self.game_step == "draw cards":
            done = True

        #FIXME only for training simple model
        num_diseases_not_on_map = 0
        for disease in [*self.disease_dict.values()]:
            if disease.num_cubes == constants.NUM_CUBES:
                num_diseases_not_on_map += 1
        
        if num_diseases_not_on_map == len(constants.DISEASE_COLORS):
            done = True
            status_str = 'All cubes removed. You win.'
            print(status_str)
            logging.info(status_str)

        return done

    def num_cubes_on_map(self):

        num_diseases_not_on_map = 0
        num_cubes_left = 0
        for disease in [*self.disease_dict.values()]:
            num_cubes_left += (constants.NUM_CUBES - disease.num_cubes)
        
        status_str = 'Num cubes on map: {}'.format(num_cubes_left)
        print(status_str)
        logging.info(status_str)
        
    def step(self, bot_response):

        # get object for the corresponding response
        bot_response_obj = self.action_dict[bot_response]
        status_str = 'Bot Response Obj {}'.format(bot_response_obj)
        # print(status_str)
        logging.info(status_str)

        
        # set default return value
        info = self.info

        # if in player action step, check to make sure the action is valid and if it is continue to next step
        if "player action" in self.game_step:
            self.current_action = bot_response #track current action so that we can check if the action args are valid

            valid_action_list = self.valid_actions()

            if bot_response not in valid_action_list:
                self.invalid_response = True
                observation, reward = self.game_state_reward_small()
                done = self.check_done()
                
                return observation, reward, done, info

            status_str = "Action chosen: {}".format(bot_response)
            print(status_str)
            logging.info(status_str)

            self._increment_game_step()

            observation, reward = self.game_state_reward_small()
            done = self.check_done()

            return observation, reward, done, info #return b/c bot_response is for player action not player arg but game_step moved forward
            
        
        # if in player arg step, check to make sure the arg is valid for the action  and if it is execute action with arg and continue to next step
        elif "player arg" in self.game_step:
            option_list = self._action_arguments(self.current_action)
            status_str = "option list: {}".format([str(x) for x in option_list])
            # print(status_str)
            logging.info(status_str)

            if bot_response_obj not in option_list:
                status_str = "Not in option list"
                # print(status_str)
                logging.info(status_str)
                self.invalid_response = False
                observation, reward = self.game_state_reward_small()
                done = self.check_done()

                return observation, reward, done, info

            action_function = getattr(self.current_player, self.current_action)
            # possible that action and argument combination is not valid


            try:
                action_function(bot_response_obj)

                status_str = "Option chosen: {}".format(bot_response)
                print(status_str)
                logging.info(status_str)

            except Exception as e:
                status_str = "Action and argument not valid"
                print(status_str)
                logging.info(status_str)

                print(e)
                logging.info(e)
                # need to go back one game step
                self._increment_game_step(-1)
                self.invalid_response = False
                observation, reward = self.game_state_reward_small()
                done = self.check_done()

                return observation, reward, done, info

            self._increment_game_step()

        # if not elif b/c player arg 4 goes straight to draw cards
        if self.game_step == "draw cards":

            # may run out of cards, losing game
            try:

                self.bot_draw_cards()

            except Exception as e:

                if len(e.args) > 1 and str(e.args[1]) == "lose":
                    print(e)

                    observation, reward = self.game_state_reward_small()
                    done = self.check_done()

                    return observation, reward, done, info

                else:
                    raise e

            # self.infect_cities()
            self.next_player()
            self.num_cubes_on_map() 

            self._increment_game_step()

        observation, reward = self.game_state_reward_small()
        done = self.check_done()
        
        return observation, reward, done, info

    def valid_actions(self):

        valid_action_list = ['drive_ferry']

        # if len(self.current_player.cards()) > 0:
        #     valid_action_list.append('direct_flight')
        #
        # if self.current_player.player_hand.contains_city(self.current_player.current_city):
        #     valid_action_list.append('charter_flight')
        #
        # if self.current_player.current_city.has_research_station and City.research_station_counter > 1:
        #     valid_action_list.append('shuttle_flight')

        # if City.research_station_counter < constants.MAX_RESEARCH_STATIONS and not self.current_player.current_city.has_research_station and self.current_player.player_hand.contains_city(self.current_player.current_city):
        #     valid_action_list.append('build_research_station')
        
        if self.current_player.current_city.total_disease_cubes() > 0:
            valid_action_list.append('treat_disease')
        if self.current_player.current_city.total_disease_cubes() > 1:
            valid_action_list.remove('drive_ferry') #FIXME later

        # if len(self.current_player.cards()) >= 1:
        #     card_colors = [card.color for card in self.current_player.cards() if not isinstance(card, EpidemicCard)]
        #     card_colors = Counter(card_colors)
        #     max_card_color = max([count for count in card_colors.values()])
        #     if self.current_player.current_city.has_research_station and max_card_color >= constants.NUM_CARDS_FOR_CURE: #wont work for any roles that require different number of cards for cure (TODO)
        #         valid_action_list.append('discover_cure')

        # if self.current_player.player_hand.contains_city(self.current_player.current_city):
        #     other_players = [*self.player_dict.values()]
        #     other_players.remove(self.current_player)
        #     other_player_in_city = self.current_player.current_city in [player.current_city for player in other_players]
        #     if other_player_in_city:
        #         valid_action_list.append('give_knowledge')

        
        # hard to check criteria especially with more than 2 players (TODO)
        # valid_action_list.append("take_knowledge")

        # if self.game_step == "draw_cards":
        #     valid_action_list.append('discard_card')

        return valid_action_list

    def _increment_game_step(self, num_steps=1):


        self.game_step_ind += num_steps
        self.game_step_ind = self.game_step_ind % len(self.game_step_list)
        self.game_step = self.game_step_list[self.game_step_ind]

        if "action 1" in self.game_step:
            self.turn_num += 1
            status_str = "Turn num: {}".format(self.turn_num)
            print(status_str)
            logging.info(status_str)

            status_str = "Reward level: {}".format(self.reward_level)
            print(status_str)
            logging.info(status_str)

            status_str = "You are in: {}".format(self.current_player.current_city)
            print(status_str)
            logging.info(status_str)

            status_str = "Current hand: {}".format(self.current_player.hand_to_string())
            print(status_str)
            logging.info(status_str)

        status_str = "New game step {}".format(self.game_step)
        print(status_str)
        logging.info(status_str)

    def bot_draw_cards(self):

        print("drawing cards")
        logging.info("player_draw_cards")

        # for each card to draw
        for i in range(constants.NUM_PLAYER_CARDS_DRAW):

            card = self.player_card_deck.draw()
            status_str = "Card drawn {}: {}".format(i, card)
            print(status_str)
            logging.info(status_str)

            if isinstance(card, EpidemicCard):

                card.cause_epidemic()

            else:
                try:
                    self.current_player.add_card(card)

                except Exception as e:

                    if str(e.args[0]) == constants.PLAYER_HAND_FULL_ERROR:

                        print(str(e))

                        player_hand_with_new_card = []
                        player_hand_with_new_card.extend(self.current_player.cards())
                        player_hand_with_new_card.append(e.args[1])
                        card_colors = [card.color for card in player_hand_with_new_card]
                        card_colors = Counter(card_colors)
                        least_common = card_colors.most_common()[-1]
                        least_common_color = least_common[0]

                        for card in player_hand_with_new_card:
                            
                            #if least common color get rid of it
                            if card.color == least_common_color:

                                if card == e.args[1]:
                                    self.player_card_discard_deck.add(card)
                                else:
                                    self.current_player.discard_card(card) #don't need to add b/c appended to list reference above
                                    self.current_player.add_card(e.args[1])
                                break

    def _action_arguments(self, action_name):

        # give list(available options depending on the action choice)
        options = None
        if action_name == "drive_ferry":
            options = self.current_player.current_city.neighbors
        elif action_name == "direct_flight":
            options = [card.city for card in self.current_player.cards()]
        elif action_name == "charter_flight":
            options = [*self.city_dict.values()]
        elif action_name == "shuttle_flight":
            city_list = [*self.city_dict.values()]
            options = list(filter(lambda city: city.has_research_station, city_list))
        elif action_name == "build_research_station":
            options = [self.current_player.current_city]
        elif action_name == "treat_disease":
            options = [self.current_player.current_city.disease]
        elif action_name == "discover_cure":
            card_colors = [card.color for card in self.current_player.cards()]
            max_color = max(card_colors, key=card_colors.count)
            options = [self.disease_dict[max_color]]
        elif action_name == "give_knowledge":
            options = [*self.player_dict.values()]
            options = list(filter(lambda player: player != self.current_player, options))
        elif action_name == "take_knowledge":
            options = [*self.player_dict.values()]
            options = list(filter(lambda player: player != self.current_player, options))
        elif action_name == "discard_card":
            options = self.current_player.cards()

        return options

    def render(self, mode):
        pass
        # print("Game step {}".format(self.game_step))

    def shortest_paths(self, start_city):
        '''Dijkstra's shortest path'''
        # set all city distances to infinity, except current city zero
        self.city_dist = {city_name: math.inf for city_name in self.city_dict.keys()}
        self.city_dist[start_city.name] = 0
        cities_in_player_hand = [card.city.name for card in self.current_player.cards()]

        # add current city to unvisited_queue
        unvisited_queue = []#Queue(maxsize=len(self.city_dist))
        unvisited_queue.append(start_city)#unvisited_queue.put(start_city)
        visited_list = []

        # for next city in unvisited_queue, if no cities left then finish
        while unvisited_queue:#not unvisited_queue.empty():
            
            current_city = unvisited_queue.pop(0)#unvisited_queue.get()

            # find all neighbors of current city
            # current_city.neighbors
            neighbors = [neighbor for neighbor in current_city.neighbors]


            # #FIXME
            # # if current city in player cards hand, then all cities are neighbors, current city card is played
            # if current_city.name in cities_in_player_hand:
            #     neighbors.extend([*self.city_dict.values()])
            #     cities_in_player_hand.remove(current_city.name)
            #
            # # player cards in hand for direct flight
            # for _ in range(len(cities_in_player_hand)):
            #     city_name = cities_in_player_hand[0] #b/c being removed in for loop
            #     city = self.city_dict[city_name]
            #     neighbors.append(city)
            #     cities_in_player_hand.remove(city_name)
            #
            # # if current city has research station then all cities with research station are neighbors
            # if current_city.has_research_station:
            #     city_research_station_list = list(filter(lambda city: city.has_research_station, [*self.city_dict.values()]))
            #     neighbors.extend(city_research_station_list)

            # remove duplicate neighbors
            neighbors = list(set(neighbors))

            #remove itself (may be added during charter flight or research station shuttle flight)
            if current_city in neighbors:
                neighbors.remove(current_city)
            
            # get rid of neighbors are in visited list
            neighbors = list(filter(lambda city: city not in visited_list, neighbors))
            
            # get rid of neighbors that are in on visited queue already
            neighbors = list(filter(lambda  city: city not in unvisited_queue, neighbors))

            # set all neighbors to distance 1 + current city distance
            current_city_dist = self.city_dist[current_city.name]

            for neighbor in neighbors:
                self.city_dist[neighbor.name] = 1 + current_city_dist

            # add neighbors to unvisited_queue
            [unvisited_queue.append(neighbor) for neighbor in neighbors]

            # add current city to visited list
            visited_list.append(current_city)

        return self.city_dist
    
    def reward_level(self):
        
        return self.reward_level




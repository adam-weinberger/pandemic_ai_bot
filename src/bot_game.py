from game import Game
from disease import Disease
import constants
from cards import EpidemicCard
import pandas as pd
from infection_rate import InfectionRate
from outbreak_counter import OutbreakCounter
from collections import Counter
import random
from gym import spaces
import numpy as np
from city import City
import logging
import pdb


class BotGame(Game):

    def __init__(self, num_players, num_epidemics):

        super().__init__(num_players, num_epidemics)

        self.create_action_dict()

        self.state_df = None

        self.create_game_steps()

        self.reward_level = 0
        _, _ = self.game_state_reward()

        self.info = {}

        # initialize game object. Game has players, epidemics, diseases. it takes care of managing each turn


    def reset(self):

        self.disease_dict = {color: Disease(color) for color in constants.DISEASE_COLORS}

        # create board,player cards, decks, players
        random.seed(235)
        self.create_cities()
        self.create_decks()
        self.create_players()

        self.create_action_dict()

        self.state_df = None

        self.create_game_steps()
        status_str = "Game step {}".format(self.game_step)
        print(status_str)
        logging.info(status_str)

        self.reward_level = 0
        observation, _ = self.game_state_reward()

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

        game_bot_obs_space = []

        for col in self.state_df.columns:

            if "cubes_left" in col:
                game_bot_obs_space.append(constants.NUM_CUBES + 1) #+1 b/c includes 0

            elif col in self.game_step_list:
                game_bot_obs_space.append(2)

            elif "infection_card" in col:
                game_bot_obs_space.append(2)

            elif "infection_rate" in col:
                game_bot_obs_space.append(max(constants.INFECTION_RATE))

            elif "is_cured" in col:
                game_bot_obs_space.append(2)

            elif "num_cubes" in col:
                game_bot_obs_space.append(6) #in theory it could be as high as 12 but in practice it would rarely ever get above 4 let alone six

            elif "outbreak_level" in col:
                game_bot_obs_space.append(constants.MAX_OUTBREAKS + 1) #+1 b/c includes 0

            elif "player_card" in col:
                game_bot_obs_space.append(2)

            elif "player" in col: #needs to be after game step list and player cards because they have the word player
                game_bot_obs_space.append(2)

            elif "research_station" in col:
                game_bot_obs_space.append(2)

            elif "total_diseases_cured" in col:
                game_bot_obs_space.append(len(constants.DISEASE_COLORS) + 1) #+1 b/c includes 0

        #game_bot_obs_space = tuple(game_bot_obs_space)

        return spaces.MultiDiscrete(game_bot_obs_space)


    def game_state_reward(self):

        state_dict = {}
        new_reward_level = 0
        
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
        new_reward_level -= (num_cards_discarded * 2)

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
            state_dict['num_cubes_{}'.format(city_name)] = num_cubes
            state_dict['research_station_{}'.format(city_name)] = int(has_research_station)

            new_reward_level -= num_cubes
            new_reward_level += int(has_research_station)
            

        #diseases (could also add is eradicated)
        for color, disease in self.disease_dict.items():
            state_dict['cubes_left_{}'.format(color)] = disease.num_cubes
            state_dict['is_cured_{}'.format(color)] = int(disease.is_cured)

            new_reward_level += int(disease.is_cured) * 24


        state_dict['total_diseases_cured'] = Disease.diseases_cured

        #infection rate
        state_dict['infection_rate'] = InfectionRate.infection_rate[InfectionRate.infection_level]


        #outbreak counter
        state_dict['outbreak_level'] = OutbreakCounter.outbreak_level
        new_reward_level -= OutbreakCounter.outbreak_level * 12
        

        #player, TODO add shortest paths
        # TODO distance to research station, 3 cube cities for reward level
        for player_name, player_obj in self.player_dict.items():
            for city_name, city_obj in self.city_dict.items():
                state_dict['{}_in_{}'.format(player_name, city_name)] = int(player_obj.current_city == city_obj)

        #state of game info TODO 1:1 with which actions are valid
        for game_step in self.game_step_list:
            if game_step == self.game_step:
                state_dict[game_step] =  1
            else:
                state_dict[game_step] = 0

        #convert to pandas and np
        state_df = pd.DataFrame(state_dict, index=[0])
        state_df = state_df.sort_index(axis=1)
        state_np = state_df.to_numpy()
        state_np = np.resize(state_np, (len(state_dict),))

        # +[0, 0, 5, 10, 15, 20, 20, ...] for [0, 1, 2, 3, 4, 5, 6, ...] of the same color cards in a single player's hand
        color_rewards = [0, 0, 5, 10, 15, 20] + [20] * (constants.HAND_SIZE_LIMIT - 5)
        for player in [*self.player_dict.values()]:
            card_colors = [card.color for card in player.player_hand.hand if not isinstance(card, EpidemicCard)]
            card_colors = Counter(card_colors)
            new_reward_level += sum([color_rewards[count] for count in card_colors.values()])


        reward = new_reward_level - self.reward_level

        self.reward_level = new_reward_level

        self.state_df = state_df

        return state_np, reward

    def check_done(self):

        done = False
        diseases_cured = 0

        for disease in [*self.disease_dict.values()]:
            if int(disease.is_cured):
                diseases_cured += 1

        if diseases_cured == len(self.disease_dict):
            done = True

        if OutbreakCounter.outbreak_level == 8:
            done = True

        for disease in [*self.disease_dict.values()]:
            if disease.num_cubes <= 0:
                done = True

        if len(self.player_card_discard_deck.card_list) == 0 and self.game_step == "draw_cards":
            done = True

        return done
        


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
                reward = -1
                observation, _ = self.game_state_reward()
                done = self.check_done()
                
                return observation, reward, done, info

            self._increment_game_step()

            observation, reward = self.game_state_reward()
            done = self.check_done()

            status_str = "Action chosen: {}".format(bot_response)
            print(status_str)
            logging.info(status_str)

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
                reward = -1
                observation, _ = self.game_state_reward()
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
                reward = -1
                observation, _ = self.game_state_reward()
                done = self.check_done()

                return observation, reward, done, info

            self._increment_game_step()
                        
        # if not elif b/c player arg 4 goes straight to draw cards
        if self.game_step == "draw cards":

            try:
                self.bot_draw_cards()

            except Exception as e:

                if str(e) == constants.PLAYER_HAND_FULL_ERROR:

                    observation, reward = self.game_state_reward()
                    done = self.check_done()
                    return observation, reward, done, info

                        
            self._increment_game_step()
        
        observation, reward = self.game_state_reward()
        done = self.check_done()
        
        return observation, reward, done, info


    def valid_actions(self):

        valid_action_list = ['drive_ferry']

        if len(self.current_player.cards()) > 0:
            valid_action_list.append('direct_flight')

        if self.current_player.player_hand.contains_city(self.current_player.current_city):
            valid_action_list.append('charter_flight')

        if self.current_player.current_city.has_research_station and City.research_station_counter > 1:
            valid_action_list.append('shuttle_flight')

        if City.research_station_counter < constants.MAX_RESEARCH_STATIONS and not self.current_player.current_city.has_research_station and self.current_player.player_hand.contains_city(self.current_player.current_city):
            valid_action_list.append('build_research_station')
        
        if self.current_player.current_city.total_disease_cubes() > 0:
            valid_action_list.append('treat_disease')
        
        card_colors = [card.color for card in self.current_player.player_hand.hand if not isinstance(card, EpidemicCard)]
        card_colors = Counter(card_colors)
        max_card_color = max([count for count in card_colors.values()])
        if self.current_player.current_city.has_research_station and max_card_color >= constants.NUM_CARDS_FOR_CURE: #wont work for any roles that require different number of cards for cure (TODO)
            # valid_action_list.append('discover_cure')
            pass
        
        # hard to check if the players are in the same city especially if there are more than 2 players (TODO)
        if  not self.current_player.player_hand.contains_city(self.current_player.current_city):
            valid_action_list.append('give_knowledge')

        
        # hard to check criteria especially with more than 2 players (TODO)
        # valid_action_list.append("take_knowledge")

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

        logging.info("player_draw_cards")

        # for each card to draw
        for _ in range(constants.NUM_PLAYER_CARDS_DRAW):
            card = self.player_card_deck.draw()
            status_str = "Card drawn: {}".format(card)
            print(status_str)
            logging.info(status_str)

            if isinstance(card, EpidemicCard):
                pdb.set_trace()
                card.cause_epidemic()

            
            else:
                self.current_player.add_card(card)


    def render(self, mode):
        pass
        # print("Game step {}".format(self.game_step))

    # def dijkstra(self, aGraph, start, target):
    #     '''Dijkstra's shortest path'''
    #     # Set the distance for the start node to zero
    #     start.set_distance(0)
    #
    #     # Put tuple pair into the priority queue
    #     unvisited_queue = [(v.get_distance(), v) for v in aGraph]
    #     heapq.heapify(unvisited_queue)
    #
    #     while len(unvisited_queue):
    #         # Pops a vertex with the smallest distance
    #         uv = heapq.heappop(unvisited_queue)
    #         current = uv[1]
    #         current.set_visited()
    #
    #         # for next in v.adjacent:
    #         for next in current.adjacent:
    #             # if visited, skip
    #             if next.visited:
    #                 continue
    #             new_dist = current.get_distance() + current.get_weight(next)
    #
    #             if new_dist < next.get_distance():
    #                 next.set_distance(new_dist)
    #                 next.set_previous(current)
    #                 print
    #                 'updated : current = %s next = %s new_dist = %s' \
    #                 % (current.get_id(), next.get_id(), next.get_distance())
    #             else:
    #                 print
    #                 'not updated : current = %s next = %s new_dist = %s' \
    #                 % (current.get_id(), next.get_id(), next.get_distance())
    #
    #         # Rebuild heap
    #         # 1. Pop every item
    #         while len(unvisited_queue):
    #             heapq.heappop(unvisited_queue)
    #         # 2. Put all vertices not visited into the queue
    #         unvisited_queue = [(v.get_distance(), v) for v in aGraph if not v.visited]
    #         heapq.heapify(unvisited_queue)



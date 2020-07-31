from player_hand import PlayerHand
import pdb
import constants


class Player:

    def __init__(self, name, current_city, player_card_discard_deck):
        '''
        
        :param current_city: City
        :param hand: list of up to 7 Player_Cards
        '''

        self.current_city = current_city
        self.name = name

        #hand starts empty
        self.player_hand = PlayerHand(player_card_discard_deck)

    def drive_ferry(self, new_city):
        '''
        move to a connected position
        :param new_city: City
        :return: 
        '''

        if new_city.is_connected(self.current_city):
            self.current_city = new_city
        else:
            raise ValueError("New position is not adjacent to player's position")

    def direct_flight(self, new_city):
        '''
        
        :param new_city: City
        :return: 
        '''
        if not self.player_hand.contains_city(new_city):
            raise ValueError("New city card not in player's hand")

        self.current_city = new_city
        self.discard_city(new_city)

    def charter_flight(self, new_city):
        '''
        Play the card matching your current city to fly anywhere.
        :param new_city: 
        :return: 
        '''
        if not self.player_hand.contains_city(self.current_city):
            raise ValueError("Current city card not in player's hand")

        self.discard_city(self.current_city)
        self.current_city = new_city

    def shuttle_flight(self, new_city):
        '''
        Fly between two cities with research stations
        :param new_city: 
        :return: 
        '''

        research_station_here = self.current_city.has_research_station
        research_station_there = new_city.has_research_station
        if not (research_station_here and research_station_there):
            raise ValueError("Both cities need a research station")
        self.current_city = new_city

    def build_research_station(self, city=None):
        '''
        Build a research station in your current city.
        :return: 
        '''
        if city is None:
            city = self.current_city
        elif city != self.current_city:
            raise ValueError("Cannot build research station and city you are not in")
        
        if not self.player_hand.contains_city(city):
            raise ValueError("Current city card not in player's hand")

        city.add_research_station()

        self.discard_city(city)


    def treat_disease(self, disease=None):
        '''
        Remove one disease cube from current_city. If this color is cured, remove all cubes of that color from the city.
        :return: 
        '''
        if disease == None:
            disease = self.current_city.disease

        self.current_city.remove_disease_cubes(disease) #todo what if 2+ disease colors? player special powers?

    def discover_cure(self, disease=None):
        '''
        Discover a cure while at a research station by expending 5 cards of one color.
        :return: 
        '''
        #todo what cards to use if more than 5 of same color
        #todo how to account if two possible cures in hand

        if disease == None:
            disease = self.current_city.disease

        if not self.current_city.has_research_station:
            raise ValueError("Your city must have a research station to discover a cure")

        player_hand = self.player_hand
        player_hand.discover_cure(disease)

    def give_knowledge(self, other_player):
        """
        Give the card that matches your current city from/to a player
        in that same city.
        """

        current_city = self.current_city
        player_hand = self.player_hand

        if current_city != other_player.current_city:
            raise ValueError("Both players must be in same city")

        if not player_hand.contains_city(current_city):
            raise ValueError("Player does not have current city card")

        player_hand.transfer_cty(current_city, other_player)

    def take_knowledge(self, other_player):
        """
        Give the card that matches your current city from/to a player
        in that same city.
        """

        current_city = self.current_city

        if current_city != other_player.current_city:
            raise ValueError("Both players must be in same city")

        if not other_player.player_hand.contains_city(current_city):
            raise ValueError("Player does not have current city card")
            
        other_player.player_hand.transfer_cty(current_city, self)

    def add_card(self, card):

        self.player_hand.add(card)

    def discard_card(self, card):

        self.player_hand.discard(card)

    def discard_city(self, city):

        self.player_hand.discard_city(city)

    def list_actions(self):

        return constants.PLAYER_ACTION_LIST
        
    def hand_to_string(self):
        return str(self.player_hand)

    def select_card(self, card_ind):
        return self.player_hand.hand[card_ind]

    def __str__(self):
        return "Player({}, {})".format(self.name, self.current_city)

    def cards(self):

        return self.player_hand.cards()
    

    

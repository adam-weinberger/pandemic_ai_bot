import constants as constants
from reward_tracker import reward_tracker


class PlayerHand:

    def __init__(self, player_card_discard_deck, size_limit=constants.HAND_SIZE_LIMIT):

        self.hand = []
        self.size_limit = size_limit
        self.player_card_discard_deck = player_card_discard_deck

    def discard(self, card):
        '''
                
        :param card: 
        :return: 
        '''

        reward_tracker.change_reward_level('hand_{}'.format(str(self)))
        self.player_card_discard_deck.add(card)
        self.hand.remove(card)


    def discard_city(self, city):
        '''

        :param city: 
        :return: 
        '''

        card_to_discard = self.contains_city(city)
        
        if not card_to_discard:
            raise ValueError("City card not in player's hand")

        self.player_card_discard_deck.add(card_to_discard)
        self.hand.remove(card_to_discard)
        reward_tracker.change_reward_level('hand_{}'.format(str(self)))

    def add(self, card):
        '''
        :param name:
        :param card: 
        :return: 
        '''

        if card in self.hand:
            raise ValueError("Can't add, card already in player hand")

        if len(self.hand) == self.size_limit:
            raise ValueError(constants.PLAYER_HAND_FULL_ERROR)

        self.hand.append(card)
        reward_tracker.change_reward_level('hand_{}'.format(str(self)))

    def transfer_cty(self, city, other_player):
        '''
        transfer card from1 player to another play        
        :param card: 
        :return: 
        '''

        card = self.contains_city(city)
        
        if not card:
            raise ValueError("City card not in player's hand")

        other_player.player_hand.add(card)
        self.hand.remove(card)
        reward_tracker.change_reward_level('hand_{}'.format(str(self)))

        return card

    def discover_cure(self, disease, cards_required=constants.NUM_CARDS_FOR_CURE):
        '''
        :param disease: disease object
        :param cards_required: most roles require 5, some require less
        :return: 
        '''

        disease_color = disease.color
        cure_cards = list(filter(lambda card: card.color == disease_color, self.hand))
        if len(cure_cards) < cards_required:
            raise ValueError("Not enough cards to discover cure for {}".format(disease_color))
        [self.discard(card) for card in cure_cards]

        reward_tracker.change_reward_level('hand_{}'.format(str(self)))

        disease.cure()


    def contains_city(self, city):
        '''
        
        :param city: 
        :return: 
        '''
        for card in self.hand:
            if card.city == city:
                return card

        return False

    def __contains__(self, card):
        '''
        
        :param card: 
        :return: 
        '''

        return card in self.hand

    def __str__(self):
        return str([str(x) for x in self.hand])

    def cards(self):

        return self.hand


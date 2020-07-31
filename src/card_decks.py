from random import shuffle
from reward_tracker import reward_tracker



class CardDeck(object):

    def __init__(self):

        self.card_list = []

    def draw(self):
        return self.card_list.pop()

    def add(self, card):
        self.card_list.append(card)

    def shuffle(self):
        shuffle(self.card_list)

    def to_string(self):
        return str(self.card_list)

    def len(self):

        return len(self.card_list)
        
class InfectionCardDeck(CardDeck):

    
    def draw_bottom_card(self):
        return self.card_list.pop(0)

    
    def add_discard_deck(self, infection_card_discard_deck):
        self.card_list = self.card_list.extend(infection_card_discard_deck.card_list)

class InfectionCardDiscardDeck(CardDeck):

    def clear_deck(self):
        self.card_list = []


class PlayerCardDeck(CardDeck):

    
    def draw(self):

        if len(self.card_list) == 0:
            # RuntimeError("No player cards left, you lose", "lose")
            print("No player cards left, you lose")

        return self.card_list.pop()

    def insert_card(self, ind, card):

        self.card_list.insert(ind, card)



class PlayerCardDiscardDeck(CardDeck):

    def pick_card(self, card):

        if card in self.card_list:
            self.card_list.remove(card)
            return card
        else:
            raise ValueError("Card is not an player discard deck")

    def add(self, card):
        self.card_list.append(card)
        reward_tracker.change_reward_level('player_card_discarded')
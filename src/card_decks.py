from random import shuffle

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
        self.card_list.extend(infection_card_discard_deck.card_list)
        infection_card_discard_deck.clear_deck()

class InfectionCardDiscardDeck(CardDeck):

    def clear_deck(self):
        self.card_list = []


class PlayerCardDeck(CardDeck):

    
    def draw(self):
        #
        # if not self.card_list:
        #     RuntimeError("No player cards left, you lose", "lose")
        #     # print("No player cards left, you lose")

        try:
            card = self.card_list.pop()
        except Exception as e:
            raise RuntimeError("No player cards left, you lose", "lose")

        return card

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
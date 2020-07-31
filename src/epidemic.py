from infection_rate import InfectionRate
import constants as constants


class Epidemic(object):
    def __init__(self, infection_card_deck, infection_card_discard_deck):
        self.infection_card_deck = infection_card_deck
        self.infection_card_discard_deck = infection_card_discard_deck

    def cause_epidemic(self):

        InfectionRate.increment()

        infection_card = self.infection_card_deck.draw_bottom_card()
        infection_card.infect(amount=constants.CITY_MAX_DISEASE_CUBES)

        self.infection_card_discard_deck.shuffle()
        self.infection_card_deck.add_discard_deck(self.infection_card_discard_deck)

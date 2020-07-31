import abc
from epidemic import Epidemic

class Card(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class EventCard(Card):
    
        
    @abc.abstractmethod
    def action(self):
        pass

class EpidemicCard(Card):

    def __init__(self, i, player_card_discard_deck, infection_card_deck, infection_card_discard_deck):

        self.epidemic = Epidemic(infection_card_deck, infection_card_discard_deck)
        self.player_card_discard_deck = player_card_discard_deck
        super().__init__('epidemic_{}'.format(i))

    def cause_epidemic(self):

        self.epidemic.cause_epidemic()
        self.player_card_discard_deck.add(self)

class PlayerCityCard(Card):

    def __init__(self, city):

        self.city = city
        self.color = city.disease.color
        super().__init__(city.name)

    def __str__(self):
        return 'PlayerCityCard({}, {})'.format(self.name, self.color)

class InfectionCard(Card):

    def __init__(self, city):

        self.city = city
        super().__init__(city.name)

    def infect(self, amount=1):

        print("Infecting {} with {}".format(str(self), amount))
        self.city.add_disease_cubes(self.city.disease, amount)

    def __str__(self):
        return 'InfectionCard({}, {})'.format(self.name, self.city.disease.color)


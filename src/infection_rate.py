import constants

class InfectionRate(object):

    infection_level = 0
    infection_rate = constants.INFECTION_RATE
    
    @classmethod
    def get_infection_rate(cls):

        return cls.infection_rate[cls.infection_level]

    @classmethod
    def increment(cls):

        cls.infection_level += 1



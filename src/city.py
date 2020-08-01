from outbreak_counter import OutbreakCounter
import constants as constants

class City:

    
    research_station_counter = 0


    def __init__(self, name, disease, neighbors=[]):
        '''
        :param disease: 
        :param name: 
        '''

        self.name = name
        self.disease = disease

        self.neighbors = neighbors
        self.disease_cubes = {color: 0 for color in constants.DISEASE_COLORS} #TODO instantiate diseases in diseases.py file?
        self.has_research_station = False

    def add_neighbor(self, other_city):
        '''
        
        :param other_city: 
        :return: 
        '''

        self.neighbors.append(other_city)

    def add_disease_cubes(self, disease=None, amount=1, ignore_cities=[]):
        '''
        
        :param disease: 
        :param amount: 
        :param ignore_cities: 
        :return: 
        '''

        #city has already had outbreak this turn, cannot be reinfected
        if self in ignore_cities:
            return

        #use city's designated disease if not given
        if disease is None:
            disease = self.disease
        color = disease.color

        #add cubes to list
        disease_cubes = self.disease_cubes
        if color not in disease_cubes.keys():
            disease_cubes[color] = amount
            disease.infect(amount)
        else:
            disease_cubes[color] += amount
            disease.infect(amount)

        #cubes cannot exceed maximum limit, outbreak occurs and other cities are infected
        if disease_cubes[color] > constants.CITY_MAX_DISEASE_CUBES:
            decrease_amount = disease_cubes[color] - constants.CITY_MAX_DISEASE_CUBES
            disease_cubes[color] -= decrease_amount
            disease.disinfect(decrease_amount)
            OutbreakCounter.increment()

            #once city has had outbreak,cannot have another outbreak in the same turn
            ignore_cities.append(self)

            #infect neighbor cities
            for neighbor in self.neighbors:
                neighbor.add_disease_cubes(disease, amount, ignore_cities)



    def remove_disease_cubes(self, disease=None, amount=1):
        '''
        
        :param disease: 
        :param amount: 
        :return: 
        '''

        if disease is None:
            disease = self.disease
        color = disease.color

        disease_cubes = self.disease_cubes

        if color not in disease_cubes.keys() or disease_cubes[color] == constants.CITY_MIN_DISEASE_CUBES:
            raise ValueError("Cannot remove disease {} cubes because city has none".format(color))

        if disease.is_cured:
            amount = constants.CITY_MAX_DISEASE_CUBES

        #cannot have less disease cubes than 0
        if amount > disease_cubes[color]:
            amount = disease_cubes[color]
        disease_cubes[color] -= amount
        disease.disinfect(amount)


    def add_research_station(self):
        '''
        
        '''

        if self.has_research_station:
            raise ValueError("{} already has a reasearch station".format(self.name))
        
        
        # TODO if you have reached the max number of research stations you are allowed to move
        if City.research_station_counter == constants.MAX_RESEARCH_STATIONS:
            raise ValueError("Reach max of {} research stations".format(City.research_station_counter))
        
        City.research_station_counter += 1

        self.has_research_station = True

    def is_connected(self, other_city):
        '''

        :return: 
        '''

        return other_city in self.neighbors

    def total_disease_cubes(self):
        
        return sum([*self.disease_cubes.values()])
        
    def __str__(self):
        return 'City({}, {}, {} cubes)'.format(self.name, self.disease.color, self.disease_cubes[self.disease.color])

import constants as constants
from reward_tracker import reward_tracker


class Disease(object):

    diseases_cured = 0

    def __init__(self, color, num_cubes=constants.NUM_CUBES):

        
        self.num_cubes = num_cubes
        self.color = color
        self.is_cured = False
        self.is_eradicated = False

    def infect(self, amount=1):

        if self.is_eradicated:
            print("{} eradicated, can't infect".format(self.color))

        self.num_cubes -= amount

        reward_tracker.change_reward_level('infect_{}'.format(amount))

        if self.num_cubes <= 0:
            # raise RuntimeError("No disease {} cubes left, you lose".format(self.color), "lose")
            print("No disease {} cubes left, you lose".format(self.color))


    def disinfect(self, amount=1):

        self.num_cubes += amount

        if self.num_cubes > constants.NUM_CUBES:
            raise ValueError("Cannot disinfect, because all disease cubes are off the board")

        reward_tracker.change_reward_level('disinfect_{}'.format(amount))

        #TODO check eradication

    
    def cure(self):

        self.is_cured = True
        print("You cured {}".format(self.color))
        Disease.diseases_cured += 1

        reward_tracker.change_reward_level('cure')

        if self.num_cubes == constants.NUM_CUBES:
            self.is_eradicated = True

        if Disease.diseases_cured == len(constants.DISEASE_COLORS):
            # raise RuntimeError("You cured all of the diseases, you win", "win")
            print("You cured all of the diseases, you win")

    def __str__(self):

        return "Disease({}, {} cubes left, {} is cured)".format(self.color, self.num_cubes, self.is_cured)





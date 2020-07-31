from reward_tracker import reward_tracker
import constants


class OutbreakCounter(object):

    outbreak_level = 0

    @classmethod
    def increment(cls):

        cls.outbreak_level += 1

        reward_tracker.change_reward_level('outbreak')

        if cls.outbreak_level == constants.MAX_OUTBREAKS:
            #raise RuntimeError("outbreak level 8, you lose", "lose")
            print("outbreak level {}, you lose".format(constants.MAX_OUTBREAKS))

class RewardTracker(object):

    def __init__(self):

        self.reward_level = 0

    def change_reward_level(self, change_str):

        # player_card_discarded
        # added_research_station
        # infect_{}
        # disinfect_{}
        # cure
        # outbreak
        # 'hand_{}'.format(str(self))
        # print(change_str)
        amount = 0

        # -2 for every player card in the discard pile
        # +1 for every research station built
        # -1 for every disease cube on the board
        # +24 for every disease cured
        # -12 for every outbreak level
        # +[5, 10, 15, 20] for [2, 3, 4, 5] of the same color cards in a single player's hand
        # TODO distance to research station, 3 cube cities

        self.reward_level += amount

#TODO how to clean up
reward_tracker = RewardTracker()

from game_env import GameEnv
import numpy as np

class ExpertGame(GameEnv):

    def __init__(self, num_players, num_epidemics):

        super().__init__(num_players, num_epidemics)

        print('starting expert game')

        self.expert_dict = {}

        self.expert_dict['actions'] = []
        self.expert_dict['episode_returns'] = []
        self.expert_dict['rewards'] = []
        self.expert_dict['obs'] = []
        self.expert_dict['episode_starts'] = []
        self.episode_start = True
        self.episode_return = 0
        self.current_obs = self.game.reset()
        self.ctr = 0
        self.episode_ctr = 0
        self.episode_length = 40
        self.n_episodes = 4

        # self.inverse_action_dict = {v: k for k, v in self.game.action_dict.items()}
        

    def step(self):

        self.expert_dict['episode_starts'].append(self.episode_start)

        # if beginning of an episode
        if self.episode_start:
            self.episode_start = False
            self.current_obs = self.reset()

        # observation comes before action
        self.expert_dict['obs'].append(self.current_obs)


        if 'action' in self.game.game_step:

            valid_action_list = self.game.valid_actions()
            valid_action_list_len = range(len(valid_action_list))
            valid_action_list_numbered = ["{}) {}".format(i, str(valid_action_list[i])) for i in valid_action_list_len]
            print(valid_action_list_numbered)

            action = None
            while action not in valid_action_list_len:
                try:
                    action = int(input("choose action:"))
                except Exception as e:
                    print(e)
                    continue
                


        elif 'arg' in self.game.game_step:

            valid_action_list = self.game._action_arguments(self.game.current_action)
            valid_action_list_len = range(len(valid_action_list))
            valid_action_list_numbered = ["{}) {}".format(i, str(valid_action_list[i])) for i in valid_action_list_len]
            print(valid_action_list_numbered)

            action = None
            while action not in valid_action_list_len:
                try:
                    action = int(input("choose arg:"))
                except Exception as e:
                    print(e)
                    continue
                

            try:
                valid_action_list_names = [None] * len(valid_action_list)
                
                for item in self.game.action_dict.items():
                    if item[1] in valid_action_list:
                        ind = valid_action_list.index(item[1])
                        valid_action_list_names.insert(ind, item[0])

                valid_action_list_names = [name for name in valid_action_list_names if name]

            except Exception as e:
                import pdb
                pdb.set_trace()

            valid_action_list = valid_action_list_names

        action_name = valid_action_list[action]
        action = self.action_list.index(action_name)

        self.expert_dict['actions'].append(np.array([action])) # how to undo

        observation, reward, done, info = self.game.step(action_name)

        self.ctr += 1

        if self.ctr == self.episode_length:
            self.ctr = 0
            self.episode_ctr += 1
            done = True
        
        
        self.current_obs = observation
        self.expert_dict['rewards'].append(reward)
        
        self.episode_start = done

        if done:
            self.expert_dict['episode_returns'].append(self.episode_return)
            self.episode_return = 0
            self.reset()

        self.episode_return += reward

        if self.episode_ctr == self.n_episodes:
            return True

        return False

    def reset(self):
        
        observation = self.game.reset()
        return observation  # reward, done, info can't be included

    def render(self, mode="human"):
        self.game.render(mode)

    def close(self):
        pass

    def reward_level(self):
        return self.game.reward_level()

if __name__ == '__main__':
    print(1)

    g = ExpertGame(1, 2)
    print(2)

    
    stop_playing = False
    while not stop_playing:
        stop_playing = g.step()

    for k, v in g.expert_dict.items():
        g.expert_dict[k] = np.array(v)

    np.savez("../logs/expert_pandemic.npz", **g.expert_dict)

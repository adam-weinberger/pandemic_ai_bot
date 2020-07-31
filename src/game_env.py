import gym
from gym import spaces
from bot_game import BotGame
from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from stable_baselines.common.env_checker import check_env
from stable_baselines.common.callbacks import CheckpointCallback


class GameEnv(gym.Env):

    """Custom Environment that follows gym interface"""

    metadata = {"render.modes": ["human"]}

    def __init__(self, num_players=2, num_epidemics=4):
        super(GameEnv, self).__init__()

        self.game = BotGame(num_players, num_epidemics)

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:

        self.action_list = list(self.game.action_dict.keys())
        self.action_space = spaces.Discrete(len(self.action_list))

        
        self.observation_space = self.game.create_observation_space()

    def step(self, action):
        action_name = self.action_list[action]
        observation, reward, done, info = self.game.step(action_name)
        return observation, reward, done, info

    def reset(self):
        
        observation = self.game.reset()
        return observation  # reward, done, info can't be included

    def render(self, mode="human"):
        self.game.render(mode)

    def close(self):
        pass

if __name__ == "__main__":

    game_env = GameEnv()
    check_env(game_env)

    model = PPO2(MlpPolicy, game_env, verbose=1)

    checkpoint_callback = CheckpointCallback(save_freq=1000, save_path='../logs/',
                                             name_prefix='rl_model')
    model.learn(total_timesteps=100000, callback=checkpoint_callback)

    obs = game_env.reset()

    for i in range(1000):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = game_env.step(action)
        game_env.render()

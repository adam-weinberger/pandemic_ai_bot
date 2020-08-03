import gym
from gym import spaces
from bot_game import BotGame
from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from stable_baselines.common.env_checker import check_env
from stable_baselines.common.callbacks import CheckpointCallback
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from setuptools import  setup
from gym.envs.registration import register
import caffeine
import os
import shutil
from timeout_callback import TimeoutCallback

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
        observation, reward, done, info = self.game.step(action_name) #TODO rescale observations
        return observation, reward, done, info

    def reset(self):
        
        observation = self.game.reset()
        return observation  # reward, done, info can't be included

    def render(self, mode="human"):
        self.game.render(mode)

    def close(self):
        pass

    def reward_level(self):
        return self.game.reward_level()

if __name__ == "__main__":

    register(
        id='pandemic-v0',
        entry_point='gym_foo.envs:FooEnv',
    )

    game_env = GameEnv()
    print("Checking")
    check_env(game_env)

    # Create save dir
    save_dir = "../logs/"
    model_filename = "rl_model"

    checkpoint_dir = save_dir + "most_recent_models/"
    try:
        shutil.rmtree(checkpoint_dir)
    except OSError as e:
        print(e)

    os.mkdir(checkpoint_dir)


    # load the model, and when loading set verbose to 1
    print("Loading")
    # loaded_model = PPO2.load(save_dir + model_filename, verbose=1, env=SubprocVecEnv([GameEnv]))
    loaded_model = PPO2(MlpPolicy, SubprocVecEnv([GameEnv, GameEnv]), verbose=1)

    # show the save hyperparameters
    print("loaded:", "gamma =", loaded_model.gamma, "n_steps =", loaded_model.n_steps)

    # model = PPO2(MlpPolicy, game_env, verbose=1)

    checkpoint_callback = CheckpointCallback(save_freq=10000, save_path=checkpoint_dir,
                                             name_prefix=model_filename)

    print("Learning")
    loaded_model.learn(total_timesteps=1000000, callback=checkpoint_callback)

    print("Saving")
    os.remove(save_dir + model_filename + ".zip")
    loaded_model.save(save_dir + model_filename)


    # obs = game_env.reset()
    #
    # for i in range(1000):
    #     action, _states = loaded_model.predict(obs)
    #     obs, rewards, dones, info = game_env.step(action)
    #     game_env.render()

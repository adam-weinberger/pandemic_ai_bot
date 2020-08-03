from stable_baselines.common.callbacks import BaseCallback

class TimeoutCallback(BaseCallback):
    """
    Stop the training once a threshold in episodic reward
    has been reached (i.e. when the model is good enough).
    It must be used with the `EvalCallback`.
    :param reward_threshold: (float)  Minimum expected reward per episode
        to stop training.
    :param verbose: (int)
    """
    def __init__(self, reward_threshold: float, verbose: int = 0, window_length: int = 10):
        super(TimeoutCallback, self).__init__(verbose=verbose)
        self.reward_threshold = reward_threshold
        self.last_n_rewards = [0] * window_length

        self.prev_reward_level = self.parent.training_env.reward_level()

    def _on_step(self) -> bool:
        assert self.parent is not None, ("`StopTrainingOnRewardThreshold` callback must be used "
                                         "with an `EvalCallback`")
        # Convert np.bool to bool, otherwise callback.on_step() is False won't work
        current_reward_level = self.parent.training_env.reward_level()
        reward = current_reward_level - self.prev_reward_level
        self.prev_reward_level = current_reward_level
        self.last_n_rewards = self.last_n_rewards[1:]
        self.last_n_rewards.append(reward)
        mean_reward = float(sum(self.last_n_rewards) / len(self.last_n_rewards))
        

        continue_training = bool(mean_reward < self.reward_threshold)
        if self.verbose > 0 and not continue_training:
            print("Stopping training because the mean reward {:.2f} "
                  " is above the threshold {}".format(mean_reward, self.reward_threshold))

        if not continue_training:
            self.parent.training_env.reset()

        return continue_training

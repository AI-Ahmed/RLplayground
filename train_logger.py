from _collections import deque
import numpy as np
from torch.utils.tensorboard import SummaryWriter
import torch
import os
import matplotlib.pyplot as plt
from time import time

class logger(object):
    def __init__(self, k, log_frequency=10):
        self.log_frequency = log_frequency
        self.last_episodes_total_rewards = deque(maxlen=k)
        self.train_start = time()
        self.total_steps  = 0
        self.done_episodes = 0
        self.last_time = self.train_start
        self.last_steps = 0

    def get_last_k_episodes_mean(self):
        return np.mean(self.last_episodes_total_rewards)

    def update_train_episode(self, episode_rewards):
        self.last_episodes_total_rewards.append(np.sum(episode_rewards))
        self.total_steps += len(episode_rewards)
        self.done_episodes += 1

    def output_stats(self, actor_stats=None):
        time_passed = time() - self.train_start
        last_k_score = self.get_last_k_episodes_mean()
        print('Episodes done: ', self.done_episodes)
        print("\t# Steps %d, time %d mins; avg-%d %.2f:" % (self.total_steps, time_passed / 60, len(self.last_episodes_total_rewards), last_k_score))
        print("\t# steps/sec avg: %.3f " % (self.total_steps / time_passed))
        # print("\t# steps/sec avg: %.3f " % ((self.total_steps- self.last_steps) / (time_passed - self.last_time)))
        print("\t# Agent stats: ", actor_stats)
        self.last_steps = self.total_steps
        self.last_time = time_passed

        return last_k_score

    def log_test(self, score):
        print("Test score: %.3f "%score)

# class TB_logger(logger):
#     def __init__(self, k, tb_writer):
#         super(TB_logger, self).__init__(k)
#         self.tb_writer = tb_writer
#
#     def log_traine_episode(self, episode_number, episode_rewards, actor_stats):
#         last_k_scores = super(TB_logger, self).log_train_episode(episode_number, episode_rewards, actor_stats)
#         self.tb_writer.add_scalar('1.last_%s_episodes_avg'%len(self.last_episodes_total_rewards), torch.tensor(last_k_scores), global_step=episode_number)
#         self.tb_writer.add_scalar('2.episode_score', torch.tensor(np.sum(episode_rewards)), global_step=episode_number)
#         self.tb_writer.add_scalar('3.episode_length', len(episode_rewards), global_step=episode_number)
#         self.tb_writer.add_scalar('4.avg_rewards', torch.tensor(np.mean(episode_rewards)), global_step=episode_number)
#         # cur_time = max(1, int(time() - train_start))
#         # self.tb_writer.add_scalar('5.episode_score_time_scaled', torch.tensor(episode_score), global_step=cur_time)

class plt_logger(logger):
    def __init__(self, k, log_frequency, logdir):
        super(plt_logger, self).__init__(k, log_frequency)
        os.makedirs(logdir, exist_ok=True)
        self.k = k
        self.logdir=logdir
        self.all_episode_lengths = []
        self.all_episode_total_scores = []
        self.all_avg_last_k = []
        self.test_scores = []

    def update_train_episode(self, episode_rewards):
        super(plt_logger, self).update_train_episode(episode_rewards)
        self.all_episode_lengths += [len(episode_rewards)]
        self.all_episode_total_scores += [np.sum(episode_rewards)]
        self.all_avg_last_k += [self.get_last_k_episodes_mean()]

    def output_stats(self, actor_stats=None, by_step=False):
        xs = np.arange(1, len(self.all_episode_lengths) + 1)
        x_label = 'Episode #'
        if by_step:
            xs = np.cumsum(self.all_episode_lengths)
            x_label = 'Step #'
        last_k_scores = super(plt_logger, self).output_stats(actor_stats)
        plt.plot(xs, self.all_episode_lengths)
        plt.ylabel('Length')
        plt.xlabel(x_label)
        plt.savefig(os.path.join(self.logdir, "Episode-lengths.png"))
        plt.clf()

        plt.plot(xs, self.all_episode_total_scores, label='Episode-score')
        plt.plot(xs, self.all_avg_last_k, label='Score-last %d' % self.k)
        plt.ylabel('Score')
        plt.xlabel(x_label)
        plt.legend()
        plt.savefig(os.path.join(self.logdir, "Episode-scores.png"))
        plt.clf()

        # plt.plot(np.cumsum(self.all_episode_lengths), self.all_episode_total_scores)
        # plt.ylabel('Score')
        # plt.xlabel('Step #')
        # plt.savefig(os.path.join(self.logdir, "Episode-scores-by-step.png"))
        # plt.clf()


        return last_k_scores

    def log_test(self, score):
        super(plt_logger, self).log_test(score)
        self.test_scores += [score]
        plt.plot( np.linspace(start=1, stop=max(2,len(self.all_avg_last_k)), num=len(self.test_scores)), self.test_scores)
        plt.ylabel('test_score-last %d'%self.k)
        plt.xlabel('Episode #')
        plt.savefig(os.path.join(self.logdir, "Test_scores.png"))
        plt.clf()
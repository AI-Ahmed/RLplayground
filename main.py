import numpy as np
import os
from time import time, sleep
import random
import gym
import descrete_agents
import continous_agents
import train_logger
import torch


def train(env, actor, train_episodes, score_scope, solved_score):
    next_progress_checkpoint = 1
    train_start = time()
    # logger = TB_logger(200, SummaryWriter(log_dir=os.path.join(TRAIN_DIR, "tensorboard_outputs",  actor.name)))
    logger = train_logger.plt_logger(score_scope, os.path.join(TRAIN_DIR,  actor.name))
    num_steps = 0
    for i in range(train_episodes):

        done = False
        state = env.reset()
        episode_rewards = []
        while not done:
            action = actor.process_new_state(state)
            state, reward, done, info = env.step(action)
            actor.process_output(state, reward, done)
            num_steps+=1
            episode_rewards += [reward]

        last_k_scores = logger.log(i, episode_rewards, num_steps, max(1, int(time() - train_start)), actor.get_stats())

        if last_k_scores >= next_progress_checkpoint*0.2*solved_score:
            actor.save_state(os.path.join(TRAIN_DIR, actor.name + "_%.5f_weights.pt"%last_k_scores))
            next_progress_checkpoint += 1

        if last_k_scores > solved_score:
            print("Solved in %d episodes"%i)
            break

    actor.save_state(os.path.join(TRAIN_DIR, actor.name + "_final_weights.pt"))

    env.close()

def test(env,  actor):
    actor.load_state(os.path.join(TRAIN_DIR, actor.name + "_trained_weights.pt"))

    done = False
    state = env.reset()
    all_rewards = []
    while not done:
        env.render()
        action = actor.process_new_state(state)
        state, reward, done, info = env.step(action)
        all_rewards += [reward]
    print("total reward: %f, # steps %d"%(np.sum(all_rewards),len(all_rewards)))
    env.close()


if  __name__ == '__main__':
    # Choose enviroment
    # ENV_NAME="CartPole-v1"; s=4; a=2
    # ENV_NAME="LunarLander-v2"; s=8; a=4
    ENV_NAME="LunarLanderContinuous-v2";s=8;bounderies=[[-1,-1],[1,1]]; score_scope=99; solved_score=200
    # ENV_NAME="Pendulum-v0";s=3;bounderies=[[-2],[2]]
    # ENV_NAME="BipedalWalker-v3"; s=24;bounderies=[[-1,-1,-1,-1],[1,1,1,1]]; score_scope=99; solved_score=300

    # Create agent
    NUM_EPISODES = 10000
    # actor = DQN_agent(s, a, NUM_EPISODES, train=True)
    # actor = vanila_policy_gradient_agent(s, a, NUM_EPISODES, train=True)
    # actor = actor_critic_agent(s, a, NUM_EPISODES, train=True, critic_objective="Monte-Carlo")
    # actor = actor_critic_agent(s, bounderies, NUM_EPISODES, train=True, critic_objective="Monte-Carlo")
    actor = continous_agents.DDPG(s, bounderies, NUM_EPISODES, train=True)
    # actor = continous_agents.TD3(s, bounderies, NUM_EPISODES, train=True)
    # actor = continous_agents.PPO(s, bounderies, NUM_EPISODES, train=True)

    env = gym.make(ENV_NAME)

    # set seeds
    SEED=13333
    random.seed(SEED)
    torch.manual_seed(SEED)
    env.seed(SEED)


    # Train
    os.makedirs("Training", exist_ok=True)
    TRAIN_DIR = os.path.join("Training", ENV_NAME)
    os.makedirs(TRAIN_DIR, exist_ok=True)
    # train(env, actor, NUM_EPISODES, score_scope, solved_score)

    # Test
    actor.train = False
    # actor.epsilon = 0.0
    test(env, actor)
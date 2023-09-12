import os
from multiprocessing.connection import Listener, Client
from PIL import Image
import gymnasium
from matplotlib import pyplot as plt
import numpy as np
from stable_baselines3 import DQN, PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.logger import configure
from datetime import datetime

class GameEnv(gymnasium.Env):
    def __init__(self):
        with open('seed.txt', 'r') as file:
            self.seed = int(file.read(1))
        with open('seed.txt', 'w') as file:
            file.write(str(self.seed+1))
        self.initialized = False
        self.listener_connection = None
        self.client_connection = None
        self.speed = 0.0
        self.position = 0.0
        self.dolphin_path = "..\\dolphin" + str(self.seed) + "\\Dolphin.exe"
        self.command = 'cmd /c ' + self.dolphin_path + " --script C:\\Users\\Carson\\MKAI\\Scripts\\dolphinscript.py \\b --exec C:\\Users\\Carson\\MKAI\\MKWii.iso"
        self.ydim = 90
        self.xdim = 168
        self.observation_space = gymnasium.spaces.Box(low = 0, high = 255, shape = (1, self.ydim, self.xdim), dtype=np.uint8)
        self.action_space = gymnasium.spaces.Discrete(7)
        self.initialize()
    
    def initialize(self):
        print('Starting Emulator')
        self.launch()
        dolphinListener = ('localhost', 20000+self.seed)
        listener = Listener(dolphinListener, authkey=b'supersecure')
        print('Waiting...')
        self.listener_connection = listener.accept()
        msg = self.listener_connection.recv()
        print('Message received:', str(msg))
        dolphinClient = ('localhost', 22000+self.seed)
        print('Connecting to script...')
        self.client_connection = Client(dolphinClient, authkey=b'password')
        self.client_connection.send('Testing!')
        print('Message sent.')
        self.reset()
    
    def step(self, action):
        info2 = {}
        left = False
        right = False
        sleft = False
        sright = False
        up = False
        down = False
        l = False
        screen = False
        info = False
        reward = 0
        terminated = False
        truncated = False
        if action == 0:
            left = True
        elif action == 1:
            right = True
        elif action == 2:
            sleft = True
        elif action == 3:
            sright = True
        elif action == 4:
            up = True
        elif action == 5:
            down = True
        elif action == 6:
            l = True
        self.client_connection.send({
            'Type': 'Inputs',
            'StickLeft': left,
            'StickRight': right,
            'SoftLeft': sleft,
            'SoftRight': sright,
            'Up': up,
            'Down': down,
            'L': l
            })
        while not screen or not info:
            msg = self.listener_connection.recv()
            if msg['Type'] == 'Screen' and not screen:
                obs = np.asarray(msg['Data'])
                obs = obs.astype(np.uint8)
                obs = obs.reshape((1, 90, 168))
                screen = True
            if msg['Type'] == 'Info' and not info:
                info2 = {'Speed': msg['Speed'], 'Position': msg['Position'], 'Frames': msg['Frames']}
                reward = msg['Reward']
                # print(reward)
                terminated = msg['Terminated']
                truncated = msg['Truncated']
                info = True
        return (obs, reward, terminated, truncated, info2)
                

    def launch(self):
        os.popen(self.command)
        print('Dolphin Loaded')

    def reset(self, seed = None, options = None):
        super().reset(seed=seed)
        print('resetting')
        self.client_connection.send({'Type': 'Reset'})
        while True:
            msg = self.listener_connection.recv()
            if msg['Type'] == 'Screen':
                img = np.asarray(msg['Data'])
                img = img.astype(np.uint8)
                img = img.reshape((1, 90, 168))
                return img, {}

def main():
    with open('seed.txt', 'w') as file:
            file.write(str(0))
    env = make_vec_env(GameEnv, n_envs=4, seed=1, vec_env_cls=SubprocVecEnv)
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./tbpp/")
    model.learn(total_timesteps = 5000)
    model.save("MKAIPPO")
    with open('logcontrol.txt', 'w') as file:
        file.write("Created new file!\n")
    while True:
        now = datetime.now()
        time = now.strftime("%D-%H-%M-%S")
        model.set_parameters("MKAIPPO", env)
        model.learn(total_timesteps = 25000, reset_num_timesteps=False)
        with open('logcontrol.txt', 'a') as file:
            file.write('Done Iteration!\n')
        model.save("MKAIPPO")
        with open('logcontrol.txt', 'a') as file:
            file.write('Saved Iteration!\n')

if __name__ == '__main__':
    main()
import os
from multiprocessing.connection import Listener, Client
from PIL import Image
import gym
from matplotlib import pyplot as plt
import numpy as np

class GameEnv(gym.Env):
    def __init__(self):
        self.initialized = False
        self.listener_connection = None
        self.client_connection = None
        self.speed = 0.0
        self.position = 0.0
        self.dolphin_path = "..\\dolphin\\Dolphin.exe"
        self.command = 'cmd /c ' + self.dolphin_path + " --script C:\\Users\\Carson\\MKAI\\Scripts\\dolphinscript.py \\b --exec C:\\Users\\Carson\\MKAI\\MKWii.iso"
        self.ydim = 90
        self.xdim = 168
        self.observation_space = gym.spaces.Box(low = 0, high = 255, shape = (self.ydim, self.xdim), dtype=np.uint8)
        self.action_space = gym.spaces.Discrete(6)
    
    def initialize(self):
        print('Starting Emulator')
        self.launch()
        dolphinListener = ('localhost', 20000)
        listener = Listener(dolphinListener, authkey=b'supersecure')
        print('Waiting...')
        self.listener_connection = listener.accept()
        msg = self.listener_connection.recv()
        print('Message received:', str(msg))
        dolphinClient = ('localhost', 22000)
        print('Connecting to script...')
        self.client_connection = Client(dolphinClient, authkey=b'password')
        self.client_connection.send('Testing!')
        print('Message sent.')
        self.reset()
    
    def step(self, action):
        left = False
        right = False
        a = False
        up = False
        down = False
        l = False
        screen = False
        info = False
        if action == 0:
            left = True
        elif action == 1:
            right = True
        elif action == 2:
            a = True
        elif action == 3:
            up = True
        elif action == 4:
            down = True
        elif action == 5:
            l = True
        self.client_connection.send({
            'Type': 'Inputs',
            'StickLeft': left,
            'StickRight': right,
            'A': a,
            'Up': up,
            'Down': down,
            'L': l
            })
        while not screen or not info:
            msg = self.listener_connection.recv()
            if msg['Type'] == 'Screen' and not screen:
                obs = np.asarray(msg['Data'])
                obs = obs.astype(np.uint8)
                screen = True
            if msg['Type'] == 'Info' and not info:
                info = {'Speed': msg['Speed'], 'Position': msg['Position']}
                info = True
        return (obs, info)
                

    def launch(self):
        os.popen(self.command)
        print('Dolphin Loaded')

    def reset(self, seed = None):
        super().reset(seed=seed)
        self.client_connection.send({'Type': 'Reset'})
        while True:
            msg = self.listener_connection.recv()
            if msg['Type'] == 'Screen':
                img = np.asarray(msg['Data'])
                img = img.astype(np.uint8)
                return img

def main():
    test = GameEnv()
    test.initialize()
    while True:
        test.step(2)

if __name__ == '__main__':
    main()
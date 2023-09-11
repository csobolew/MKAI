import os
from multiprocessing.connection import Listener, Client
import time
import subprocess
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
        self.reset_race()

    def launch(self):
        dolphin_path = "..\\dolphin\\Dolphin.exe"
        command = 'cmd /c ' + dolphin_path + " --script C:\\Users\\Carson\\MKAI\\Scripts\\dolphinscript.py \\b --exec C:\\Users\\Carson\\MKAI\\MKWii.iso"
        os.popen(command)
        print('Dolphin Loaded')

    def reset_race(self):
        self.client_connection.send({'Type': 'Reset'})
    
    def run(self):
        while True:
            self.client_connection.send(
            {
            'Type': 'Inputs',
            'StickLeft': True,
            'StickRight': True,
            'A': True,
            'Up': True,
            'Down': False,
            'L': True
            }
            )
            received = self.listener_connection.recv()
            if received['Type'] == 'Info':
                self.speed = received['Speed']
                self.position = received['Position']
            if received['Type'] == 'Screen':
                print('Screenshot received!')
                imgs = np.asarray(received['Data'])
                imgs = imgs.astype(np.uint8)
                plt.imshow(imgs,cmap='gray')
                plt.waitforbuttonpress()

def main():
    test = GameEnv()
    test.initialize()
    test.run()

if __name__ == '__main__':
    main()
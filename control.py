import os
from multiprocessing.connection import Listener, Client
import time
import subprocess
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np

class Controller():
    def __init__(self):
        self.initialized = False
        self.listener_connection = None
        self.client_connection = None
        self.speed = 0.0
        self.position = 0.0
    
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
                imgs = Image.frombytes('RGBA', (received['Width'], received['Height']), received['Data'], 'raw')
                plt.imshow(imgs)
                plt.waitforbuttonpress()

def main():
    test = Controller()
    test.initialize()
    test.run()

if __name__ == '__main__':
    main()
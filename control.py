import os
from multiprocessing.connection import Listener, Client
import time
import subprocess

class Controller():
    def __init__(self):
        self.initialized = False
        self.listener_connection = None
        self.client_connection = None
    
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

    def launch(self):
        dolphin_path = "..\\dolphin-scripting-preview2-x64\\Dolphin.exe"
        command = 'cmd /c ' + dolphin_path + " --script C:\\Users\\Carson\\MKAI\\Scripts\\dolphinscript.py \\b --exec C:\\Users\\Carson\\MKAI\\MKWii.iso"
        os.popen(command)
        print('Dolphin Loaded')

    
    def run(self):
        while True:
            self.client_connection.send({
            'StickLeft': True,
            'StickRight': False,
            'A': True,
            'Up': True,
            'Down': False,
            'L': False
        })

def main():
    test = Controller()
    test.initialize()
    test.run()

if __name__ == '__main__':
    main()
import os
from multiprocessing.connection import Listener

class Controller():
    def __init__(self):
        self.initialized = False
        self.listener_connection = None
        self.client_connection = None
    
    def initialize(self):
        print('Starting Emulator')
        self.launch()

    def launch(self):
        dolphin_path = "..\\dolphin-scripting-preview2-x64\\Dolphin.exe"
        command = dolphin_path + " --script C:\\Users\\Carson\\MKAI\\Scripts\\testscript.py --exec C:\\Users\\Carson\\MKAI\\MKWii.iso"
        os.popen(command)
        print('Dolphin Loaded')
        dolphinListener = ('localhost', 20000)
        listener = Listener(dolphinListener, authkey=b'supersecure')
        print('Waiting...')
        self.listener_connection = listener.accept()
        msg = self.listener_connection.recv()
        print('Message received:', str(msg))

def main():
    test = Controller()
    test.initialize()

if __name__ == '__main__':
    main()
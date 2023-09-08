from dolphin import event, memory, controller
from multiprocessing.connection import Client, Listener
import time

with open('log.txt', 'w') as file:
    file.write("Created new file!\n")
with open('log.txt', 'a') as file:
    file.write('Successfully loaded!\n')

class Dolphin():
    def __init__(self):
        with open('log.txt', 'a') as file:
            file.write('New!\n')
        self.input_map = {
            'StickLeft': False,
            'StickRight': False,
            'A': False,
            'Up': False,
            'Down': False,
            'L': False
        }
        self.speed = 0
        self.position = 0
        self.client_connection = Client(('localhost', 20000), authkey=b'supersecure')
        self.client_connection.send("Script Started!")
        self.listener = Listener(('localhost', 22000), authkey=b'password')
        self.listener_connection = self.listener.accept()
        print('Waiting for mesg')
        msg = self.listener_connection.recv()
        with open('log.txt', 'a') as file:
            file.write('Received message: ' + str(msg))            

main = Dolphin()

while True:
    await event.frameadvance()
    msg = main.listener_connection.recv()
    print(msg)
    speed = memory.read_f32(0x80FCE540)
    position = memory.read_f32(0x80E478B0)
    # print('Speed: ' + str(speed))
    # print('Track Position: ' + str(position))
    stickX = 128
    if msg['StickLeft'] and not msg['StickRight']:
        stickX = 0
    elif msg['StickRight'] and not msg['StickLeft']:
        stickX= 256
    controller.set_gc_buttons(0, {'Left': False, 'Right': False, 'Down': msg['Down'], 'Up': msg['Up'], 'Z': False, 'R': False, 'L': msg['L'], 'A': msg['A'], 'B': False, 'X': False, 'Y': False, 'Start': False, 'StickX': stickX, 'StickY': 128, 'CStickX': 128, 'CStickY': 128, 'TriggerLeft': 0, 'TriggerRight': 0, 'AnalogA': 0, 'AnalogB': 0, 'Connected': True})
    # print('Inputs: ' + str(controller.get_gc_buttons(0)))


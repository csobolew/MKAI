from dolphin import event, memory, controller, savestate
from multiprocessing.connection import Client, Listener
import sys
#sys.path.append('C:\\Users\\Carson\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\site-packages')
#import numpy

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
        print('duh')
        self.client_connection = Client(('localhost', 20000), authkey=b'supersecure')
        self.client_connection.send("Script Started!")
        self.listener = Listener(('localhost', 22000), authkey=b'password')
        self.listener_connection = self.listener.accept()
        print('Waiting for mesg')
        msg = self.listener_connection.recv()
        with open('log.txt', 'a') as file:
            file.write('Received message: ' + str(msg))     

print ('here')
main = Dolphin()
print('test')
# for i in range(4):
#     await event.frameadvance()
while True:
    (width, height, data) = await event.framedrawn()
    for i in range(2):
        await event.frameadvance()
    #img = PIL.Image.frombytes('RGBA', (width, height), data, 'raw')
    #img = img.convert("L")
    #enhancer = PIL.ImageEnhance.Sharpness(img)
    #img = enhancer.enhance(4)
    #img = img.resize((140,75))
    #enhancer = PIL.ImageEnhance.Sharpness(img)
    #img = enhancer.enhance(4)
    #img = np.asarray(img)
    #img = img.astype(np.uint8)
    msg = main.listener_connection.recv()
    if msg['Type'] == 'Inputs':
        stickX = 128
        if msg['StickLeft'] and not msg['StickRight']:
            stickX = 0
        elif msg['StickRight'] and not msg['StickLeft']:
            stickX= 255
        controller.set_gc_buttons(0, {'Left': False, 'Right': False, 'Down': msg['Down'], 'Up': msg['Up'], 'Z': False, 'R': False, 'L': msg['L'], 'A': msg['A'], 'B': False, 'X': False, 'Y': False, 'Start': False, 'StickX': stickX, 'StickY': 128, 'CStickX': 128, 'CStickY': 128, 'TriggerLeft': 0, 'TriggerRight': 0, 'AnalogA': 0, 'AnalogB': 0, 'Connected': True})
    elif msg['Type'] == 'Reset':
        controller.set_gc_buttons(0, {'Left': False, 'Right': False, 'Down': False, 'Up': False, 'Z': False, 'R': False, 'L': False, 'A': False, 'B': False, 'X': False, 'Y': False, 'Start': False, 'StickX': 128, 'StickY': 128, 'CStickX': 128, 'CStickY': 128, 'TriggerLeft': 0, 'TriggerRight': 0, 'AnalogA': 0, 'AnalogB': 0, 'Connected': True})
        savestate.load_from_slot(1)
    speed = memory.read_f32(0x80FCE500)
    position = memory.read_f32(0x80E47870)
    main.client_connection.send({'Type': 'Info', 'Speed': speed, 'Position': position})
    main.client_connection.send({'Type': 'Screen', 'Data': data, 'Width': width, 'Height': height})
    # print('Speed: ' + str(speed))
    # print('Track Position: ' + str(position))

    # print('Inputs: ' + str(controller.get_gc_buttons(0)))


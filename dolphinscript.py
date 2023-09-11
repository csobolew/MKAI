from dolphin import event, memory, controller, savestate
from multiprocessing.connection import Client, Listener
import sys
sys.path.append('C:\\Users\\Carson\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\site-packages')
from PIL import Image, ImageEnhance

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
        self.framecount = 0
        self.prev_position = 0
        self.recent_speeds = []
        self.client_connection = Client(('localhost', 20000), authkey=b'supersecure')
        self.client_connection.send("Script Started!")
        self.listener = Listener(('localhost', 22000), authkey=b'password')
        self.listener_connection = self.listener.accept()
        print('Waiting for response...')
        msg = self.listener_connection.recv()
        with open('log.txt', 'a') as file:
            file.write('Received message: ' + str(msg))    
        print('Received response!')
    
    def update_env_reward(self):
        self.framecount += 1
        self.recent_speeds.append(self.speed)
        if len(self.recent_speeds) >= 5:
            self.recent_speeds.pop(0)
        self.speed = memory.read_f32(0x80FCE500)
        print('speed: ' + str(self.speed))
        self.prev_position =self.position
        self.position = memory.read_f32(0x80E47870)
        print('pos: ' + str(self.position))

        reward = 0
        terminated = False
        truncated = False

        return (reward, terminated, truncated)

main = Dolphin()
# for i in range(4):
#     await event.frameadvance()
while True:
    (width, height, data) = await event.framedrawn()
    await event.frameadvance()
    (reward, terminated, truncated) = main.update_env_reward()
    img = Image.frombytes('RGBA', (width, height), data, 'raw')
    img = img.convert("L")
    img = img.resize((168,90))
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(5)
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
    main.client_connection.send({'Type': 'Info', 'Speed': main.speed, 'Position': main.position, 'Frames': main.framecount})
    main.client_connection.send({'Type': 'Screen', 'Data': img, 'Width': 168, 'Height': 90})
    # print('Speed: ' + str(speed))
    # print('Track Position: ' + str(position))

    # print('Inputs: ' + str(controller.get_gc_buttons(0)))


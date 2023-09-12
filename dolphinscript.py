from dolphin import event, memory, controller, savestate, gui
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
        with open('seed.txt', 'r') as file:
            self.seed = int(file.read(1))
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
        self.recent_positions = []
        self.recent_speeds = []
        self.next_check = 1.05
        self.total_reward = 0
        done = False
        try:
            self.client_connection = Client(('localhost', 20000 + self.seed - 1), authkey=b'supersecure')
            done = True
            self.seed = self.seed - 1
        except:
            pass
        if not done:
            try:
                self.client_connection = Client(('localhost', 20000 + self.seed - 2), authkey=b'supersecure')
                done = True
                self. seed = self.seed - 2
            except:
                pass
        if not done:
            try:
                self.client_connection = Client(('localhost', 20000 + self.seed - 3), authkey=b'supersecure')
                done = True
                self.seed = self.seed - 3
            except:
                pass
        if not done:
            try:
                self.client_connection = Client(('localhost', 20000 + self.seed - 4), authkey=b'supersecure')
                done = True
                self.seed = self.seed - 4
            except:
                pass
        self.client_connection.send("Script Started!")
        self.listener = Listener(('localhost', 22000 + self.seed), authkey=b'password')
        self.listener_connection = self.listener.accept()
        print('Waiting for response...')
        msg = self.listener_connection.recv()
        with open('log.txt', 'a') as file:
            file.write('Received message: ' + str(msg))    
        print('Received response!')
    
    def update_env_reward(self):
        self.framecount += 1
        self.recent_speeds.append(self.speed)
        if len(self.recent_speeds) >= 180:
            self.recent_speeds.pop(0)
        self.speed = memory.read_f32(0x80FC6B6C)
        self.recent_positions.append(self.position)
        if len(self.recent_positions) >= 180:
            self.recent_positions.pop(0)
        self.position = memory.read_f32(0x80E418AC)

        reward = 0
        terminated = False
        truncated = False

        if self.position > self.next_check:
            self.next_check += 0.04
            reward += 0.5 - min(0.25, self.framecount * 0.0025)
            self.framecount = 0
        # if self.position > self.recent_positions[-1]:
        #     reward += 0.0025 * (self.position - self.recent_positions[-1])

        if self.speed > 100:
            reward += 0.008
        elif self.speed > 95:
            reward += 0.0055
        elif self.speed > 90:
            reward += 0.0035
        elif self.speed > 85:
            reward += 0.002
        elif self.speed > 80:
            reward += 0.001
        elif self.speed > 75:
            reward += 0.0005
        elif self.speed > 70:
            reward += 0.0001
        elif self.speed < 35:
            reward -= 0.01
        elif self.speed < 45:
            reward -= 0.0035
        elif self.speed < 55:
            reward -= 0.001
        elif self.speed < 65:
            reward -= 0.0001

        # if self.speed > 100:
        #     reward += 0.0065
        # elif self.speed > 95:
        #     reward += 0.004
        # elif self.speed > 92:
        #     reward += 0.003
        # elif self.speed > 90:
        #     reward += 0.0025
        # elif self.speed > 87:
        #     reward += 0.002
        # elif self.speed > 85:
        #     reward += 0.001
        # elif self.speed > 82:
        #     reward += 0.00075
        # elif self.speed > 78:
        #     reward += 0.0005
        # elif self.speed > 70:
        #     reward += 0.0001
        # elif self.speed < 65:
        #     reward -= 0.0001
        # elif self.speed < 60:
        #     reward -= 0.001
        # elif self.speed < 50:
        #     reward -= 0.005
        # elif self.speed < 35:
        #     reward -= 0.01

        if self.position >= 4.0125:
            reward += 9.75
            terminated = True

        elif (len(self.recent_speeds) == 179 and max(self.recent_speeds) < 45) or (len(self.recent_positions) == 179 and (self.recent_positions[-1]
                                                                                                                         - self.recent_positions[0]) < 0.0025):
            reward = -0.1
            truncated = True
        self.total_reward += reward
        print(self.total_reward)
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
        if msg['StickLeft']:
            stickX = 0
        elif msg['StickRight']:
            stickX= 255
        elif msg['SoftLeft']:
            stickX = 64
        elif msg['SoftRight']:
            stickX = 192
        controller.set_gc_buttons(0, {'Left': False, 'Right': False, 'Down': msg['Down'], 'Up': msg['Up'], 'Z': False, 'R': False, 'L': msg['L'], 'A': True, 'B': False, 'X': False, 'Y': False, 'Start': False, 'StickX': stickX, 'StickY': 128, 'CStickX': 128, 'CStickY': 128, 'TriggerLeft': 0, 'TriggerRight': 0, 'AnalogA': 0, 'AnalogB': 0, 'Connected': True})
    elif msg['Type'] == 'Reset':
        controller.set_gc_buttons(0, {'Left': False, 'Right': False, 'Down': False, 'Up': False, 'Z': False, 'R': False, 'L': False, 'A': False, 'B': False, 'X': False, 'Y': False, 'Start': False, 'StickX': 128, 'StickY': 128, 'CStickX': 128, 'CStickY': 128, 'TriggerLeft': 0, 'TriggerRight': 0, 'AnalogA': 0, 'AnalogB': 0, 'Connected': True})
        main.recent_speeds = []
        main.recent_positions = []
        main.speed = 0
        main.position = 0
        main.framecount = 0
        main.total_reward = 0
        main.next_check = 1.05
        savestate.load_from_slot(1)
    main.client_connection.send({'Type': 'Info', 'Speed': main.speed, 'Position': main.position, 'Reward': reward, 'Frames': main.framecount, 'Terminated': terminated, 'Truncated': truncated})
    main.client_connection.send({'Type': 'Screen', 'Data': img, 'Width': 168, 'Height': 90})
    # print('Speed: ' + str(speed))
    # print('Track Position: ' + str(position))

    # print('Inputs: ' + str(controller.get_gc_buttons(0)))


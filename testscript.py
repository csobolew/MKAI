from dolphin import event, memory, controller
import os

with open('log.txt', 'w') as file:
    file.write("Created new file!\n")
with open('log.txt', 'a') as file:
    file.write('Successfully loaded!\n')
with open('dolphin_pid.txt', 'w') as file:
    file.write(str(os.getpid()))


class Dolphin():
    def __init__(self):
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



while True:
    await event.frameadvance()
    speed = memory.read_f32(0x80FCE540)
    position = memory.read_f32(0x80E478B0)
    # print('Speed: ' + str(speed))
    # print('Track Position: ' + str(position))
    controller.set_gc_buttons(0, {'Left': False, 'Right': False, 'Down': False, 'Up': False, 'Z': False, 'R': False, 'L': False, 'A': True, 'B': False, 'X': False, 'Y': False, 'Start': False, 'StickX': 0, 'StickY': 128, 'CStickX': 128, 'CStickY': 128, 'TriggerLeft': 0, 'TriggerRight': 0, 'AnalogA': 0, 'AnalogB': 0, 'Connected': True})
    # print('Inputs: ' + str(controller.get_gc_buttons(0)))

import sys
import time
import serial
from os.path import exists
from psychopy import visual, core, event, monitors
from mr_helpers import setup_path, get_monitors
from pygaze import eyetracker, libscreen
import pygaze

mon_name = 'projector'
mon_specs = get_monitors(mon_name)
exp_mon = monitors.Monitor(name=mon_name, width=mon_specs["size_cm"][0], distance=mon_specs["dist"])
exp_mon.setSizePix(mon_specs["size_px"])
exp_mon.save()

# debugging variables
mon_size = [1024, 768]
full_screen = False
fake_ans = True

# Window
exp_win = visual.Window(
    monitor=exp_mon,
    fullscr=full_screen,
    units='deg',
    size=mon_size,
    allowGUI=False,
    screen=0,
    autoLog=False,
    name='behav_win'
)

msg_stim = visual.TextStim(win=exp_win, wrapWidth=30, height=.8, alignText='left', autoLog=False)

waiting = visual.TextStim(exp_win, pos=[0, 0], text="Waiting for scanner...",
                          color='black', name="Waiting")
waiting_fake = visual.TextStim(exp_win, pos=[0, 0], text="Waiting for (fake) scanner...",
                               color='black', name="Waiting_fake")

serial_path = 'COM3'
# serial_path = '/dev/cu.USA19H62P1.1'
# serial_path = '/dev/cu.USA19H142P1.1'
# serial_path = '/dev/tty.USA19H142P1.1'

if not exists(serial_path):
    waiting_fake.draw()
    exp_win.flip()
    serial_exists = False
    b_serial = "No serial device detected, using keyboard"
    event.waitKeys(keyList=['5'])
    first_trigger = "Got sync from keyboard. Resetting clocks"
else:
    waiting.draw()
    exp_win.flip()
    serial_exists = True
    b_serial = "Serial device detected"
    ser = serial.Serial(serial_path, 19200, timeout=.0001)
    ser.flushInput()
    scanner_wait = True

    while scanner_wait:
        ser_out = ser.read()
        if b'5' in ser_out:
            scanner_wait = False
            first_trigger = "Got sync from scanner!"

# check keys
print(b_serial)
print(first_trigger)
pressed = event.getKeys()
print(pressed)

# check eye tracker
disp = libscreen.Display(moniotr=exp_mon)
win = pygaze.expdisplay
tracker = eyetracker.EyeTracker(disp)
tracker.calibrate()

exp_win.close()
core.quit()

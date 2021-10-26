#!usr/bin/env python
"""
Created at 10/23/21
@author: Sharif Saleki

Pre-scan behavioral experiment for determining illusion size of each participant
"""
from psychopy import visual, monitors, event, core, logging, gui
from dd_helpers import setup_path, get_monitors

import numpy as np
from pathlib import Path
import pandas as pd
from itertools import product

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! SETUP ---------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Get the parameters from gui
# setup
input_gui = gui.Dlg(title=">_<")
input_gui.addText('Participant Information')
input_gui.addField('Initials: ')
input_gui.addField('Age: ', choices=list(range(18, 81)))
input_gui.addField('Vision: ', choices=["Normal", "Corrected", "Other"])
input_gui.addField('Participant Number: ', choices=list(range(1, 25)))
input_gui.addField('Debug: ', choices=[True, False])

# show
part_info = input_gui.show()
if not part_info.OK:
    core.quit()

# check debug
debug = part_info.data[4]
if not debug:
    sub_init = part_info.data[1]
    sub_id = part_info.data[3]
else:
    sub_init = 'gg'
    sub_id = 0

# Directories and files
EXP = "DoubleDriftODC"
PART = "psychophysics"
TASK = "IllusionSize"
ROOTDIR = Path(__file__).resolve().parent.parent  # find the current file
PARTDIR = setup_path(sub_id, ROOTDIR, PART)
run_file = PARTDIR / f"sub-{sub_id:02d}_task-{TASK}_part-{PART}_exp-{EXP}"

# file names
exp_file = str(run_file)
frames_file = str(run_file) + "_frame-intervals.log"
log_file = str(run_file) + "_runtime-log.log"

# Monitor
mon_name = 'Asus'
mon_specs = get_monitors(mon_name)
exp_mon = monitors.Monitor(name=mon_name, width=mon_specs["size_cm"][0], distance=mon_specs["dist"])
exp_mon.setSizePix(mon_specs["size_px"])
exp_mon.save()

# debugging variables
if int(debug):
    mon_size = [1024, 768]
    full_screen = False
    fake_ans = True
else:
    mon_size = mon_specs["size_px"]
    full_screen = True
    fake_ans = False

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

# Logging
log_clock = core.Clock()
logging.setDefaultClock(log_clock)
log_data = logging.LogFile(log_file, filemode='w', level=logging.INFO)
logging.console.setLevel(logging.ERROR)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! STIMULUS --------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# gabor
gabor = visual.GratingStim(
    win=exp_win,
    mask='gauss',
    contrast=1,
    interpolate=False,
    autoLog=False
)

# fixation dot
fix = visual.Circle(
    win=exp_win,
    radius=0.3,
    fillColor=-1,
    lineColor=-1,
    autoLog=False
)

# Response line
resp_line = visual.Line(
    win=exp_win,
    start=(0, 0),
    end=(0, 1),
    lineWidth=7,
    lineColor=-1,
    opacity=1,
    autoLog=False
)

# Text messages
msg_stim = visual.TextStim(win=exp_win, wrapWidth=30, height=.8, alignText='left', autoLog=False)
rep_stim = visual.TextStim(win=exp_win, wrapWidth=30, height=.8, pos=[0, -5], autoLog=False)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! PROCEDURE -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Instructions
resp_stages = ['Length', 'Orientation']  # reporting stages
resp_order = np.random.rand() < .5
resp_stages = [resp_stages[resp_order],
               resp_stages[1 - resp_order]]  # so order 0 is [length, orientation] and order 1 is [orientation, length]

instr_msg = \
    "On each trial, maintain fixation at the center of the screen on the black circle.\n\n" \
    "Pay attention to the path that the Gabor moves on.\n\n" \
    "When the Gabor disappears, a line appears on the fixation circle.\n\n" \
    f"First, use the mouse wheel to change the {resp_stages[0]} of the line to match the {resp_stages[0]} of the " \
    f"Gabor's path.\n\n" \
    f"Press the Spacebar when you are done adjusting the {resp_stages[0]}.\n\n" \
    f"Then, use the mouse wheel to change the {resp_stages[1]} of the line to match the {resp_stages[1]} of the " \
    f"Gabor's path.\n\n" \
    "Again, press the Spacebar to submit your report and move on to the next trial.\n\n" \
    "Press the spacebar to start the experiment..."

end_msg = "Thank you for your participation :)"

# Conditions
speeds = [  # internal, external
    [4, 6],
    [4, 5],  # based on Sirui's experiment
    [4, 3]
]
quadrants = ["L", "R"]
n_trials_per_cond = 15

# Data handler
# columns of experiment dataframe
cols = [
    "RESP_ORDER",
    "V_INTERNAL",
    "V_EXTERNAL",
    "QUADRANT",
    "RESP_ORI",
    "RESP_LENGTH",
    "TRIAL",
    "TASK",
    "EXPERIMENT",
    "SUBJECT_ID",
    "SUB_INITIALS"
]

# blocks and trials
exp_blocks = None  # actual dataframe

# in the speed block, speeds are varied. In the duration block, durations are varied.
conds = list(product(speeds, quadrants))
n_trials = n_trials_per_cond * len(conds)  # total number of trials in the blocks

# loop through conditions, make every permutation, and save it to a numpy array
rows = None
for cond in list(conds):
    row = np.array([
        int(resp_order),
        cond[0][0],  # internal speed
        cond[0][1],  # external speed
        cond[1],  # quadrant
        np.NaN,  # reported orientation
        np.NaN,  # reported length
        np.NaN,  # trial
        TASK,  # task
        EXP,  # experiment
        sub_id,  # subject ID
        sub_init,  # subject's initials
    ])
    if rows is None:
        rows = row
    else:
        rows = np.vstack((rows, row))

# repeat conditions for however many trials
this_block = np.repeat(rows, n_trials_per_cond, axis=0)

# shuffle them
np.random.shuffle(this_block)  # this preserves the order within row and just shuffles the rows

# sanity check
# print(f"Shape of block {b}: {this_block.shape}")
assert this_block.shape == (n_trials, len(cols))

# add trial labels
this_block[:, 6] = np.arange(1, n_trials + 1)  # trial is the 7(-1)th col. set it to a list of ordered numbers

if exp_blocks is None:
    exp_blocks = this_block
else:
    exp_blocks = np.vstack((exp_blocks, this_block))

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! RUN ------------------------------------ #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Initialize parameters
# gabor
gab_size = 1.2  # in dva
gab_shift = 7  # degrees shift in x from the center of the screen
gab_sf = .5 / gab_size  # cycles per degree spatial frequency
gabor.size = gab_size
gabor.sf = gab_sf

# runtime params
exp_win.refreshThreshold = (1 / mon_specs["refresh_rate"]) + 0.003
path_dur = 1000  # milli-second
n_frames = np.floor(path_dur * int(mon_specs["refresh_rate"]) / 1000)

# clocks
exp_clock = core.Clock()

# show instructions and wait for keypress
msg_stim.text = instr_msg
msg_stim.draw()
exp_win.flip()
event.waitKeys(keyList=['space'])
logging.exp("===========================")
logging.exp("Experiment started")
logging.exp("===========================")
exp_win.flip()
exp_clock.reset()

# start trials
for trial in range(n_trials):

    # log it
    logging.exp(f"---------------------------")
    logging.exp(f"Trial {trial} started.")

    # run parameters
    # from Hz to cycles/frame
    v_tex = [exp_blocks[trial, 1] / mon_specs["refresh_rate"], 0]
    v_env = [0, exp_blocks[trial, 2] / mon_specs["refresh_rate"]]

    # start recording frames
    exp_win.recordFrameIntervals = True

    # show fixation
    fix.autoDraw = True

    # log it
    logging.exp("Moving the stimulus.")

    # show the drift
    for rep in range(2):

        # control drawing every frame
        for frame in range(n_frames):

            # drift right / move up on odd repetitions
            if not rep:
                gabor.phase += v_tex
                gabor.pos += v_env

            # drift left / move down on even repetitions
            else:
                gabor.phase -= v_tex
                gabor.pos -= v_env

            gabor.draw()
            exp_win.flip()

    # Get the response
    # clean buffer
    event.clearEvents()

    # reporting device
    ans_mouse = event.Mouse(visible=False, win=exp_win)

    # initialize response line length and ori every trial
    resp_line.size = .1 if resp_stages[0] == 'Length' else 1  # starting line size with 1 dva
    resp_line.ori = 90

    # for debugging
    if not fake_ans:

        # text message
        rep_stim.autoDraw = True

        # reporting stages
        for stage in resp_stages:

            # get response
            resp = True

            # reporting loop
            while resp:

                # mouse wheel for controlling the line
                wheel_dX, wheel_dY = ans_mouse.getWheelRel()

                # change the orientation
                if stage == 'Orientation':

                    # text message
                    rep_stim.text = "Match orientation"
                    rep_stim.draw()

                    if 0 <= resp_line.ori < 180:  # don't allow weird responses
                        resp_line.setOri(wheel_dY * 2, '-')
                    else:
                        resp_line.ori = 0

                # change the length
                else:

                    # text message
                    rep_stim.text = "Match length"
                    rep_stim.draw()

                    if resp_line.size > 0:  # don't allow below 0 size!
                        resp_line.size += wheel_dY * .05
                    else:
                        resp_line.size = .1

                resp_line.draw()
                exp_win.flip()

                # get the keypress for end of reporting
                keys = event.getKeys()

                for key in keys:

                    # space is the end of reporting
                    if key == 'space':

                        # save the orientation
                        if stage == 'Orientation':
                            exp_blocks[trial, 4] = resp_line.ori

                        # save the length
                        else:
                            # sometimes .size returns an np array!
                            try:
                                # the default response line size=1 means 2dva
                                exp_blocks[trial, 5] = np.round(resp_line.size, 2)
                            except:
                                exp_blocks[trial, 5] = np.round(resp_line.size[0], 2)

                        # log and end reporting
                        logging.exp(f"Response recorded: {exp_blocks[trial, 4]}")
                        resp = False  # end reporting
                        rep_stim.autoDraw = False

                    # escape is quitting
                    elif key == 'escape':  # quit button
                        logging.error("Aborted experiment.")
                        exp_win.close()
                        core.quit()

    # if in debugging mode
    else:
        # just generate fake responses
        exp_win.flip()
        core.wait(4)  # approximate response time
        exp_blocks[trial, 4] = .33  # random orientation
        exp_blocks[trial, 5] = .69  # random size

    # Turn fixation off
    fix.autoDraw = False

    # clear buffer
    event.clearEvents()
    logging.exp(f"Trial ended.")

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! WRAP UP -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# time it
t_end = np.round(exp_clock.getTime() / 60, 2)
logging.exp(f"Experiment finished. Duration: {t_end} minutes.")
print(f"Experiment finished. Duration: {t_end} minutes.")

# show than you message
msg_stim.text = end_msg
msg_stim.draw()
exp_win.flip()
core.wait(2)
exp_win.logOnFlip("Experiment ended.", level=logging.EXP)
exp_win.flip()

# save in csv
exp_df = pd.DataFrame(exp_blocks, columns=cols)  # turn it into a pandas dataframe
exp_df.to_csv(exp_file + '.csv', sep=',', index=False)

# save recorded frames
exp_win.saveFrameIntervals(fileName=frames_file)

exp_win.close()
core.quit()

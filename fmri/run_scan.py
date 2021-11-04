#!usr/bin/env python
"""
Created at 10/23/21
@author: Sharif Saleki

fMRI experiment for finding the location of attentional feedback in V1
"""
from psychopy import visual, monitors, event, core, logging, gui, data
from mr_helpers import setup_path, get_monitors

import numpy as np
from pathlib import Path
import pandas as pd
from itertools import product
from collections import defaultdict

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! SETUP ---------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Get the parameters from gui
# setup
input_gui = gui.Dlg(title=">_<")
input_gui.addField('Debug: ', True, color='red')

input_gui.addText('Participant Information', color='blue')
input_gui.addField('Participant Number: ', choices=list(range(1, 25)))
input_gui.addField('Initials: ')
input_gui.addField('DBIC ID: ')
input_gui.addField('Accession Number: ')
input_gui.addField('Session: ', choices=[1, 2])
input_gui.addField('Age: ', choices=list(range(18, 81)))
input_gui.addField('Vision: ', choices=["Normal", "Corrected", "Other"])

input_gui.addText("Experiment Parameters", color='blue')
input_gui.addField("Path orientation: ", 10)
input_gui.addField("Path length: ")
input_gui.addField("Initial Eye:", choices=["Left", "Right"])
input_gui.addFixedField("Date: ", data.getDateStr())

# show
part_info = input_gui.show()
if not input_gui.OK:
    core.quit()
else:
    print(part_info)
# check debug
debug = part_info[0]
if not debug:
    sub_id = int(part_info[1])
    sub_init = part_info[2]
else:
    sub_init = 'gg'
    sub_id = 0

init_eye = part_info[10]
date = part_info[11]

# Directories and files
EXP = "DoubleDriftODC"
PART = "fmri"
TASK = "contrast_change"
ROOTDIR = Path(__file__).resolve().parent.parent  # find the current file
PARTDIR = setup_path(sub_id, ROOTDIR, PART)
run_file = PARTDIR / f"sub-{sub_id:02d}_task-{TASK}_part-{PART}_exp-{EXP}"

# file names
exp_file = str(run_file)
frames_file = str(run_file) + "_frame-intervals.log"
log_file = str(run_file) + "_runtime-log.log"

# Monitor
mon_name = 'RaZer'
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

# Add a new logging level name called bids
# we will use this level to log information that will be saved
# in the _events.tsv file for this run
BIDS = 69
logging.addLevel(BIDS, 'BIDS')

# BIDS TEMPLATE
logging.root.log("onset\tduration\ttask_side\teye", level=BIDS)
template_bids = '{onset:.3f}\t{duration:.3f}\t{hemifield}\t{eye}'

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! STIMULUS --------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# gabor
horiz_offset = 7
left_gabor = visual.GratingStim(
    win=exp_win,
    mask='gauss',
    pos=[-horiz_offset, 0],
    contrast=1,
    interpolate=False,
    autoLog=False
)

right_gabor = visual.GratingStim(
    win=exp_win,
    mask='gauss',
    pos=[horiz_offset, 0],
    contrast=1,
    interpolate=False,
    autoLog=False
)

# checkerboards
sqr_sz = 3
n_sqrs = 8
stim_sides = ["left", "right"]
patterns = ["pat1", "pat2"]
oris = ["vert", "obl"]
checkers = defaultdict(list)

for lr in stim_sides:
    for pat in patterns:
        for ori in oris:
            for s in range(n_sqrs):
                checkers[f"{lr}_{pat}_{ori}"].append(
                    visual.Rect(
                        win=exp_win,
                        size=sqr_sz,
                        pos=[-horiz_offset if lr == "left" else horiz_offset, sqr_sz / 2 + s],
                        lineColor=0,
                        ori=0 if (ori == "vert") else int(part_info[8]),
                        fillColor=(1 if s % 2 else -1) if (pat == "pat1") else (-1 if s % 2 else 1),
                        autoLog=False
                    )
                )

# cue
cue = visual.ImageStim(
    win=exp_win,
    image='arrow.png',
    autoLog=False
)

# fixation dot
fix = visual.Circle(
    win=exp_win,
    radius=0.1,
    fillColor='black',
    size=.3,
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
instr_msg = \
    "On each trial, maintain fixation at the center of the screen on the inner circle.\n\n" \
    "A red arrow will appear at fixation that indicates which side of the screen you should pay attention to for all " \
    "the subsequent trials.\n\n" \
    "When the arrow disappears, maintain fixation and pay attention to the moving Gabor on the cued side and ignore " \
    "the other side of the screen.\n\n" \
    "If the gabor on the cued side becomes dimmer, press the response button!\n\n"\
    "Press the response button to start the experiment..."

end_msg = "Thank you for your participation :)"

# Conditions
hemifields = ["L", "R"]  # target left or right side of the fixation
# trial_types = ["dd", "ctrl_vert", "ctrl_oblq"]  # is it a double- or single-drift
trial_types = ["dd"]
eyes = ["L", "R"]  # left eye viewing or right eye: first 5 runs are one eye and the last 5 are the other
block_parts = ["wait", "fixation", "stim"]
n_blocks = 10  # each block has an initial 4s wait period followed by 11s of stimulus presentation and 15s fixation
n_runs = 12  # number of runs

# Data handler
# columns of experiment dataframe
cols = [
    "HEMIFIELD",
    "TRIAL_TYPE",
    "DIM",
    "DIM_TIME",
    "TRIAL",
    "EYE",
    "BLOCK",
    "RUN",
    "PATH_LEN",
    "PATH_ORI",
    "TASK",
    "EXPERIMENT",
    "SUB_ID",
    "SUB_INITIALS",
    "DBIC_ID",
    "ACCESSION_NUM"
]

# blocks and trials
exp_runs = None  # actual dataframe

# in the speed block, speeds are varied. In the duration block, durations are varied.
conds = list(product(trial_types, eyes, hemifields))
n_trials = n_runs * n_blocks * len(conds)  # total number of trials in the blocks

# loop through conditions, make every permutation, and save it to a numpy array
for run in range(n_runs):
    run_eye = ("L" if run < n_runs / 2 else "R") if init_eye == "L" else ("R" if run < n_runs / 2 else "L")
    rand_blocks = np.ones(n_blocks)
    rand_blocks[:n_blocks//2] = 0
    np.random.shuffle(rand_blocks)

    for block in range(n_blocks):
        block_side = np.random.choice(hemifields)

rows = None
for hemi, trial_type, eye in conds:
    row = np.array([
        hemi,  # cued hemifield
        trial_type,  # vertical control, oblique control, or dd
        np.NaN,  # does the target dim
        np.NaN,  # time of dimming
        np.NaN,  # trial
        eye,  # eye
        np.NaN,  # block
        np.NaN,  # run
        np.NaN,  # path length
        np.NaN,  # path orientation
        TASK,  # task
        EXP,  # experiment
        sub_id,  # subject ID
        sub_init,  # subject initials
        part_info[3],  # DBIC ID
        part_info[4]  # Accession Number
    ])
    if rows is None:
        rows = row
    else:
        rows = np.vstack((rows, row))

print(rows)

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

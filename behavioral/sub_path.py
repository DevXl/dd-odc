#!usr/bin/env python
"""
Created at 10/24/21
@author: Sharif Saleki

Description: Script to calculate the mean of the path length and orientation for a subject based on their report and
shows the parameters that lead to the largest illusion size. It also shows the dimensions of the checkerboard that
should be used as the input to the fmri script for the subject.
"""
from pathlib import Path
import pandas as pd
import sys

# Get subject number
if len(sys.argv) > 1:
    sub_id = f"{sys.argv[1]}:02d"

# Paths
ROOTDIR = Path(__file__).resolve().parent.parent
DATADIR = ROOTDIR / "data"
EXP = "DoubleDriftODC"
TASK = "behavioral"
data_file = DATADIR / f"sub-{sub_id}" / "behavioral" / f"sub-{sub_id}_task-{TASK}_exp-{EXP}.csv"

# Load the file
df = pd.read_csv(data_file)



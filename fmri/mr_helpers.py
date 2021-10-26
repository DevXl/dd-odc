#!usr/bin/env python
"""
Helper functions for double-drift experiments
"""


def setup_path(sub, root, exp_part):
    """
    Sets up paths and directories for experiment
    The structure loosely follows BIDS convention

    Parameters
    ----------
    sub : int
    root : Pathlib object
        points to the root directory of the experiment
    exp_part : str
    """
    # data directory
    data_dir = root / "data"
    if not data_dir.exists():
        print("Making the data directory...")
        data_dir.mkdir()

    # subject directory
    sub_id = f"{sub:02d}"
    sub_dir = data_dir / f"sub-{sub_id}"
    if not sub_dir.exists():
        print("Making the subject directory...")
        sub_dir.mkdir()

    # task directory
    task_dir = sub_dir / exp_part
    if not task_dir.exists():
        print("Making the task directory...")
        task_dir.mkdir()

    return task_dir


def get_monitors(mon_name):
    """
    Has all the monitors with their specs and returns the one with the specified name.

    Parameters
    ----------
    mon_name : str
        name of the requested monitor

    Returns
    -------
    dict
    """
    test_monitors = {
        "lab": {
            "size_cm": (54, 0),
            "size_px": (1024, 768),
            "dist": 100,
            "refresh_rate": 60
        },
        "RaZer": {
            "size_cm": (38, 20),
            "size_px": (2560, 1440),
            "dist": 60,
            "refresh_rate": 165
        },
        "projector": {
            "size_cm": (54, 30),
            "size_px": (1280, 960),
            "dist": 124,
            "refresh_rate": 60
        }
    }

    return test_monitors[mon_name]


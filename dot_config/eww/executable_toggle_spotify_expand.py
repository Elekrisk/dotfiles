#!/usr/bin/env python3

import os
import subprocess

lockfile = "/home/elekrisk/.config/eww/spotify.lock"
eww = "/home/elekrisk/src/eww/target/release/eww"

if os.path.exists(lockfile):
    subprocess.run([eww, "close", "spotifyExpand"])
    subprocess.run(["rm", lockfile], capture_output = True)
else:
    subprocess.run([eww, "open", "spotifyExpand"])
    subprocess.run(["touch", lockfile], capture_output = True)
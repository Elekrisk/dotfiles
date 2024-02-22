#!/usr/bin/env python3

import subprocess
import sys
import json

proc = subprocess.Popen(["pactl", "subscribe"], stdout=subprocess.PIPE)

def emit_volume():
        volume = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], capture_output=True)
        volume = str(volume.stdout.split()[4][:-1], 'utf-8').zfill(2)
        muted = subprocess.run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], capture_output=True)
        muted = muted.stdout == b"Mute: yes\n"
        data = { "volume": volume, "muted": muted }
        print(json.dumps(data))
        sys.stdout.flush()
    
emit_volume()


while True:
    line = proc.stdout.readline()
    if line.startswith(b"Event 'change' on sink"):
        emit_volume()

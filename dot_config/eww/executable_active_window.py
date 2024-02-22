#!/usr/bin/env python3

import socket
import sys
import os
import json
import subprocess

sig = os.environ["HYPRLAND_INSTANCE_SIGNATURE"]
path = f"/tmp/hypr/{sig}/.socket2.sock"

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

client.connect(path)

client = client.makefile()

while True:
    ev = client.readline().strip()
    [ev, payload] = ev.split('>>', 1)

    if ev == "activewindow":
        [window_class, window_title] = payload.split(',', 1)
        print(json.dumps({"class": window_class, "title": window_title}))
        sys.stdout.flush()

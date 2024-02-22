#!/usr/bin/env python3

import socket
import sys
import os
import json
import subprocess

from window_icon import get_icon

sig = os.environ["HYPRLAND_INSTANCE_SIGNATURE"]
path = f"/tmp/hypr/{sig}/.socket2.sock"

f = open("/home/elekrisk/log.txt", "w")

def log(msg):
    f.write(msg + "\n")
    f.flush()

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

client.connect(path)

client = client.makefile()

class WindowsState:
    def __init__(self):
        self.windows = {}
        self.active_window = ""
    def set_active_window(self, addr):
        self.active_window = addr
    def open_window(self, addr, workspace, windowclass, title):
        try:
            workspace = int(workspace)
        except ValueError:
            pass
        icon = get_icon(windowclass)
        if icon == None:
            icon = windowclass
        self.windows[addr] = {
            "address": addr,
            "workspace": workspace,
            "class": windowclass,
            "title": title,
            "icon": icon,
        }
    def close_window(self, addr):
        del self.windows[addr]
    def move_window(self, addr, workspace):
        try:
            workspace = int(workspace)
        except ValueError:
            pass
        self.windows[addr]["workspace"] = workspace
    def set_window_title(self, addr):
        pass
    def emit(self):
        print(json.dumps({ "active_window": self.active_window, "windows": sorted(self.windows.values(), key=lambda w: w["workspace"]) }))
        sys.stdout.flush()


state = WindowsState()

info = json.loads(subprocess.run(["hyprctl", "-j", "clients"], capture_output=True).stdout)

for window in info:
    if window["workspace"]["id"] != -1:
        state.open_window(window["address"], window["workspace"]["name"], window["class"], window["title"])

active = json.loads(subprocess.run(["hyprctl", "-j", "activewindow"], capture_output=True).stdout)
if "address" in active:
    state.set_active_window(active["address"])

state.emit()

while True:
    msg = client.readline()
    msg = msg.strip()
    # print(msg);
    [event, payload] = msg.split(">>", 1)

    if event == "openwindow":
        [addr, workspace, windowclass, title] = payload.split(',', 3)
        if workspace != "":
            state.open_window("0x"+ addr, workspace, windowclass, title)
    elif event == "closewindow":
        state.close_window("0x" + payload)
    elif event == "movewindow":
        [addr, workspace] = payload.split(',', 1)
        state.move_window("0x" + addr, workspace)
    elif event == "windowtitle":
        state.set_window_title("0x" + payload)
    elif event == "activewindowv2":
        state.set_active_window("0x" + payload)
    else:
        continue
    
    state.emit()
    

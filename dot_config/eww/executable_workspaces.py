#!/usr/bin/env python3

import socket
import sys
import os
import json
import subprocess

sig = os.environ["HYPRLAND_INSTANCE_SIGNATURE"]
path = f"/tmp/hypr/{sig}/.socket2.sock"

f = open("/home/elekrisk/log.txt", "w")

def log(msg):
    f.write(msg + "\n")
    f.flush()

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

client.connect(path)

client = client.makefile()

class WorkspacesState:
    def __init__(self):
        self.workspaces = {}
        self.active_workspace = None
        
    def create_workspace(self, workspace_id):
        self.workspaces[workspace_id] = { "id": workspace_id }
    
    def delete_workspace(self, workspace_id):
        del self.workspaces[workspace_id]

    def set_active_workspace(self, workspace_id):
        self.active_workspace = workspace_id
        if workspace_id not in self.workspaces:
            self.create_workspace(workspace_id)
        
    def emit(self):
        msg = json.dumps({ "active": self.active_workspace, "workspaces": sorted(self.workspaces.values(), key=lambda x: x["id"]) })
        log(msg)
        print(msg)
        sys.stdout.flush()

state = WorkspacesState()

info = json.loads(subprocess.run(["hyprctl", "-j", "workspaces"], capture_output=True).stdout)

for workspace in info:
    state.create_workspace(workspace["id"])

active = json.loads(subprocess.run(["hyprctl", "-j", "activeworkspace"], capture_output=True).stdout)["id"]

state.set_active_workspace(active)

state.emit()

while True:
    msg = client.readline()
    msg = msg.strip()
    log(msg);
    parts = msg.split(">>")
    event = parts[0]
    payload = parts[1]

    if event == "workspace":
        state.set_active_workspace(int(payload))
    elif event == "destroyworkspace":
        state.delete_workspace(int(payload))
    else:
        continue
    
    state.emit()
    

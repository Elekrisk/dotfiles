#!/usr/bin/env python3

import subprocess
import json
import sys
import os
import time
from threading import Thread
import urllib.request

lockfile = "/home/elekrisk/.config/eww/spotify.lock"

spotify_state = {
    "running": False,
    "status": "Stopped",
    "position": 0,
    "mpris:length": 1
}

def download_album(url):
    urllib.request.urlretrieve(url, "/home/elekrisk/.config/eww/album.png")
    if os.path.exists(lockfile):
        subprocess.run(["/home/elekrisk/src/eww/target/release/eww", "open", "spotifyExpand"], capture_output=True)


def repopulate_state():
    meta = subprocess.run(['playerctl', '-p', 'spotify', 'metadata'], capture_output=True).stdout
    spotify_state["running"]: True
    for line in meta.splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3:
            [player, attribute, value] = parts
        elif len(parts) == 2:
            [player, attribute] = parts
            value = ""

        if player != "spotify":
            continue

        set_attribute(attribute, value)


def secs_to_micros(val):
    return int(float(val) * 1000000)

def set_attribute(attr, value):
    global spotify_state
    spotify_state[attr] = value
    print(json.dumps(spotify_state))
    sys.stdout.flush()
    if attr == "mpris:artUrl" and value != "":
        download_album(value)

def metadata():
    global spotify_state

    # print("Starting metadata")

    proc = subprocess.Popen(['playerctl', '-p', 'spotify', '-F', 'metadata'], stdout=subprocess.PIPE)
    while True:
        line = str(proc.stdout.readline().strip(), 'utf-8')
        if spotify_state["running"] != (line != ""):
            # if line != "":
            #     time.sleep(3)
            #     repopulate_state()
            set_attribute("running", line != "")
        parts = line.split(None, 2)
        if len(parts) == 3:
            [player, attribute, value] = parts
        elif len(parts) == 2:
            [player, attribute] = parts
            value = ""

        if player != "spotify":
            continue

        set_attribute(attribute, value)

def status():
    global spotify_state
    
    # print("Starting status")
    
    proc = subprocess.Popen(['playerctl', '-p', 'spotify', '-F', 'status'], stdout=subprocess.PIPE)
    while True:
        line = str(proc.stdout.readline().strip(), 'utf-8')
        # print(line)
        
        if line != "":
            set_attribute("status", line)
            # print("HEHEHEHEHEHE")
            res = subprocess.run(['playerctl', '-p', 'spotify', 'position'], capture_output=True)
            # print("--------------")
            # print(res.stdout)
            # print("--------------")
            pos = float(res.stdout.strip())
            set_attribute("position", secs_to_micros(pos))

def timer():
    global spotify_state

    # print("Starting timer")

    sleep_time = 0.1

    while True:
        if spotify_state["running"] and spotify_state["status"] == "Playing":
            pos = spotify_state["position"] + secs_to_micros(sleep_time)
            set_attribute("position", pos)
        time.sleep(sleep_time)


def position():
    global spotify_state

    # print("Starting position")

    proc = subprocess.Popen(['playerctl', '-p', 'spotify', '-F', 'position'], stdout=subprocess.PIPE)
    while True:
        line = str(proc.stdout.readline().strip(), 'utf-8')
        
        if line != "":
            set_attribute("position", secs_to_micros(line))


threads = [
    Thread(target=metadata),
    Thread(target=status),
    Thread(target=timer),
    Thread(target=position)
]

for t in threads:
    t.start()

for t in threads:
    t.join()

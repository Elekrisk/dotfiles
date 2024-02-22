#!/usr/bin/env python3

def get_icon(windowclass):
    match windowclass:
        case "kitty":
            return ""
        case "firefox":
            return ""
        case "VSCodium" | "codium" | "codium-url-handler":
            return ""
        case "Spotify":
            return ""
        case _:
            return "?"

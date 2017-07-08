#!/bin/sh

xset s off         # don't activate screensaver
xset -dpms         # disable DPMS (Energy Star) features.
xset s noblank     # don't blank the video device

exec /home/pi/src/lil-t/tools/lil-tk.py

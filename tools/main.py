#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import print_function

import argparse
import logging

from fb import FramebufferUI
from model import Model
from util import add_midi_event_listener


DEFAULT_PLUGIN = 'http://drobilla.net/plugins/mda/Piano'

LOG_FILE_PATH = '/home/pi/lil-tk.log'

SYSEX_UP = 0
SYSEX_DOWN = 4
SYSEX_LEFT = 1
SYSEX_RIGHT = 5
SYSEX_ONE = 8
SYSEX_TWO = 9
SYSEX_THREE = 10
SYSEX_FOUR = 11
SYSEX_FIVE = 12
SYSEX_SIX = 13

MANUFACTURER_ID = 0x7D


logging.basicConfig(
    filename=LOG_FILE_PATH,
    filemode='w',
    )
logger = logging.getLogger(__name__)


def on_event(event):
  print(event)


def on_midi_event(self, midi_input_name, message):
  logger.info('midi(%s): %s', midi_input_name, message)

#
def main():
  model = Model()
  model.clear_modules()

  fbui = FramebufferUI()
  fbui.fill((0, 0, 255))

  add_midi_event_listener(on_midi_event)

  model.add_module(DEFAULT_PLUGIN, 0)

  fbui.listen(on_event)


#
if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('--debug', action='store_true')

  args = parser.parse_args()

  debug = args.debug

  if debug:
    logger.setLevel(logging.DEBUG)

  main()

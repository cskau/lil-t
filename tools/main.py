#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import print_function

import argparse
import logging

import pygame

from fb import FramebufferUI
from model import Model
import util
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


def on_midi_event(midi_input_name, message):
  logger.info('midi(%s): %s', midi_input_name, message)


class Controls:

  def __init__(self, model, screen):
    self.model = model
    self.screen = screen
    self.symbols = model.get_symbols(DEFAULT_PLUGIN)
    self.font = pygame.font.Font(None, 18)
    self.active_symbol_nos = [i for i in range(min(4, len(self.symbols)))]


  def draw(self):
    self.screen.fill((0, 0, 0))

    # pygame.draw.rect(self.screen, (0, 255, 0), (8, 28, 54, 34), 2)
    # pygame.draw.line(self.screen, (0, 255, 0), (10, 100), (510, 100))

    active_channel = 0
    x = 0
    for symbol_no in self.active_symbol_nos:
      symbol, min_val, default_val, max_val = self.symbols[symbol_no]
      param_val = self.model.get_param(active_channel, symbol)
      text_surface = self.font.render(
          '{}: {}'.format(symbol, param_val),
          False,
          (255, 255, 255))
      text_surface = pygame.transform.rotate(text_surface, -90)
      self.screen.blit(text_surface, (x, 10))
      x += 40

    pygame.display.flip()


  def adjust(self, channel, symbol_no, adjustment):
    symbol, min_val, default_val, max_val = self.symbols[symbol_no]
    param_val = self.model.get_param(channel, symbol)
    self.model.set_param(channel, symbol, param_val + adjustment)


  def on_pygame_event(self, event):
    active_channel = 0
    if event.type == pygame.KEYDOWN:
      print(event.key, event)
      if event.key == 27: # Esc
        pygame.quit()
      elif event.key == 282: # F1
        print('F1')
      elif event.key == 283: # F2
        print('F2')
      elif event.key == 284: # F3
        print('F3')
      elif event.key == 285: # F4
        print('F4')
      elif event.key == 49: # 1
        self.active_symbol_nos[0] += 1
        self.active_symbol_nos[0] %= len(self.symbols)
      elif event.key == 50: # 2
        self.active_symbol_nos[1] += 1
        self.active_symbol_nos[1] %= len(self.symbols)
      elif event.key == 51: # 3
        self.active_symbol_nos[2] += 1
        self.active_symbol_nos[2] %= len(self.symbols)
      elif event.key == 52: # 4
        self.active_symbol_nos[3] += 1
        self.active_symbol_nos[3] %= len(self.symbols)
      elif event.key == 113: # q
        adjustment = 0.1 if event.mod == 0 else -0.1
        self.adjust(active_channel, self.active_symbol_nos[0], adjustment)
      elif event.key == 119: # w
        adjustment = 0.1 if event.mod == 0 else -0.1
        self.adjust(active_channel, self.active_symbol_nos[1], adjustment)
      elif event.key == 101: # e
        adjustment = 0.1 if event.mod == 0 else -0.1
        self.adjust(active_channel, self.active_symbol_nos[2], adjustment)
      elif event.key == 114: # r
        adjustment = 0.1 if event.mod == 0 else -0.1
        self.adjust(active_channel, self.active_symbol_nos[3], adjustment)
      self.draw()


#
def main():
  model = Model()
  model.clear_modules()

  add_midi_event_listener(on_midi_event)

  model.add_module(DEFAULT_PLUGIN, 0)

  model.jack_client.connect(
      'a2j:LPK25 [24] (capture): LPK25 MIDI 1',
      'effect_0:event_in',
      )
  model.jack_client.connect(
      'effect_0:left_out',
      'system:playback_1',
      )
  model.jack_client.connect(
      'effect_0:right_out',
      'system:playback_2',
      )

  fbui = FramebufferUI()
  fbui.screen.fill((0, 0, 0))
  pygame.display.flip()

  controls = Controls(model, fbui.screen)
  controls.draw()

  fbui.listen(controls.on_pygame_event)


#
if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('--debug', action='store_true')

  args = parser.parse_args()

  debug = args.debug

  if debug:
    logger.setLevel(logging.DEBUG)
    util.logger.setLevel(logging.DEBUG)

  main()

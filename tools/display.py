#!/usr/bin/env python

from __future__ import print_function

import logging
import socket
from time import sleep

import Image
import ImageDraw
import ImageFont

from lilv import World
from lilv import Plugin
from lilv import Instance

import mido

#import display_emulator
import ST7735 as TFT
import Adafruit_GPIO.SPI as SPI


logger = logging.getLogger(__name__)


SPEED_HZ = 4000000
DISPLAY_PIN_DC = 24
DISPLAY_PIN_RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

FRAME_DELAY_SECONDS = 0.1
WIDTH = 128
HEIGHT = 160

COLOURS = [
  '#dfd9ff', # light grey
  '#ff385c', # red
  '#00ee96', # green
  '#6f99ff', # blue
  '#1a75bb', # dark blue
  '#6e6f84', # dark grey
  '#9557dc', # purple
  '#966757', # brown
]


##
class Mod():

  def __init__(self):
    self.to_modhost_socket = self.open_socket(port=5555)
    self.from_modhost_socket = self.open_socket(port=5556)

    self.plugin_map = {}

    world = World()
    world.load_all()
    self.plugins = world.get_all_plugins()

    for plugin in self.plugins:
      uri = plugin.get_uri()
      self.plugin_map[str(uri)] = plugin

    midi_output_names = mido.get_input_names()
    for midi_output_name in midi_output_names:
      input_port = mido.open_input(
          midi_output_name,
          callback=lambda message:self.on_midi_event(midi_output_name, message),
          )


  def on_midi_event(self, midi_output_name, message):
    val = ((message.note - 53) / 23.0) * 100
    self.set_param(0, 'volume', val)


  def render_loop(self, frame_ui, frame_callback, scale=1, delay=FRAME_DELAY_SECONDS):
    while True:
      plugin = self.plugin_map['urn:50m30n3:plugins:SO-666']

      frame_ui.clear()

      x, y = 20, 20
      for p in range(plugin.get_num_ports()):
        port = plugin.get_port(p)
        port_range = port.get_range()
        if not port_range[1] is None:
          default_val, min_val, max_val = [float(str(v)) for v in port_range]

          val = default_val

          symbol = port.get_symbol()
          resp = self.get_param(0, symbol)
          resp_parts = resp.split(' ')
          if len(resp_parts) == 3:
            resp_header, resp_channel, resp_val = resp_parts
            val = float(resp_val[:6])

          frame_ui.draw_knob(x, y, (val, min_val, max_val))
          x += 40
          if x >= 140:
            x = 20
            y += 40

      frame = frame_ui.get_frame()
      if scale != 1:
        frame = frame.resize(
            (frame.width * scale, frame.height * scale),
            Image.NEAREST,
            )

      frame_callback(frame)

      sleep(delay)


  def open_socket(self, host='localhost', port=5555):
    new_socket = socket.socket()
    new_socket.connect((host, port))
    new_socket.settimeout(5)
    return new_socket


  def send_command(self, command):
    self.to_modhost_socket.send(command)

    logger.debug('sent: %s', command)
    
    resp = None

    try:
      resp = self.to_modhost_socket.recv(1024)
      if resp:
        logger.debug('resp: %s', resp)
    except Exception:
      return None

    # try:
    #   resp = self.from_modhost_socket.recv(1024)
    #   if resp:
    #     logging.debug('resp: %s', resp)
    # except Exception:
    #   return None

    return resp


  def get_param(self, channel, symbol):
    return self.send_command('param_get {} {}'.format(channel, symbol))


  def set_param(self, channel, symbol, value):
    return self.send_command('param_set {} {} {}'.format(channel, symbol, value))


  def get_presets(self, URI):
    return self.send_command('preset_show {}'.format(URI))


##
class FrameUI():

  def __init__(self, width, height, background_color=(0, 0, 0, 255)):
    self.width = width
    self.height = height
    self.size = 18
    self.background_color = background_color

    self.image = Image.new(
        'RGBA',
        (self.width, self.height),
        self.background_color,
        )

    self.draw = ImageDraw.Draw(self.image)

    self.font = ImageFont.truetype(
        '~/.fonts/Dosis/Dosis-Light.ttf', # !
        # '~/.fonts/Advent_Pro/AdventPro-Light.ttf', # !
        # '~/.fonts/Abel/Abel-Regular.ttf', # !
        self.size,
        )


  def get_frame(self):
    return self.image


  def clear(self):
    self.draw.rectangle(
        [(0, 0), (self.width, self.height)],
        self.background_color)


  def draw_menu(self, items, selected):
    for i, item in enumerate(items):
      if selected == i:
        self.draw.rectangle(
            (
              (10 - 5, i * self.size),
              (self.width - 10 + 10/2, i * self.size + 20 + 5)
            ),
            COLOURS[5],
            )
      self.draw.text(
          (10, i * self.size),
          item,
          COLOURS[2],
          font=font,
          )


  def draw_knob(self, x, y, vr):
    val, val_min, val_max = vr
    deg = 360 * (float(val - val_min) / float(val_max - val_min))
    self.draw.pieslice(
        ((x, y), (x+30, y+30)),
        -90,
        deg - 90,
        COLOURS[4],
        )
    self.draw.text(
        (x+5, y+5),
        str(val),
        COLOURS[2],
        font=self.font,
        )


##
def main():
  # display = display_emulator.DisplayEmulator(WIDTH, HEIGHT, scale=2)

  display = TFT.ST7735(
      DISPLAY_PIN_DC,
      rst=DISPLAY_PIN_RST,
      spi=SPI.SpiDev(
          SPI_PORT,
          SPI_DEVICE,
          max_speed_hz=SPEED_HZ))
  display.begin()

  frame_ui = FrameUI(WIDTH, HEIGHT)

  mod = Mod()

  mod.send_command('remove {}'.format(0))
  mod.send_command('add {} {}'.format('urn:50m30n3:plugins:SO-666', 0))

  mod.render_loop(
      frame_ui,
      frame_callback=lambda image:display.display(image))


##
if __name__ == '__main__':
  main()

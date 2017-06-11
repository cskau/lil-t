#!/usr/bin/env python

from __future__ import print_function

import argparse
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

import jack


logging.basicConfig()
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

FONT = '/home/pi/.fonts/Dosis-Light.ttf'
# '/home/pi/.fonts/Advent_Pro/AdventPro-Light.ttf'
# '/home/pi/.fonts/Abel/Abel-Regular.ttf'

DEFAULT_PLUGIN = 'http://drobilla.net/plugins/mda/DX10'
# DEFAULT_PLUGIN = 'http://drobilla.net/plugins/mda/JX10'
# DEFAULT_PLUGIN = 'http://drobilla.net/plugins/mda/EPiano'
# DEFAULT_PLUGIN = 'http://drobilla.net/plugins/mda/Piano'
# DEFAULT_PLUGIN = 'http://magnus.smartelectronix.com/lv2/synth/qin' # Not polyphonic.
# DEFAULT_PLUGIN = 'urn:50m30n3:plugins:SO-404' # Channel has to be 15, other controls don't work?
# DEFAULT_PLUGIN = 'urn:50m30n3:plugins:SO-666' # Channel has to be 15, other controls don't work?
# DEFAULT_PLUGIN = 'urn:50m30n3:plugins:SO-kl5' # Channel has to be 15, other controls don't work?


##
class Mod():

  def __init__(self):
    self.to_modhost_socket = self.open_socket(port=5555)
    self.from_modhost_socket = self.open_socket(port=5556)

    self.plugin_map = {}

    world = World()
    world.load_all()
    self.plugins = world.get_all_plugins()

    # Pre-load info about all known plugins.
    for plugin in self.plugins:
      if self.is_midi_plugin(plugin):
        uri = plugin.get_uri()
        self.plugin_map[str(uri)] = plugin

    self.active_plugin = None

    # setup handler for all incoming MIDI messages.
    midi_output_names = mido.get_input_names()
    for midi_output_name in midi_output_names:
      input_port = mido.open_input(
          midi_output_name,
          callback=lambda message:self.on_midi_event(midi_output_name, message),
          )

    self.knob_mapping = {
      16: 0, # General Purpose Controller 1
      17: 1, # General Purpose Controller 2
      18: 2, # General Purpose Controller 3
      19: 3, # General Purpose Controller 4
    }

    self.state = 'menu'
    # self.state = 'knobs'


  def is_midi_plugin(self, plugin):
    for p in range(plugin.get_num_ports()):
      port = plugin.get_port(p)
      if self.is_midi_port(port):
        return True
    return False


  def is_midi_port(self, port):
    classes = [str(c) for c in port.get_classes()]
    if ('http://lv2plug.in/ns/lv2core#InputPort' in classes
        and 'http://lv2plug.in/ns/ext/atom#AtomPort' in classes):
      return True
    return False


  def remove_plugin(self, number):
    self.send_command('remove {}'.format(number))


  def add_plugin(self, number, plugin_uri):
    self.send_command('add {} {}'.format(plugin_uri, 0))

    self.ports = []

    plugin = self.plugin_map[plugin_uri]
    for p in range(plugin.get_num_ports()):
      port = plugin.get_port(p)
      port_range = port.get_range()
      if not (port_range[0] is None or port_range[1] is None):
        default_val, min_val, max_val = [float(str(v)) for v in port_range]
        symbol = port.get_symbol()
        self.ports.append((default_val, min_val, max_val, symbol))

        # val = default_val
        # resp = self.get_param(0, symbol)
        # if resp:
        #   resp_parts = resp.split(' ')
        #   if len(resp_parts) == 3:
        #     resp_header, resp_channel, resp_val = resp_parts
        #     val = float(resp_val[:6])
        #     self.ports.append((val, min_val, max_val, symbol))


  def on_midi_event(self, midi_output_name, message):
    logger.info('midi(%s): %s', midi_output_name, message)
    if message.type == 'note_on':
      message.channel
      message.note
      message.velocity
    elif message.type == 'control_change':
      message_channel = message.channel
      control = message.control
      effect_number = 0
      if control in self.knob_mapping:
        port = self.knob_mapping[control]
        if port < len(self.ports):
          val, min_val, max_val, symbol = self.ports[port]
          val = (max_val - min_val) * (message.value / 127.0) + min_val
          self.ports[port] = (val, min_val, max_val, symbol)
          self.set_param(effect_number, symbol, val)
    elif message.type == 'program_change':
      message.channel
      message.program
    elif message.type == 'sysex':
      data = message.data
      if len(data) == 3:
        manufacturer_id, button, onoff = data
        if manufacturer_id == 0x7D:
          logger.debug('Button pressed: %s', button)
          if button == 0:
            # Switch to next plugin
            if self.active_plugin is None or self.active_plugin >= len(self.plugin_map):
              self.active_plugin = 0
            self.active_plugin += 1
            print(self.active_plugin, len(self.plugin_map))
            for i, plugin_uri in enumerate(self.plugin_map):
              if self.active_plugin == i:
                self.remove_plugin(0)
                self.add_plugin(0, plugin_uri)
          elif button == 1:
            self.state = 'knobs'
          elif button == 8:
            # Switch knob 0 to next control.
            self.knob_mapping[16] += 1
          elif button == 9:
            self.knob_mapping[17] += 1
          elif button == 10:
            self.knob_mapping[18] += 1
          elif button == 11:
            self.knob_mapping[19] += 1
          elif button == 12:
            # Reset knobs.
            self.knob_mapping[16] = 0
            self.knob_mapping[17] = 1
            self.knob_mapping[18] = 2
            self.knob_mapping[19] = 3
          elif button == 13:
            # Print all port params for plugin.
            effect_number = 0
            for val, min_val, max_val, symbol in self.ports:
              val = self.get_param(effect_number, symbol)
              print(val, min_val, max_val, symbol)


  def render_menu(self, frame_ui):
    frame_ui.draw_menu(
        items=['item0', 'item1'],
        selected=0,
        )


  def render_knobs(self, frame_ui):
    x, y = 10, 20
    for val, min_val, max_val, symbol in self.ports:
      frame_ui.draw_knob(x, y, (val, min_val, max_val), symbol)
      x += 40
      if x >= 100:
        x = 10
        y += 40


  def render_loop(self, frame_ui, frame_callback, delay=FRAME_DELAY_SECONDS):
    while True:
      frame_ui.clear()

      if self.state == 'menu':
        self.render_menu(frame_ui)
      elif self.state == 'knobs':
        self.render_knobs(frame_ui)

      frame = frame_ui.get_frame()

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
        FONT,
        self.size,
        )
    self.font12 = ImageFont.truetype(
        FONT,
        12,
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
          font=self.font,
          )


  def draw_knob(self, x, y, vr, symbol, diameter=30):
    val, val_min, val_max = vr
    deg = int(360 * (float(val - val_min) / float(val_max - val_min)))
    self.draw.pieslice(
        ((x, y), (x+diameter, y+diameter)),
        -90,
        deg - 90,
        COLOURS[4],
        )
    self.draw.text(
        (x, y+5),
        '{:0.2f}'.format(val),
        COLOURS[2],
        font=self.font,
        )
    self.draw.text(
        (x, y-10),
        str(symbol),
        COLOURS[1],
        font=self.font12,
        )


def connect_audio_midi(jack_client):
  # Connect A2J Teensy MIDI output to all plugin MIDI inputs
  teensy_midi_outs = jack_client.get_ports('Teensy', is_midi=True, is_output=True)
  plugins_midi_ins = jack_client.get_ports('effect_', is_midi=True, is_input=True)

  if len(teensy_midi_outs) == 1 and plugins_midi_ins:
    for midi_in in plugins_midi_ins:
      jack_client.connect(teensy_midi_outs[0], midi_in)
  else:
    logger.error(
        'Found wrong amount of MIDI ports: %s outs, %s ins',
        len(teensy_midi_outs),
        len(plugins_midi_ins))

  # Connect plugin audio to system audio
  plugins_audio_outs = jack_client.get_ports(
      'effect_',
      is_audio=True,
      is_output=True,
      )
  system_audio_ins = jack_client.get_ports(
      'system:playback_',
      is_audio=True,
      is_input=True,
      )

  if len(plugins_audio_outs) in [1, 2] and len(system_audio_ins) >= 2:
    jack_client.connect(plugins_audio_outs[0], system_audio_ins[0])
    jack_client.connect(plugins_audio_outs[-1], system_audio_ins[1])
  else:
    logger.error(
        'Found wrong amount of audio ports: %s outs, %s ins',
        len(plugins_audio_outs),
        len(system_audio_ins))


##
def main(emulate_display=False, plugin=DEFAULT_PLUGIN):
  logger.info('Connecting display')

  if emulate_display:
    import display_emulator
    display = display_emulator.DisplayEmulator(WIDTH, HEIGHT, scale=2)
  else:
    import ST7735 as TFT
    import Adafruit_GPIO.SPI as SPI
    display = TFT.ST7735(
        DISPLAY_PIN_DC,
        rst=DISPLAY_PIN_RST,
        spi=SPI.SpiDev(
            SPI_PORT,
            SPI_DEVICE,
            max_speed_hz=SPEED_HZ))
    display.begin()

  frame_ui = FrameUI(WIDTH, HEIGHT)

  logger.info('Connecting to mod-host')

  mod = Mod()
  mod.remove_plugin(0)
  mod.add_plugin(0, plugin)

  logger.info('Connecting to JACK')

  jack_client = jack.Client(
      'my_jack_client',
      no_start_server=False,
      servername=None)

  jack_client.activate()

  # logger.info('Connecting to ports')

  # connect_audio_midi(jack_client)

  logger.info('Looping')

  mod.render_loop(
      frame_ui,
      frame_callback=lambda image:display.display(image))


##
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--emulate_display', action='store_true')
  parser.add_argument('--debug', action='store_true')
  parser.add_argument('--plugin')
  args = parser.parse_args()

  debug = args.debug
  emulate_display = args.emulate_display
  plugin = args.plugin

  if debug:
    logger.setLevel(logging.DEBUG)

  main(emulate_display, plugin)

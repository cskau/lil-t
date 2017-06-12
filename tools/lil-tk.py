#!/usr/bin/env python

from __future__ import print_function

import argparse
import logging

from Tkinter import *

from util import ModHostConnection
from util import add_midi_event_listener
from util import get_plugins
from util import get_jack_client
from util import connect_audio_midi


LOG_FILE_PATH = '/home/pi/lil-tk.log'

WIDTH = 160
HEIGHT = 128

SYSEX_UP = 0
SYSEX_DOWN = 4
SYSEX_RIGHT = 1
SYSEX_LEFT = 5


logging.basicConfig(
    filename=LOG_FILE_PATH,
    filemode='w',
    )
logger = logging.getLogger(__name__)


class LilTKApp:

  def __init__(self, root, width=WIDTH, height=HEIGHT, scale=1):
    self.root = root

    self.root.wm_title('lil-tk')

    # Set explicite window size.
    self.root.geometry("{}x{}".format(width, height))

    self.frame = Frame(self.root)
    self.frame.pack(fill=BOTH, expand=YES)

    # my_label = Label(self.frame, text="Hello, world!")
    # my_label.pack()

    #
    plugins, plugin_map = get_plugins()

    self.listbox = self.add_listbox(self.frame, [p.get_uri() for p in plugins])
    self.listbox.bind('<<ListboxSelect>>', self.on_select)

    #
    add_midi_event_listener(self.on_midi_event)

    #
    self.mod_host = ModHostConnection()

    self.mod_host.add_plugin('http://drobilla.net/plugins/mda/EPiano', 0)

    #
    self.jack_client = get_jack_client('liltk_jack_client')
    connect_audio_midi(self.jack_client)


  def on_midi_event(self, midi_input_name, message):
    logger.info('midi(%s): %s', midi_input_name, message)


  def add_listbox(self, master, options):
    listbox = Listbox(master, selectmode=EXTENDED)
    listbox.pack(fill=BOTH, expand=YES)
    for item in options:
      listbox.insert(END, item)
    return listbox


  def on_select(self, event):
    w = event.widget

    # for c in self.controls:
    #   c.pack_forget()

    for i, selection in enumerate(w.curselection()):
      value = w.get(int(selection))
      # self.mod_host.send_command('remove {}'.format(selection))
      # self.mod_host.send_command('add {} {}'.format(value, selection))
      self.mod_host.send_command('remove {}'.format(i))
      self.mod_host.send_command('add {} {}'.format(value, i))
      # self.mod_host.get_presets(value)

    connect_audio_midi(self.jack_client)


  def set_fullscreen(self, fullscreen):
    # Set window to fullscreen mode.
    self.root.attributes("-fullscreen", fullscreen)


  def set_window_border(self, hide_border=1):
    # Remove window border
    self.root.overrideredirect(show_border)


def main():
  root = Tk()

  app = LilTKApp(root)

  root.mainloop()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--debug', action='store_true')
  args = parser.parse_args()

  debug = args.debug

  if debug:
    logger.setLevel(logging.DEBUG)

  main()

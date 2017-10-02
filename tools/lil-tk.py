#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import print_function

import argparse
import logging

from Tkinter import *

from util import ModHostConnection
from util import add_midi_event_listener
from util import get_plugins
from util import get_jack_client
from util import get_ports
from util import get_symbols
from util import connect_effect


LOG_FILE_PATH = '/home/pi/lil-tk.log'

WIDTH = 160
HEIGHT = 128

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


#
def add_listbox(master, options):
  listbox = Listbox(master, selectmode=EXTENDED)
  listbox.pack(fill=BOTH, expand=YES)
  for item in options:
    listbox.insert(END, item)
  return listbox


def move_selection(listbox, delta):
  selection = (listbox.curselection() or [0])[0]
  selection = min(max(selection + delta, 0), listbox.size() - 1)
  listbox.selection_clear(0, listbox.size() - 1)
  listbox.selection_set(selection)
  listbox.see(selection)


#
class Model:

  def __init__(self):
    self.plugins_slots = {}

    #
    self.plugins, self.plugin_map = get_plugins()

    #
    self.mod_host = ModHostConnection()

    #
    self.jack_client = get_jack_client('liltk_jack_client')


  def get_plugin_urls(self):
    return [p.get_uri() for p in self.plugins]


  def clear_modules(self):
    for i in range(len(self.plugins_slots)):
      self.clear_module(i)


  def clear_module(self, i):
    self.mod_host.remove_plugin(i)
    self.plugins_slots[i] = ''


  # def add_modules(self, plugins):
  #   for i in range(16):
  #     self.mod_host.send_command('remove {}'.format(i))
  #   for i, plugin in enumerate(plugins):
  #     # self.mod_host.send_command('remove {}'.format(selection))
  #     # self.mod_host.send_command('add {} {}'.format(value, selection))
  #     # self.mod_host.send_command('remove {}'.format(i))
  #     self.mod_host.send_command('add {} {}'.format(plugin, i))
  #     # self.mod_host.get_presets(value)
  #
  #   connect_audio_midi(self.jack_client)


  def add_module(self, url, i):
    self.mod_host.remove_plugin(i)
    self.mod_host.add_plugin(url, i)

    self.plugins_slots[i] = url

    connect_effect(self.jack_client, 'effect_{}'.format(i))


  def get_param(self, channel, symbol):
    return self.mod_host.get_param(channel, symbol)


  def set_param(self, channel, symbol, value):
    self.mod_host.set_param(channel, symbol, value)


  def get_symbols(self, url):
    plugin = self.plugin_map[url]
    return get_symbols(plugin)


  def get_instances(self):
    return self.plugins_slots


  def get_connections(self):
    return


#
class ModulesFrame(Frame):

  def __init__(self, parent, controller, model):
    Frame.__init__(self, parent)

    self.controller = controller
    self.model = model

    self.listbox = add_listbox(self, self.model.get_instances().values())
    self.listbox.insert(END, 'Add module')
    self.listbox.selection_set(0)


  def on_event(self, message):
    if message.type == 'sysex':
      if len(message.data) == 3:
        manufacturer_id, button, onoff = message.data
        if manufacturer_id == MANUFACTURER_ID:
          if button == SYSEX_RIGHT:
            selection = (self.listbox.curselection() or [0])[0]

            if self.listbox.get(selection) == 'Add module':
              self.controller.show_load_module_frame(selection)
            else:
              instances = self.model.get_instances()
              self.controller.show_controls_frame(instances[selection])
          else:
            if button == SYSEX_UP:
              move_selection(self.listbox, -1)
            elif button == SYSEX_DOWN:
              move_selection(self.listbox, +1)
            selection = (self.listbox.curselection() or [0])[0]
            self.controller.set_instance_number(selection)


#
class LoadModulesFrame(Frame):

  def __init__(self, parent, controller, model, instance_number):
    Frame.__init__(self, parent)

    self.controller = controller

    self.listbox = add_listbox(self, model.get_plugin_urls())
    self.listbox.selection_set(0)

    self.instance_number = instance_number


  def on_event(self, message):
    selection = (self.listbox.curselection() or [0])[0]

    if message.type == 'sysex':
      if len(message.data) == 3:
        manufacturer_id, button, onoff = message.data
        if manufacturer_id == MANUFACTURER_ID:
          if button == SYSEX_UP:
            move_selection(self.listbox, -1)
          elif button == SYSEX_DOWN:
            move_selection(self.listbox, +1)
          elif button == SYSEX_RIGHT:
            self.controller.load_into_instance(
                self.listbox.get(selection),
                self.instance_number,
                )


#
class ControlsFrame(Frame):

  def add_labels(self, key, val, column, bg=None):
    value_var = DoubleVar()
    value_var.set(val)
    label_var = StringVar()
    label_var.set(key)
    knob = Label(self, text='x', justify=CENTER, wraplength=40, bg=bg)
    knob.grid(row=0, column=column)
    value = Label(self, textvariable=value_var, justify=CENTER, wraplength=40)
    value.grid(row=1, column=column)
    label = Label(self, textvariable=label_var, justify=CENTER, wraplength=40)
    label.grid(row=2, column=column)
    return value_var, label_var


  def __init__(self, parent, controller, model, instance_number, url):
    Frame.__init__(self, parent)

    self.controller = controller
    self.model = model

    self.url = url
    self.instance_number = instance_number

    self.offset = 0

    symbols = self.model.get_symbols(self.url)

    if len(symbols) < 1:
      return

    self.value_var1, self.label_var1 = self.add_labels(
        symbols[0 + self.offset][0], symbols[0 + self.offset][1], 0, 'light yellow')

    if len(symbols) < 2:
      return

    self.value_var2, self.label_var2 = self.add_labels(
        symbols[1 + self.offset][0], symbols[1 + self.offset][1], 1, 'light green')

    if len(symbols) < 3:
      return

    self.value_var3, self.label_var3 = self.add_labels(
        symbols[2 + self.offset][0], symbols[2 + self.offset][1], 2, 'light pink')

    if len(symbols) < 4:
      return

    self.value_var4, self.label_var4 = self.add_labels(
        symbols[3 + self.offset][0], symbols[3 + self.offset][1], 3, 'light blue')


  def on_event(self, message):
    if message.type == 'control_change':
      symbols = self.controller.get_symbols(self.url)

      symbol_index = message.control - 16 + self.offset

      symbol, default_val, min_val, max_val = symbols[symbol_index]

      value = (max_val - min_val) * (message.value / 127.0) + min_val

      self.controller.set_param(self.instance_number, symbol, value)

      if message.control == 16:
        self.value_var1.set(value)
      elif message.control == 17:
        self.value_var2.set(value)
      elif message.control == 18:
        self.value_var3.set(value)
      elif message.control == 19:
        self.value_var4.set(value)


#
class PortsFrame(Frame):

  def __init__(self, parent, controller, model, instance_number):
    Frame.__init__(self, parent)

    self.controller = controller
    self.model = model

    self.listbox = None
    self.list_ports()

    self.selected = None


  def list_ports(self, effect=''):
    if self.listbox:
      self.listbox.destroy()
    # effect = 'effect_{}:'.format(instance_number)
    ports = [p.name for p in self.model.jack_client.get_ports(effect)]
    # ports = [p.name for p in self.model.jack_client.get_ports()]
    self.listbox = add_listbox(self, ports)
    self.listbox.selection_set(0)


  def on_event(self, message):
    if message.type == 'sysex':
      if len(message.data) == 3:
        manufacturer_id, button, onoff = message.data
        if manufacturer_id == MANUFACTURER_ID:
          if button == SYSEX_UP:
            move_selection(self.listbox, -1)
          elif button == SYSEX_DOWN:
            move_selection(self.listbox, +1)
          elif button == SYSEX_RIGHT:
            selection = (self.listbox.curselection() or [0])[0]
            if self.selected:
              self.model.jack_client.connect(
                  self.selected,
                  self.listbox.get(selection),
                  )
              self.selected = None
              self.controller.show_modules_frame()
              return
            self.selected = self.listbox.get(selection)
            self.list_ports()


#
class LilTKApp:

  def __init__(self, root, width=WIDTH, height=HEIGHT, scale=1):
    self.root = root

    #
    self.model = Model()

    self.model.clear_modules()

    #
    self.root.title('lil-tk')

    # Set explicite window size.
    self.root.geometry("{}x{}".format(width, height))

    # Container frame where all other frames are put.
    self.container = Frame(root, bg="pink")
    self.container.pack(side="top", fill="both", expand=True)
    self.container.grid_rowconfigure(0, weight=1)
    self.container.grid_columnconfigure(0, weight=1)

    #
    self.instance_number = 0
    self.active_frame = None

    self.show_modules_frame()

    #
    add_midi_event_listener(self.on_midi_event)


  def set_instance_number(self, instance_number):
    self.instance_number = instance_number


  def set_param(self, instance_number, symbol, value):
    self.model.set_param(instance_number, symbol, value)


  def get_symbols(self, url):
    return self.model.get_symbols(url)


  def switch_to_frame(self, frame):
    if self.active_frame:
      self.active_frame.pack_forget()
      self.active_frame.destroy()
    frame.grid(row=0, column=0, sticky="nsew")
    frame.tkraise()
    self.active_frame = frame


  def show_modules_frame(self):
    self.switch_to_frame(
        ModulesFrame(
            parent=self.container,
            controller=self,
            model=self.model,
            )
        )


  def show_load_module_frame(self, instance_number):
    self.switch_to_frame(
        LoadModulesFrame(
            parent=self.container,
            controller=self,
            model=self.model,
            instance_number=instance_number,
            )
        )


  def show_controls_frame(self, url):
    self.switch_to_frame(
        ControlsFrame(
            parent=self.container,
            controller=self,
            model=self.model,
            instance_number=self.instance_number,
            url=url,
            )
        )


  def show_ports_frame(self, instance_number):
    self.switch_to_frame(
        PortsFrame(
            parent=self.container,
            controller=self,
            model=self.model,
            instance_number=instance_number,
            )
        )


  def on_midi_event(self, midi_input_name, message):
    logger.info('midi(%s): %s', midi_input_name, message)

    if message.type == 'sysex':
      if len(message.data) == 3:
        manufacturer_id, button, onoff = message.data
        if manufacturer_id == MANUFACTURER_ID:
          if button == SYSEX_ONE:
            self.show_modules_frame()
          elif button == SYSEX_TWO:
            self.show_load_module_frame(self.instance_number)
          elif button == SYSEX_THREE:
            selection = 1
            instances = self.model.get_instances()
            instance = instances[selection]
            self.show_controls_frame(instance)
          elif button == SYSEX_FOUR:
            self.show_ports_frame(self.instance_number)
          else:
            self.active_frame.on_event(message)
    elif message.type == 'control_change':
      self.active_frame.on_event(message)


  def load_into_instance(self, url, instance_number):
    self.model.add_module(url, instance_number)
    self.show_modules_frame()


  def set_fullscreen(self, fullscreen):
    # Set window to fullscreen mode.
    self.root.attributes("-fullscreen", fullscreen)


  def set_window_border(self, show_border):
    # Remove window border
    self.root.overrideredirect(1 if show_border else 0)


#
def main():
  root = Tk()

  app = LilTKApp(root)

  root.mainloop()


#
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--debug', action='store_true')
  args = parser.parse_args()

  debug = args.debug

  if debug:
    logger.setLevel(logging.DEBUG)

  main()

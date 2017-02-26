#!/usr/bin/env python

from __future__ import print_function

import socket

from Tkinter import *

from lilv import World
from lilv import Plugin
from lilv import Instance


class LilUIApp:

  def __init__(self, master):
    self.frame = Frame(master)
    self.frame.pack(fill=BOTH, expand=YES)

    self.controls = []

    self.to_modhost_socket = self.open_socket(port=5555)
    self.from_modhost_socket = self.open_socket(port=5556)

    world = World()
    world.load_all()
    self.plugins = world.get_all_plugins()

    self.list = self.add_listbox(self.frame, [p.get_uri() for p in self.plugins])
    self.list.bind('<<ListboxSelect>>', self.onselect)


  def onselect(self, event):
    w = event.widget
    
    for c in self.controls:
      c.pack_forget()
    
    for selection in w.curselection():
      value = w.get(int(selection))
      self.send_command('remove {}'.format(selection))
      self.send_command('add {} {}'.format(value, selection))
      # self.get_presets(value)

      for plugin in self.plugins:
        name = unicode(plugin.get_name()).encode('utf-8')
        uri = plugin.get_uri()
        num_ports = plugin.get_num_ports()
        if uri == value:
          for p in range(num_ports):
            port = plugin.get_port(p)
            index = port.get_index()
            name = unicode(port.get_name()).encode('utf-8')
            port_range = port.get_range()
            scale_points = port.get_scale_points()
            symbol = port.get_symbol()

            default_val, min_val, max_val = port_range
            if not default_val is None:
              scale = self.add_scale(
                  self.frame,
                  from_val=min_val,
                  to_val=max_val,
                  default=default_val,
                  label=name,
                  )
              scale.bind("<B1-Motion>", self.on_scale_change)
              self.controls.append(scale)


  def on_scale_change(self, event):
    widget = event.widget
    selection = widget.selection_get()
    value = widget.get()
    label = widget.cget('label')

    for i, plugin in enumerate(self.plugins):
      if plugin.get_uri() == selection:
        for p in range(plugin.get_num_ports()):
          port = plugin.get_port(p)
          symbol = port.get_symbol()
          name = unicode(port.get_name()).encode('utf-8')
          if name == label:
            self.send_command('param_set {} {} {}'.format(i, symbol, value))


  def add_listbox(self, master, options):
    listbox = Listbox(master, selectmode=EXTENDED)
    listbox.pack(fill=BOTH, expand=YES)
    for item in options:
      listbox.insert(END, item)
    return listbox


  def add_scale(self, master, from_val, to_val, default=0, label=None, on_change=None):
    new_scale = Scale(
        master,
        from_=from_val,
        to=to_val,
        orient=VERTICAL,
        resolution=0.1,
        label=label,
        command=on_change,
        )
    new_scale.set(default)
    new_scale.pack(side=LEFT)
    return new_scale


  def add_button(self):
    #frame.quit
    new_button = Button(frame, text="Hello", command=self.say_hi)
    new_button.pack(side=LEFT)
    self.buttons.append(new_button)


  def open_socket(self, host='localhost', port=5555):
    new_socket = socket.socket()
    new_socket.connect((host, port))
    new_socket.settimeout(5)
    return new_socket


  def send_command(self, command):
    self.to_modhost_socket.send(command)
    print('sent:', command)

    try:
      resp = self.to_modhost_socket.recv(1024)
      if resp:
        print('resp:', resp)
    except Exception:
      return False

    if False:
      try:
        resp = self.from_modhost_socket.recv(1024)
        if resp:
          print('resp:', resp)
      except Exception:
        return False

    return True


  def get_presets(self, URI):
    self.send_command('preset_show {}'.format(URI))


def main():
  root = Tk()

  app = LilUIApp(root)

  root.mainloop()
  #root.destroy()


if __name__ == '__main__':
  main()

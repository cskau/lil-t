#!/usr/bin/env python

from __future__ import print_function

import argparse
from time import sleep

from lilv import World
from lilv import Plugin
from lilv import Instance

import numpy


def print_port(port):
  classes = port.get_classes()
  index = port.get_index()
  name = unicode(port.get_name()).encode('utf-8')
  node = port.get_node()
  properties = port.get_properties()
  port_range = port.get_range()
  scale_points = port.get_scale_points()
  symbol = port.get_symbol()

  print('    {}'.format(name))


def print_plugin(plugin, verify=False):
  name = unicode(plugin.get_name()).encode('utf-8')
  print('{}'.format(name))

  uri = plugin.get_uri()
  print('  URI: {}'.format(uri))

  bundle_uri = plugin.get_bundle_uri()
  print('  bundle URI: {}'.format(bundle_uri))

  library_uri = plugin.get_library_uri()
  print('  library URI: {}'.format(library_uri))

  plugin_class = plugin.get_class()
  print('  class: {}'.format(plugin_class))

  num_ports = plugin.get_num_ports()
  print('  ports: {}'.format(num_ports))

  latency_port_index = plugin.get_latency_port_index()
  print('  latency port: {}'.format(latency_port_index))

  print('  Required features:')
  required_features = plugin.get_required_features()
  for f in required_features:
    print('    {}'.format(f))

  print('  Supported features:')
  supported_features = plugin.get_supported_features()
  for f in supported_features:
    print('    {}'.format(f))

  print('  Optional features:')
  optional_features = plugin.get_optional_features()
  for f in optional_features:
    print('    {}'.format(f))

  print('  UIs:')
  uis = plugin.get_uis()
  for ui in uis:
    print('    {}'.format(ui))

  print('  Ports:')
  for p in range(num_ports):
    port = plugin.get_port(p)
    print_port(port)

  if verify:
    plugin.verify()


def lv2(print_list=False, plugin_index=0):
  world = World()
  
  print('Loading plugins ...')

  # Load all installed LV2 bundles on the system.
  world.load_all()

  # Return a list of all found plugins.
  plugins = world.get_all_plugins()

  if print_list:
    print('Plugins found:')
    for i, plugin in enumerate(plugins):
      print('{}:'.format(i))
      print_plugin(plugin)
  else:
    #
    print('Instantiating plugin {}:'.format(plugin_index))
    plugin = plugins[plugin_index]
    instance = Instance(plugin, 48000)

    print_plugin(plugin)

    instance_descriptor = instance.get_descriptor()

    print(instance.get_uri())
    print(instance.get_handle())

    print('Activating plugin ..')
    instance.activate()
    
    audio_data = numpy.array([0] * 100)
    midi_data = numpy.array([0, 0, 0])
    instance.connect_port(port_index=0, data=audio_data) # Output
    instance.connect_port(port_index=1, data=midi_data) # MIDI Input
    instance.connect_port(port_index=2, data=numpy.array([0.0])) # Amp Decay
    instance.connect_port(port_index=3, data=numpy.array([0.4])) # LP Filter Decay
    instance.connect_port(port_index=4, data=numpy.array([0.1])) # HP Filter Decay
    instance.connect_port(port_index=5, data=numpy.array([0.0])) # Amp Release
    instance.connect_port(port_index=6, data=numpy.array([5.0])) # LP Filter Release
    instance.connect_port(port_index=7, data=numpy.array([5.0])) # HP Filter Release
    instance.connect_port(port_index=8, data=numpy.array([20.0])) # Pulse Width
    instance.connect_port(port_index=9, data=numpy.array([0.1])) # Detune

    instance.run(sample_count=100)
    
    print(data)

    print('Deactivating plugin ..')
    instance.deactivate()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='')
  parser.add_argument('-l', '--list', action='store_true', help='')
  parser.add_argument('-p', '--plugin', default=0, type=int, nargs='?', help='')
  args = parser.parse_args()
  
  print_list = args.list
  plugin = args.plugin

  lv2(print_list, plugin)

  print('Bye!')

#!/usr/bin/env python

from __future__ import print_function

import logging

import socket

from lilv import World
from lilv import Plugin
from lilv import Instance

import mido

import jack


logging.basicConfig()
logger = logging.getLogger(__name__)



# mod-host utils

class ModHostConnection():

  def __init__(self):
    self.to_modhost_socket, self.from_modhost_socket = self.get_mod_host_sockets()


  def get_mod_host_sockets(self):
    to_modhost_socket = self.open_socket(port=5555)
    from_modhost_socket = self.open_socket(port=5556)
    return (to_modhost_socket, from_modhost_socket)


  def open_socket(self, host='localhost', port=5555):
    new_socket = socket.socket()
    new_socket.settimeout(5)
    try:
      new_socket.connect((host, port))
    except socket.error as e:
      if e.errno == 111:
        logger.error(
            'Couldn\'t connect to mod-host socket. '
            'Check that mod-host is running and accessible.'
            )
      raise e
    return new_socket


  def send_command(self, command):
    assert self.to_modhost_socket
    assert self.from_modhost_socket

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

    return resp.strip('\x00')


  def add_plugin(self, plugin_uri, instance_number=0):
    self.send_command('add {} {}'.format(plugin_uri, instance_number))


  def remove_plugin(self, instance_number):
    self.send_command('remove {}'.format(instance_number))


  def get_presets(self, URI):
    return self.send_command('preset_show {}'.format(URI))


  def get_param(self, instance_number, symbol):
    print('param_get {} {}'.format(instance_number, symbol))
    return self.send_command('param_get {} {}'.format(instance_number, symbol))


  def set_param(self, instance_number, symbol, value):
    return self.send_command('param_set {} {} {}'.format(instance_number, symbol, value))


# LV2 utils

def get_plugins():
  world = World()
  world.load_all()

  plugins = world.get_all_plugins()

  plugin_map = {}

  # Pre-load info about all known plugins.
  for plugin in plugins:
    if is_midi_plugin(plugin):
      uri = plugin.get_uri()
      plugin_map[str(uri)] = plugin

  return (plugins, plugin_map)


def is_midi_plugin(plugin):
  for p in range(plugin.get_num_ports()):
    port = plugin.get_port(p)
    if is_midi_port(port):
      return True
  return False


def is_midi_port(port):
  for c in port.get_classes():
    if str(c) == 'http://lv2plug.in/ns/lv2core#InputPort':
      return True
    elif str(c) == 'http://lv2plug.in/ns/ext/atom#AtomPort':
      return True
  return False


def get_ports(plugin):
  ports = []
  for p in range(plugin.get_num_ports()):
    port = plugin.get_port(p)
    ports.append(port)
  return ports


def get_symbols(plugin):
  symbols = []
  for p in range(plugin.get_num_ports()):
    port = plugin.get_port(p)
    symbol = port.get_symbol()
    port_range = port.get_range()
    if not (port_range[0] is None or port_range[1] is None):
      default_val, min_val, max_val = [float(str(v)) for v in port_range]
      symbols.append((symbol, default_val, min_val, max_val))
  return symbols


# Mido MIDI utils

def add_midi_event_listener(event_handler):
  # Add handler for all incoming MIDI messages.
  midi_input_names = mido.get_input_names()
  for midi_input_name in midi_input_names:
    input_port = mido.open_input(
        midi_input_name,
        callback=lambda message: event_handler(midi_input_name, message),
        )


# jack_client JACK utils

def get_jack_client(
    client_name,
    no_start_server=False,
    servername=None,
    activate=True,
    ):
  jack_client = jack.Client(
      client_name,
      no_start_server=no_start_server,
      servername=servername,
      )

  if activate:
    jack_client.activate()

  return jack_client


def get_connections(jack_client, port):
  return jack_client.get_all_connections(port)


def get_all_ports(jack_client):
  return jack_client.get_ports()


def connect_effect(jack_client, effect, midi_in='Teensy'):
  ports = jack_client.get_ports(effect + ':')

  midi_in_ports = jack_client.get_ports(
      effect + ':',
      is_midi=True,
      is_input=True,
      )

  audio_out_ports = jack_client.get_ports(
      effect + ':',
      is_audio=True,
      is_output=True,
      )

  midi_out_ports = jack_client.get_ports(
      midi_in,
      is_midi=True,
      is_output=True,
      )

  audio_in_ports = jack_client.get_ports(
      'system:',
      is_audio=True,
      is_input=True,
      )

  # print(midi_in_ports)
  # print(audio_out_ports)
  # print(midi_out_ports)
  # print(audio_in_ports)

  if (len(midi_in_ports) == 1
      and len(audio_out_ports) == 2
      and len(midi_out_ports) == 1
      and len(audio_in_ports) == 2):
    jack_client.connect(
        audio_out_ports[0],
        audio_in_ports[0],
        )
    jack_client.connect(
        audio_out_ports[1],
        audio_in_ports[1],
        )
    jack_client.connect(
        midi_out_ports[0],
        midi_in_ports[0],
        )

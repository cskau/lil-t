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

    return resp


  def add_plugin(self, plugin_uri, number=0):
    self.send_command('add {} {}'.format(plugin_uri, number))


  def remove_plugin(self, number):
    self.send_command('remove {}'.format(number))


  def get_presets(self, URI):
    self.send_command('preset_show {}'.format(URI))


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
  classes = [str(c) for c in port.get_classes()]
  if ('http://lv2plug.in/ns/lv2core#InputPort' in classes
      and 'http://lv2plug.in/ns/ext/atom#AtomPort' in classes):
    return True
  return False


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


def connect_audio_midi(jack_client):
  # Connect A2J Teensy MIDI output to all plugin MIDI inputs
  teensy_midi_outs = jack_client.get_ports(
      'Teensy',
      is_midi=True,
      is_output=True,
      )
  plugins_midi_ins = jack_client.get_ports(
      'effect_',
      is_midi=True,
      is_input=True,
      )

  if len(teensy_midi_outs) == 1 and plugins_midi_ins:
    for midi_in in plugins_midi_ins:
      try:
        jack_client.connect(teensy_midi_outs[0], midi_in)
      except jack.JackError as e:
        logger.warning(e)
  else:
    logger.error(
        'Found wrong amount of MIDI ports: %s outs, %s ins',
        len(teensy_midi_outs),
        len(plugins_midi_ins),
        )

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

  if len(plugins_audio_outs) >= 1 and len(system_audio_ins) >= 2:
    for plugins_audio_out in plugins_audio_outs:
      system_audio_in = (
          system_audio_ins[0]
          if 'left' in plugins_audio_out.name else
          system_audio_ins[1]
          )

      try:
        jack_client.connect(plugins_audio_out, system_audio_in)
      except jack.JackError as e:
        logger.warning(e)
  else:
    logger.error(
        'Found wrong amount of audio ports: %s outs, %s ins',
        len(plugins_audio_outs),
        len(system_audio_ins),
        )

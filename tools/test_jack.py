#!/usr/bin/env python

from __future__ import print_function

import argparse
from time import sleep

import numpy

import jack


def test_jack(port_index=2):
  print('Creating JACK client..')
  my_test_client = jack.Client(
      'my_test_client',
      no_start_server=False,
      servername=None)

  print('Activating..')
  my_test_client.activate()

  print('Ports:')
  ports = my_test_client.get_ports(
      name_pattern='',
      is_audio=False,
      is_midi=False,
      is_input=False,
      is_output=False,
      is_physical=False,
      can_monitor=False,
      is_terminal=False)
  for port in ports:
    print('  {}'.format(port))

  print('Transport state:')
  transport_state, transport_position = my_test_client.transport_query()
  print('  {}'.format(transport_state))
  print('  {}'.format(transport_position))

  if transport_state != jack.ROLLING:
    my_test_client.transport_start()
  
  port = ports[port_index]

  connections = my_test_client.get_all_connections(port=port)
  print(connections)

  my_in_port = my_test_client.inports.register(
      shortname='my_in',
      is_terminal=False,
      is_physical=False)
  print(my_in_port)

  my_out_port = my_test_client.outports.register(
      shortname='my_out',
      is_terminal=False,
      is_physical=False)
  print(my_out_port)

  cpu_load = my_test_client.cpu_load()
  print(cpu_load)
  
  sleep(10)

  # my_test_client.transport_stop()

  my_test_client.deactivate()

  my_test_client.close()


if __name__ == '__main__':
  test_jack()

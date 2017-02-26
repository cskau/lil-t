#!/usr/bin/env python

from __future__ import print_function

import argparse
from time import sleep

import mido


def print_diagnostics():
  input_names = mido.get_input_names()
  ioport_names = mido.get_ioport_names()
  output_names = mido.get_output_names()

  print('MIDI input ports:')
  for i, ins in enumerate(input_names):
    print('  {} {}'.format(i, ins))

  print('MIDI I/O ports:')
  for i, ios in enumerate(input_names):
    print('  {} {}'.format(i, ios))

  print('MIDI output ports:')
  for i, outs in enumerate(input_names):
    print('  {} {}'.format(i, outs))


def send_keys(note=60, velocity=100, bpm=60, output_index=0):
  output_names = mido.get_output_names()
  output_name = output_names[output_index]

  print('Opening port for output: {}'.format(output_name))

  output = mido.open_output(output_name)

  print('Sending MIDI note {} with velocity {} at {} BPM'.format(note, velocity, bpm))

  try:
    while True:
      output.send(mido.Message('note_on', note=note, velocity=velocity))
      sleep(60.0 / bpm / 2.0) # seconds
      output.send(mido.Message('note_off', note=note))
      sleep(60.0 / bpm / 2.0) # seconds
  except KeyboardInterrupt:
    output.send(mido.Message('note_off', note=note))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='')
  parser.add_argument('-d', '--diagnostics', action='store_true', help='')
  parser.add_argument('-o', '--output', default=0, type=int, nargs='?', help='')
  parser.add_argument('-n', '--note', default=60, type=int, nargs='?', help='')
  parser.add_argument('-v', '--velocity', default=60, type=int, nargs='?', help='')
  parser.add_argument('-b', '--bpm', default=60, type=int, nargs='?', help='')
  args = parser.parse_args()

  diagnostics = args.diagnostics
  output_index = args.output
  note = args.note
  velocity = args.velocity
  bpm = args.bpm

  if diagnostics:
    print_diagnostics()

  send_keys(note, velocity, bpm, output_index)

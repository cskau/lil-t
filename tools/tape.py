#!/usr/bin/env python
# -*- encoding: utf-8  -*-

from __future__ import print_function

import logging
import struct
import wave

try:
  from StringIO import StringIO # Python 2
except Exception as e:
  from io import StringIO # Python 3

import jack

import numpy


logger = logging.getLogger(__name__)


@jack.set_error_function
def error(msg):
  logger.error('Error: %s', msg)


@jack.set_info_function
def info(msg):
  logger.info('Info: %s', msg)


class Tape:

  def __init__(self):
    self.client = jack.Client('tape')

    if self.client.status.server_started:
      logger.info('JACK server was started')
    else:
      logger.info('JACK server was already running')

    if self.client.status.name_not_unique:
      logger.warning('Unique client name generated: %s', self.client.name)

    self.client.set_xrun_callback(self.xrun)
    self.client.set_process_callback(self.process)

    self.blocksize = self.client.blocksize
    self.samplerate = self.client.samplerate

    self.tracks = []

    self.buffer_size = 4 * self.blocksize
    self.quiet = '\x00' * self.buffer_size

    time_t = 0
    self.record = False
    self.play = False
    self.active_track = 0

    self.client.activate()

    self.tracks.append(
        self.create_track(self.client)
        )


  def xrun(self, delay):
    logger.error('xrun: running %s ms behind', delay)


  def create_track(self, client):
    track_n = len(self.tracks)
    channel_left = StringIO.StringIO()
    channel_right = StringIO.StringIO()
    # Stereo in
    in_left = client.inports.register('track{}_left_in'.format(track_n))
    in_right = client.inports.register('track{}_right_in'.format(track_n))
    # Stereo out
    out_left = client.outports.register('track{}_left_out'.format(track_n))
    out_right = client.outports.register('track{}_right_out'.format(track_n))
    # Connect
    client.connect('effect_0:left_out', 'tape:track{}_left_in'.format(track_n))
    client.connect('effect_0:right_out', 'tape:track{}_right_in'.format(track_n))
    client.connect('tape:track{}_left_out'.format(track_n), 'system:playback_1')
    client.connect('tape:track{}_right_out'.format(track_n), 'system:playback_2')
    return (in_left, in_right, channel_left, channel_right, out_left, out_right)


  def process(self, frames):
    if self.record:
      if len(self.tracks) > self.active_track:
        in1, in2, channel1, channel2, out1, out2 = self.tracks[self.active_track]
        channel1.write(in1.get_buffer())
        channel2.write(in2.get_buffer())

    for track in self.tracks:
      in1, in2, channel1, channel2, out1, out2 = track
      data1 = channel1.read(self.buffer_size)
      data2 = channel2.read(self.buffer_size)

      if self.play:
        if len(data1) == self.buffer_size:
          out1.get_buffer()[:] = data1
          out2.get_buffer()[:] = data2
        else:
          channel1.seek(0)
          channel2.seek(0)
          logger.debug('loop')

      if not (self.play or self.record):
        out1.get_buffer()[:] = self.quiet
        out2.get_buffer()[:] = self.quiet


  def set_recording(self, is_recording):
    self.record = is_recording


  def set_playing(self, is_playing):
    self.play = is_playing


  def seek(self, time_sec):
    for in1, in2, channel1, channel2, out1, out2 in self.tracks:
      channel1.seek(time_sec * self.samplerate)
      channel2.seek(time_sec * self.samplerate)
    logger.info('Seeked to {}s'.format(time_sec))


  def set_track(self, track_n):
    self.active_track = track_n
    if self.active_track >= len(self.tracks):
      self.tracks.append(self.create_track(self.client))
    logger.info('Switched to track {}'.format(self.active_track))


  def clear_tape(self):
    for in1, in2, channel1, channel2, out1, out2 in self.tracks:
      channel1.truncate(0)
      channel2.truncate(0)
    logger.info('Tape cleared')


  def halt(self):
    self.play = False
    self.record = False
    logger.info('stop')

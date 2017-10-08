#!/usr/bin/env python

import os
import time

import pygame


# Framebuffer drivers by preference, fall back on x11 for Xvfb:
FB_DRIVERS = ['fbcon', 'directfb', 'svgalib', 'x11']


class FramebufferUI:
  screen = None
  clock = None

  def init_framebuffer_display(self, fb_drivers=FB_DRIVERS):
    if os.getenv("DISPLAY"):
      print('Running on X display {}'.format(os.getenv("DISPLAY")))

    driver_succeeded = False
    for driver in fb_drivers:
      if not os.getenv('SDL_VIDEODRIVER'):
        os.putenv('SDL_VIDEODRIVER', driver)

      try:
        pygame.display.init()
      except pygame.error as e:
        print('{} driver failed.'.format(driver))
        continue

      print('{} driver succeeded!'.format(driver))
      driver_succeeded = True
      break

    if not driver_succeeded:
      raise Exception('All drivers failed!')


  def __init__(self):
    self.init_framebuffer_display()
    pygame.font.init()

    self.screen = pygame.display.set_mode(
        (pygame.display.Info().current_w, pygame.display.Info().current_h),
        pygame.FULLSCREEN)

    pygame.mouse.set_visible(0)

    self.clock = pygame.time.Clock()

    self.clear()


  def __del__(self):
    None


  def clear(self, color=(0, 0, 0)):
    self.screen.fill(color)
    pygame.display.flip()


  def run_loop(self, event_callback, draw_callback, target_framerate=30):
    running = True
    while running:
      # wait some amount of time for target framerate
      self.clock.tick(target_framerate)

      for event in pygame.event.get():
        event_callback(event)
        if event.type == pygame.QUIT:
          running = False
          pygame.quit()
          break
      if not running:
        break

      draw_callback()

      pygame.display.flip()


#
if __name__ == '__main__':
  # For testing
  fbui = FramebufferUI()
  fbui.clear((0, 0, 255))
  time.sleep(10)

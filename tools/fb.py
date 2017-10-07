#!/usr/bin/env python

import os
import time

import pygame


# Framebuffer drivers by preference, fall back on x11 for Xvfb:
FB_DRIVERS = ['fbcon', 'directfb', 'svgalib', 'x11']


class FramebufferUI:
  screen = None

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

    self.screen.fill((0, 0, 0))
    pygame.display.flip()


  def __del__(self):
    None


  def listen(self, handler):
    while True:
      event = pygame.event.wait()
      handler(event)
      if event.type == pygame.QUIT:
        pygame.quit()
        break


  def fill(self, color):
    self.screen.fill(color)
    pygame.display.flip()


#
def main():
  fbui = FramebufferUI()
  fbui.fill((0, 0, 255))
  time.sleep(10)


#
if __name__ == '__main__':
  main()

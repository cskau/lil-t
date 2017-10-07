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

    os.putenv('SDL_NOMOUSE', 1)


  def __init__(self):
    self.init_framebuffer_display()
    pygame.mouse.set_visible(0)
    pygame.font.init()
    self.screen = pygame.display.set_mode(
        (pygame.display.Info().current_w, pygame.display.Info().current_h),
        pygame.FULLSCREEN)
    self.screen.fill((0, 0, 0))
    pygame.display.update()


  def __del__(self):
    None


  def test(self):
    self.screen.fill((255, 0, 0))
    pygame.display.update()


#
def main():
  fbui = FramebufferUI()
  fbui.test()
  time.sleep(10)


#
if __name__ == '__main__':
  main()

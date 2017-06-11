#!/usr/bin/env python

from __future__ import print_function

import argparse
import logging

from Tkinter import *
import Image
import ImageTk


WIDTH = 128
HEIGHT = 160


logging.basicConfig()
logger = logging.getLogger(__name__)



class LilTKApp:

  def __init__(self, root, width=WIDTH, height=HEIGHT, scale=1):
    # self.root = Tk()
    self.root = root

    self.root.wm_title('Display emulator')

    # Set window to fullscreen mode.
    # self.root.attributes("-fullscreen", True)

    # Set explicite window size.
    self.root.geometry("{}x{}".format(width, height))

    # Remove window border
    # self.root.overrideredirect(1)

    self.frame = Frame(self.root)
    self.frame.pack(fill=BOTH, expand=YES)

    my_label = Label(self.frame, text="Hello, world!")
    my_label.pack()



def main():
  root = Tk()

  app = LilTKApp(root)

  root.mainloop()


if __name__ == '__main__':
  main()

#!/usr/bin/env python

from Tkinter import *
import Image
import ImageTk


class DisplayEmulator:

  def __init__(self, width, height, scale=1):
    root = Tk()
    root.wm_title('Display emulator')

    self.root = root
    self.scale = scale
    self.canvas = Canvas(
        self.root,
        bg='pink', # dummy color
        width=width * scale,
        height=height * scale,
        highlightthickness=0,
        )
    self.canvas.pack(
        # fill=BOTH,
        expand=YES,
        )


  def display(self, frame):
    if self.scale != 1:
      frame = frame.resize(
          (frame.width * self.scale, frame.height * self.scale),
          Image.NEAREST,
          )

    # A reference must be kept around otherwise the image won't show.
    self.canvas.photo_image = ImageTk.PhotoImage(frame)
    canvas_image = self.canvas.create_image(
        frame.width / 2,
        frame.height / 2,
        image=self.canvas.photo_image,
        )

    self.root.update()

    return self.canvas

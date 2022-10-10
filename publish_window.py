import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
print('publish_window in')


class pub_screen(object):
    """"""

    def __init__(self, parent, position, phase):
        self.parent = parent
        self.win = tk.Toplevel()
        try:
            self.win.geometry('792x600' + position)
        except tk.TclError:
            self.win.geometry('792x600+500+100')
            print('Not correct position')
        # self.win.attributes('-fullscreen', True)
        self.win.overrideredirect(1)
        def handler(event): return self.on_close()
        self.win.bind('<Escape>', handler)
        img = Image.fromarray(np.uint8((phase % 256)/255*210))
        img.save('./phase.bmp')
        im = ImageTk.PhotoImage(img)
        self.lbl_img = tk.Label(self.win, image=im)
        self.lbl_img.image = im
        self.lbl_img.pack(fill='both', side=tk.TOP, expand=1)
        with open('./new_phase.txt', 'w') as f:
            f.write('new')

    def update_img(self, phase):
        """For controlPhaseSLM and feedbaccker to display the phase"""
        img = Image.fromarray(np.uint8((phase % 256)/255*210))
        img.save('./phase.bmp')
        im = ImageTk.PhotoImage(img)
        self.lbl_img['image'] = im
        self.lbl_img.image = im
        with open('./new_phase.txt', 'w') as f:
            f.write('new')

    def on_close(self):
        self.win.destroy()
        self.parent.pub_win_closed()

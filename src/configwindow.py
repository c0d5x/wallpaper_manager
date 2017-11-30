#!/usr/bin/env python3
"""
draw the configuration window that writes the conf
"""


import sys
import config as cfg
if sys.version_info < (3, 0):
    # Python 2
    import Tkinter as tk
    # from tkFileDialog import askopenfilename as filedialog    # pylint: disable=import-error
    import tkFileDialog as filedialog
else:
    # Python 3
    import tkinter as tk
    from tkinter import filedialog as filedialog


# pylint: disable=too-many-ancestors
class ConfigWindow(tk.Frame):
    '''da shit'''

    gallery_size_options = {"10": 10, "20": 20, "50": 50, "100": 100}

    def __init__(self, master=None):
        if sys.version_info < (3, 0):
            # Python 2
            tk.Frame.__init__(self)
        else:
            # Python 3
            super().__init__(master)

        self.pack()
        self.master.title("Wallpaper Configuration")
        self.master.geometry("660x190")
        self.master.resizable(0, 0)
        self.config = cfg.Config()
        self.create_widgets()

    def create_widgets(self):
        '''da shit'''

        # gallery size, gallery folder, logfile

        self.lbl_title = tk.Label(self, text="Wallpaper App Configuration", font=("Helvetica", 18), padx=10, pady=20)
        self.lbl_title.grid(row=0, columnspan=2)

        self.lbl_gallery_size = tk.Label(self, text="Images to keep locally")
        self.lbl_gallery_size.grid(row=1, sticky=tk.E)

        self.size_def = tk.StringVar(self)
        self.size_def.set("10")

        self.gallery_size_menu = tk.OptionMenu(self, self.size_def, *self.gallery_size_options.keys())
        self.gallery_size_menu.grid(row=1, column=1, sticky=tk.W)

        lbl_gallery_folder = tk.Label(self, text="Folder for your images")
        lbl_gallery_folder.grid(row=2, sticky=tk.E)

        self.entry_gallery_folder = tk.Entry(self)
        self.entry_gallery_folder.insert(0, self.config.wallpaper_dir)
        self.entry_gallery_folder.grid(row=2, column=1)
        self.entry_gallery_folder.config(width=50)
        self.entry_gallery_folder.bind('<Button-1>', self.size_callback)

        self.save = tk.Button(self, text="Save", command=self.save_func, font=("Helvetica", 14), padx=10, pady=20)
        self.save.grid(row=3, columnspan=2, sticky=tk.E)

    def save_func(self):
        '''save changes to config file'''
        # TODO: salvar
        gallery_size = self.size_def.get()
        print(gallery_size)
        folder = self.entry_gallery_folder.get()
        # TODO: check if folder exists
        print(folder)
        # TODO: actually save the settings
        ROOT.destroy()

    def size_callback(self, _):
        ''' set the value for the size'''
        directory = filedialog.askdirectory()
        self.entry_gallery_folder.delete(0, tk.END)
        self.entry_gallery_folder.insert(0, directory)


if __name__ == '__main__':
    ROOT = tk.Tk()
    APP = ConfigWindow(master=ROOT)
    APP.mainloop()

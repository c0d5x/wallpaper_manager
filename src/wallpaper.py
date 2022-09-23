#!/usr/bin/env python3
""" This file downloads wallpapers and sets a random wallpaper every time it runs """

from __future__ import print_function

import os
import sys
import glob
import random
import subprocess


# pylint: disable-msg=W0401
import socwall

# import utils
import config
import desktops

# pylint: disable-msg=C0325

VERBOSE = 1


class Wallpaper:
    """
    Set a nice and random wallpaper for your desktops
    """

    def __init__(self):
        self.conf = config.Config()

    def gallery_maintenance(self):
        """remove used, download new"""
        # self.remove_used()
        existing_images = len(self.get_existing_images())
        if existing_images < self.conf.gallery_size:
            self.download_images()

    def set_wallpaper(self, file_path):
        """GUI set wallpaper"""
        try:
            desktop_env = self.conf.desktop_env
            if desktop_env == "unknown":
                print("Could not detect desktop environment, not setting wallpaper")
            else:
                print("setting: ", file_path)
                desktops.WMS[desktop_env](file_path)
                self.save_used_image(file_path)
        except IndexError:
            print(
                f"Unexpected error setting wallpaper for {desktop_env}:",
                sys.exc_info()[0],
            )

    def download_images(self, path=""):
        """download random images"""
        # TODO: Cycle thru image providers, downloading from each
        if path == "":
            path = self.conf.wallpaper_dir
        return socwall.dl_random_images(path)

    def get_existing_images(self):
        """Return a list of img options to choose from"""
        used_images = []
        with open(self.conf.logfile_name, "r", encoding="utf-8") as logf:
            used_images = logf.readlines()
            used_images = [used.strip("\n") for used in used_images]

        wallpaper_dir = self.conf.wallpaper_dir
        wallpaper_static_dir = self.conf.wallpaper_static_dir
        images = glob.glob(wallpaper_dir + "/*.jpg")
        images += glob.glob(wallpaper_static_dir + "/*.jpg")
        return [img for img in images if img not in used_images]

    def get_random_wallpaper(self):
        """Returns a random image that has not been seen before"""
        options = self.get_existing_images()
        if options:
            return random.choice(options)
        return self.dl_one_image()

    def dl_one_image(self, path=""):
        """Get one image fast"""
        if path == "":
            path = self.conf.wallpaper_dir
        return socwall.dl_one(path)

    def save_used_image(self, image_path):
        """Log an image that has been used"""
        with open(self.conf.logfile_name, "a+", encoding="utf-8") as log:
            log.write(image_path + "\n")

    def remove_oldest(self, num):
        """remove a number of images"""
        fnbytes = subprocess.check_output(
            f"/bin/ls -tr -S {self.conf.wallpaper_dir}|head -n {num}",
            shell=True,
        )
        fnstr = fnbytes.decode()
        for filepath in [fn for fn in fnstr.split("\n") if fn != ""]:
            os.remove(self.conf.wallpaper_dir + "/" + filepath)
            print(f"Removed: {filepath}")

    def remove_used(self):
        """remove used images from disk and log"""
        used_images = []
        with open(self.conf.logfile_name, "r", encoding="utf-8") as logf:
            used_images = logf.readlines()
            used_images = [used.strip("\n") for used in used_images]
        for used_path in used_images:
            try:
                print("removing: ", used_path)
                os.remove(used_path)
            except PermissionError:
                pass
        with open(self.conf.logfile_name, "w", encoding="utf-8") as truncate_log:
            truncate_log.write("")


if __name__ == "__main__":
    WM = Wallpaper()
    WM.remove_used()
    img = WM.get_random_wallpaper()
    WM.set_wallpaper(img)
    WM.gallery_maintenance()

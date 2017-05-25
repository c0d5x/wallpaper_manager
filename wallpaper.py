#!/usr/bin/env python3
''' This file downloads wallpapers and sets a random wallpaper every time it runs '''

from __future__ import print_function

import os
import sys
import glob
import random
import subprocess


# pylint: disable-msg=W0401,W0403
import socwall
import utils

# pylint: disable-msg=C0325

APP_NAME = "wallpaper_manager"
VERBOSE = 1

# TODO: change seen by downloaded, don't download twice
# TODO: OS changes. Set folder for wallpapers and time period


class Wallpaper(object):
    """
    Set a nice and random wallpaper for your desktops
    """

    gallery_size = 200
    home_dir = ""
    config_dir = ""
    wallpaper_dir = ""
    desktop_env = ""
    options = []

    # pool of images to keep locally
    # TODO: image rotation

    def __init__(self):
        self.home_dir = utils.get_home_dir()
        self.config_dir = self.get_config_dir()
        self.wallpaper_dir = self.get_wallpaper_dir()
        self.desktop_env = utils.get_desktop_env()
        '''
        if len(self.get_existing_images()) < self.gallery_size:
            self.dl_one_image()
        '''

    def get_config_dir(self, app_name=APP_NAME):
        ''' Use XDG standard config, THIS METHOD HAS TO BE CALLED AFTER get_home_dir '''
        if "XDG_CONFIG_HOME" in os.environ:
            confighome = os.environ['XDG_CONFIG_HOME']
        elif "APPDATA" in os.environ:  # On Windows
            confighome = os.environ['APPDATA']
        else:
            try:
                from xdg import BaseDirectory
                confighome = BaseDirectory.xdg_config_home
            except ImportError:  # Most likely a Linux/Unix system anyway
                confighome = os.path.join(self.home_dir, ".config")
        configdir = os.path.join(confighome, app_name)
        if not os.path.exists(configdir):
            os.mkdir(configdir)
        return configdir

    def get_wallpaper_dir(self):
        ''' Images are saved in a visible folder for the user '''
        wallpaper_dir = os.path.join(self.home_dir, "Wallpapers")
        if not os.path.exists(wallpaper_dir):
            os.mkdir(wallpaper_dir)
        return wallpaper_dir

    def logfile_name(self):
        ''' Name of log file '''
        ldir = self.config_dir
        if not os.path.exists(ldir):
            os.mkdir(ldir)
        logname = ldir + "/used_images.log"
        if not os.path.exists(logname):
            with open(logname, "a+"):
                pass
        return logname

    def set_wallpaper_random(self):
        '''
TODO: all
        '''
        desktop_env = self.desktop_env
        self.remove_used()
        try:
            if desktop_env == 'unknown':
                print('Could not detect desktop environment, not setting wallpaper')
            else:
                utils.WMS[desktop_env]()
                self.save_used_image()
        except:
            print("Unexpected error setting wallpaper for {}:".format(desktop_env), sys.exc_info()[0])

        # verify we have more images for next time, remove if max
        existing_images = len(self.get_existing_images())
        if existing_images < self.gallery_size:
            self.download_images()
        else:
            self.remove_oldest(int(self.gallery_size * 0.1))  # remove 10% of the images if we have reached the max

    def set_wallpaper(self, file_path):
        '''
        Entry point for the module. This call checks if new images need to be downloaded, and removes the oldest images

        Set the current wallpaper for all platforms
        '''
        desktop_env = self.desktop_env
        self.remove_used()
        try:
            if desktop_env == 'unknown':
                print('Could not detect desktop environment, not setting wallpaper')
            else:
                utils.WMS[desktop_env](file_path)
                self.save_used_image(file_path)
        except:
            print("Unexpected error setting wallpaper for {}:".format(desktop_env), sys.exc_info()[0])

        # verify we have more images for next time, remove if max
        existing_images = len(self.get_existing_images())
        if existing_images < self.gallery_size:
            self.download_images()
        else:
            self.remove_oldest(int(self.gallery_size * 0.1))  # remove 10% of the images if we have reached the max

    def download_images(self, path=''):
        """
        TODO: Cycle thru image providers, downloading from each
        """
        if path == '':
            path = self.wallpaper_dir
        return socwall.dl_random_page(path)

    def get_existing_images(self):
        ''' Return a list of img options to choose from '''
        used_images = list()
        with open(self.logfile_name(), "r") as logf:
            used_images = logf.readlines()
            used_images = [l.strip('\n') for l in used_images]

        wallpaper_dir = self.wallpaper_dir
        images = glob.glob(wallpaper_dir + "/*.jpg")

        return [img for img in images if img not in used_images]

    def get_random_wallpaper(self):
        ''' Returns a random image that has not been seen before '''
        options = self.options
        if len(options) < 1:
            options = self.get_existing_images()
        if len(options) > 0:
            return random.choice(options)
        else:
            return self.dl_one_image()
    #        options = self.get_existing_images()
    #        return random.choice(options)

    def dl_one_image(self, path=''):
        ''' Get one image fast '''
        if path == '':
            path = self.wallpaper_dir
        return socwall.dl_one(path)

    def save_used_image(self, image_path):
        ''' Log an image that has been used '''
        with open(self.logfile_name(), "a+") as log:
            log.write(image_path + "\n")

    def enough_provisioned(self):
        """ check if enough pics are there already """
        return len(self.get_existing_images()) > self.gallery_size

    def remove_oldest(self, num):
        """ remove a number of images """
        # TODO: what to do in windows ?
        fnbytes = subprocess.check_output("/bin/ls -tr {}|head -n {}".format(self.wallpaper_dir, num), shell=True)
        fnstr = fnbytes.decode()
        for filepath in [fn for fn in fnstr.split('\n') if fn != '']:
            os.remove(self.wallpaper_dir + "/" + filepath)
            print("Removed: {}".format(filepath))

    def remove_used(self):
        '''remove used images from disk and log'''
        used_images = []
        with open(self.logfile_name(), "r") as logf:
            used_images = logf.readlines()
            used_images = [l.strip('\n') for l in used_images]
        for used_path in used_images:
            try:
                os.remove(used_path)
            except:
                pass
                # I don't care if the file was not there
        truncate_log = open(self.logfile_name(), "w")
        truncate_log.close()


if __name__ == '__main__':
    WM = Wallpaper()
    WM.set_wallpaper(WM.get_random_wallpaper())

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
# import utils
import config
import desktops

# pylint: disable-msg=C0325

VERBOSE = 1

# TODO: change seen by downloaded, don't download twice
# TODO: OS changes. Set folder for wallpapers and time period


class Wallpaper(object):
    """
    Set a nice and random wallpaper for your desktops
    """

    def __init__(self):
        self.conf = config.Config()
        self.options = self.get_existing_images()

        '''
        if len(self.get_existing_images()) < self.gallery_size:
            self.dl_one_image()
        '''

    def set_wallpaper_random(self):
        '''
TODO: all
        '''
        desktop_env = self.conf.desktop_env
        self.remove_used()
        try:
            if desktop_env == 'unknown':
                print('Could not detect desktop environment, not setting wallpaper')
            else:
                desktops.WMS[desktop_env]()
#                self.save_used_image()
        except:
            print("Unexpected error setting wallpaper for {}:".format(desktop_env), sys.exc_info()[0])

        # verify we have more images for next time, remove if max
        existing_images = len(self.get_existing_images())
        if existing_images < self.conf.gallery_size:
            self.download_images()
        else:
            self.remove_oldest(int(self.conf.gallery_size * 0.1))  # remove 10% of the images if we have reached the max

    def gallery_maintenance(self):
        ''' remove used, download new'''
        self.remove_used()

        existing_images = len(self.get_existing_images())
        if existing_images < self.conf.gallery_size:
            self.download_images()
        else:
            # used images have already been deleted,,, so removing more images here is only necessary for additional
            # rotation
            # self.remove_oldest(int(self.conf.gallery_size * 0.1))  # remove 10% of the images if we have reached the max
            pass

    def set_wallpaper(self, file_path):
        '''
        Entry point for the module. This call checks if new images need to be downloaded, and removes the oldest images

        Set the current wallpaper for all platforms
        '''
        desktop_env = self.conf.desktop_env
        try:
            if desktop_env == 'unknown':
                print('Could not detect desktop environment, not setting wallpaper')
            else:
                desktops.WMS[desktop_env](file_path)
                self.save_used_image(file_path)
        except:
            print("Unexpected error setting wallpaper for {}:".format(desktop_env), sys.exc_info()[0])

    def download_images(self, path=''):
        """
        TODO: Cycle thru image providers, downloading from each
        """
        if path == '':
            path = self.conf.wallpaper_dir
        return socwall.dl_random_images(path)

    def get_existing_images(self):
        ''' Return a list of img options to choose from '''
        used_images = list()
        with open(self.conf.logfile_name, "r") as logf:
            used_images = logf.readlines()
            used_images = [l.strip('\n') for l in used_images]

        wallpaper_dir = self.conf.wallpaper_dir
        images = glob.glob(wallpaper_dir + "/*.jpg")

        return [img for img in images if img not in used_images]

    def get_random_wallpaper(self):
        ''' Returns a random image that has not been seen before '''
        options = self.options

        if options:
            return random.choice(options)

        self.gallery_maintenance()
        return self.dl_one_image()

    def dl_one_image(self, path=''):
        ''' Get one image fast '''
        if path == '':
            path = self.conf.wallpaper_dir
        return socwall.dl_one(path)

    def save_used_image(self, image_path):
        ''' Log an image that has been used '''
        with open(self.conf.logfile_name, "a+") as log:
            log.write(image_path + "\n")

    def enough_provisioned(self):
        """ check if enough pics are there already """
        return len(self.get_existing_images()) > self.conf.gallery_size

    def remove_oldest(self, num):
        """ remove a number of images """
        # TODO: what to do in windows ?
        fnbytes = subprocess.check_output("/bin/ls -tr -S {}|head -n {}".format(self.conf.wallpaper_dir, num), shell=True)
        fnstr = fnbytes.decode()
        for filepath in [fn for fn in fnstr.split('\n') if fn != '']:
            os.remove(self.conf.wallpaper_dir + "/" + filepath)
            print("Removed: {}".format(filepath))

    def remove_used(self):
        '''remove used images from disk and log'''
        used_images = []
        with open(self.conf.logfile_name, "r") as logf:
            used_images = logf.readlines()
            used_images = [l.strip('\n') for l in used_images]
        for used_path in used_images:
            try:
                os.remove(used_path)
            except:
                pass
                # I don't care if the file was not there
        truncate_log = open(self.conf.logfile_name, "w")
        truncate_log.close()


if __name__ == '__main__':
    WM = Wallpaper()
    WM.set_wallpaper(WM.get_random_wallpaper())

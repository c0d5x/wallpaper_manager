"""
Deal with configuration file and variables
"""


import os
import desktops
from xdg import BaseDirectory


DEFAULT_GALLERY_SIZE = 20
APP_NAME = "wallpaper"


class Config:
    """deal with configuration"""

    gallery_size = DEFAULT_GALLERY_SIZE
    home_dir = ""
    config_dir = ""
    wallpaper_dir = ""
    wallpaper_static_dir = ""
    desktop_env = ""
    logfile_name = ""

    def __init__(self):
        self.home_dir = self.get_home_dir()
        self.config_dir = self.get_config_dir()
        self.wallpaper_dir = self.get_wallpaper_dir()
        self.wallpaper_static_dir = self.get_wallpaper_static_dir()
        self.desktop_env = desktops.get_desktop_env()
        self.logfile_name = self.get_logfile_name()

    def get_home_dir(self):
        """ Home dir for all platforms """
        home_dir = os.getenv("USERPROFILE") or os.getenv("HOME")
        if home_dir is not None:
            return os.path.normpath(home_dir)
        else:
            raise KeyError("Neither HOME or USERPROFILE environment variables set.")

    def get_config_dir(self, app_name=APP_NAME):
        """ Use XDG standard config, THIS METHOD HAS TO BE CALLED AFTER get_home_dir """
        if "XDG_CONFIG_HOME" in os.environ:
            confighome = os.environ["XDG_CONFIG_HOME"]
        elif "APPDATA" in os.environ:  # On Windows
            confighome = os.environ["APPDATA"]
        else:
            try:
                confighome = BaseDirectory.xdg_config_home
            except ImportError:  # Most likely a Linux/Unix system anyway
                confighome = os.path.join(self.home_dir, ".config")
        configdir = os.path.join(confighome, app_name)
        if not os.path.exists(configdir):
            os.mkdir(configdir)
        return configdir

    def get_wallpaper_dir(self):
        """ Images are saved in a visible folder for the user """
        wallpaper_dir = os.path.join(self.home_dir, "Wallpapers")
        if not os.path.exists(wallpaper_dir):
            os.mkdir(wallpaper_dir)
        return wallpaper_dir

    def get_wallpaper_static_dir(self):
        """ Images are saved in a visible folder for the user AND NEVER DELETED """
        wallpaper_dir = os.path.join(self.home_dir, "Static-Wallpapers")
        if not os.path.exists(wallpaper_dir):
            os.mkdir(wallpaper_dir)
        return wallpaper_dir

    def get_logfile_name(self):
        """ Name of log file """
        ldir = self.config_dir
        if not os.path.exists(ldir):
            os.mkdir(ldir)
        logname = ldir + "/used_images.log"
        if not os.path.exists(logname):
            with open(logname, "a+"):
                pass
        return logname

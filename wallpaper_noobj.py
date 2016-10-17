#!/usr/bin/env python3
''' This file downloads wallpapers and sets a random wallpaper every time it runs '''


import subprocess
import os
import sys

import socwall
import glob
import random


APP_NAME = "wallpaper_manager"
VERBOSE = 1


def set_wallpaper_gnomefamily(file_path):
    ''' gnome, unity, cinnamon, awesome-gnome '''
    uri = "'file://%s'" % file_path
    try:
        args = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri]
        subprocess.Popen(args)
    except subprocess.CalledProcessError:
        args = ["dconf", "write", "/org/gnome/desktop/background/picture-uri", uri]
        subprocess.Popen(args)


def set_wallpaper_gnome2(file_path):
    ''' gnome2 uses gconftool-2 '''
    # From https://bugs.launchpad.net/variety/+bug/1033918
    try:
        args = ["gconftool-2", "-t", "string", "--set", "/desktop/gnome/background/picture_filename", '"%s"' % file_path]
        subprocess.Popen(args)
    except subprocess.CalledProcessError:
        set_wallpaper_gnomefamily(file_path)


def set_wallpaper_mate(file_path):
    ''' mate wm '''
    try:  # MATE >= 1.6
        # info from http://wiki.mate-desktop.org/docs:gsettings
        args = ["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % file_path]
        subprocess.Popen(args)
    except subprocess.CalledProcessError:
        # From https://bugs.launchpad.net/variety/+bug/1033918
        args = ["mateconftool-2", "-t", "string", "--set", "/desktop/mate/background/picture_filename", '"%s"' % file_path]
        subprocess.Popen(args)


def set_wallpapper_razor_qt(file_path):  # TODO: implement reload of desktop when possible
    ''' razor qt, not tested '''
    import configparser
    desktop_conf = configparser.ConfigParser()
    desktop_conf_file = os.path.join(get_config_dir("razor"), "desktop.conf")
    if os.path.isfile(desktop_conf_file):
        config_option = r"screens\1\desktops\1\wallpaper"
    else:
        desktop_conf_file = os.path.join(get_home_dir(), ".razor/desktop.conf")
        config_option = r"desktops\1\wallpaper"
    desktop_conf.read(os.path.join(desktop_conf_file))
    if desktop_conf.has_option("razor", config_option):  # only replacing a value
        desktop_conf.set("razor", config_option, file_path)
        import codecs
        with codecs.open(desktop_conf_file, "w", encoding="utf-8", errors="replace") as fhandler:
            desktop_conf.write(fhandler)


def set_wallpaper_xfce4(file_path):
    ''' not tested '''
    # From http://www.commandlinefu.com/commands/view/2055/change-wallpaper-for-xfce4-4.6.0
    args = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-path", "-s", file_path]
    subprocess.Popen(args)
    args = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-style", "-s", "3"]
    subprocess.Popen(args)
    args = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-show", "-s", "true"]
    subprocess.Popen(args)
    args = ["xfdesktop", "--reload"]
    subprocess.Popen(args)


def set_wallpaper_windows(file_path):
    ''' not tested '''
    # From http://stackoverflow.com/questions/1977694/change-desktop-background
    import ctypes
    ctypes.windll.user32.SystemParametersInfoA(20, 0, file_path, 0)


def set_wallpaper_feh(file_path):
    ''' not tested '''
    args = ["feh", "--bg-center", file_path]
    subprocess.Popen(args)


def set_wallpaper(file_path):
    ''' Set the current wallpaper for all platforms'''
    desktop_env = get_desktop_env()
    args = list()
    try:
        if desktop_env in ["gnome", "unity", "cinnamon", "awesome-gnome"]:
            set_wallpaper_gnomefamily(file_path)
        elif desktop_env == "mac":  # Not tested since I do not have a mac
            # From http://stackoverflow.com/questions/431205/how-can-i-programatically-change-the-background-in-mac-os-x
            cmd = "osascript -e 'tell application \"Finder\" to set desktop picture to POSIX file \"%s\"'" % file_path
            subprocess.Popen(cmd, shell=True)
        elif desktop_env == "windows":  # Not tested since I do not run this on Windows
            set_wallpaper_windows(file_path)
        elif desktop_env == "mate":
            set_wallpaper_mate(file_path)
        elif desktop_env == "gnome2":  # Not tested
            set_wallpaper_gnome2(file_path)
        elif desktop_env in ["kde3", "trinity"]:
            # From http://ubuntuforums.org/archive/index.php/t-803417.html
            args = 'dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % file_path
            subprocess.Popen(args, shell=True)
        elif desktop_env == "xfce4":
            set_wallpaper_xfce4(file_path)
        elif desktop_env == "razor-qt":
            set_wallpapper_razor_qt(file_path)
        elif desktop_env in ["fluxbox", "jwm", "openbox", "afterstep"]:
            args = ["fbsetbg", file_path]
            subprocess.Popen(args)
        elif desktop_env == "icewm":
            # command found at http://urukrama.wordpress.com/2007/12/05/desktop-backgrounds-in-window-managers/
            args = ["icewmbg", file_path]
            subprocess.Popen(args)
        elif desktop_env == "blackbox":
            # command found at http://blackboxwm.sourceforge.net/BlackboxDocumentation/BlackboxBackground
            args = ["bsetbg", "-full", file_path]
            subprocess.Popen(args)
        elif desktop_env == "lxde":
            args = "pcmanfm --set-wallpaper %s --wallpaper-mode=scaled" % file_path
            subprocess.Popen(args, shell=True)
        elif desktop_env == "windowmaker":
            # From http://www.commandlinefu.com/commands/view/3857/set-wallpaper-on-windowmaker-in-one-line
            args = "wmsetbg -s -u %s" % file_path
            subprocess.Popen(args, shell=True)
        else:
            set_wallpaper_feh(file_path)
    except:
        set_wallpaper_feh(file_path)

    log_image(file_path)
    if get_num_existing() - get_num_seen() < 10:
        download_images()


def download_images():
    socwall.dl_random_page()


def get_wallpaper_dir():
    ''' Images are saved in a visible folder for the user '''
    wallpaper_dir = os.path.join(get_home_dir(), "Wallpapers")
    if not os.path.exists(wallpaper_dir):
        os.mkdir(wallpaper_dir)
    return wallpaper_dir


def get_config_dir(app_name=APP_NAME):
    ''' Use XDG standard config '''
    if "XDG_CONFIG_HOME" in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME']
    elif "APPDATA" in os.environ:  # On Windows
        confighome = os.environ['APPDATA']
    else:
        try:
            from xdg import BaseDirectory
            confighome = BaseDirectory.xdg_config_home
        except ImportError:  # Most likely a Linux/Unix system anyway
            confighome = os.path.join(get_home_dir(), ".config")
    configdir = os.path.join(confighome, app_name)
    if not os.path.exists(configdir):
        os.mkdir(configdir)
    return configdir


def get_home_dir():
    ''' Home dir for all platforms '''
    if sys.platform == "cygwin":
        home_dir = os.getenv('HOME')
    else:
        home_dir = os.getenv('USERPROFILE') or os.getenv('HOME')
    if home_dir is not None:
        return os.path.normpath(home_dir)
    else:
        raise KeyError("Neither USERPROFILE or HOME environment variables set.")


# def get_num_seen():
#     ''' number of seen images '''
#     seen_images = list()
#     with open(log_name(), "r") as logf:
#         seen_images = logf.readlines()
#         seen_images = [l.strip('\n') for l in seen_images]
#     return len(seen_images)
#
#
# def get_num_existing():
#     ''' get number of existing images '''
#     wallpaper_dir = get_wallpaper_dir()
#     images = glob.glob(wallpaper_dir + "/*.jpg")
#     return len(images)


def get_img_options():
    ''' Return a list of img options to choose from '''
    seen_images = list()
    with open(log_name(), "r") as logf:
        seen_images = logf.readlines()
        seen_images = [l.strip('\n') for l in seen_images]

    wallpaper_dir = get_wallpaper_dir()
    images = glob.glob(wallpaper_dir + "/*.jpg")

    return [img for img in images if img not in seen_images]


def get_random_wallpaper():
    ''' Returns a random image that has not been seen before '''
    options = get_img_options()
    if len(options) > 1:
        return random.choice(options)
    else:
        dl_one_image()
        options = get_img_options()
        return random.choice(options)


def dl_one_image():
    ''' Get one image fast '''
    socwall.dl_one()


def get_desktop_env():
    ''' Desktop environment for all platforms '''
    desktop_env = "unknown"
    if sys.platform in ["win32", "cygwin"]:
        desktop_env = "windows"
    elif sys.platform == "darwin":
        desktop_env = "mac"
    else:  # linux/unix
        desktop_session = os.environ.get('DESKTOP_SESSION')
        if desktop_session is not None:  # easier to match if we doesn't have to deal with caracter cases
            desktop_session = desktop_session.lower()
            if desktop_session in ["gnome", "unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox",
                                   "blackbox", "openbox", "icewm", "jwm", "afterstep", "trinity", "kde",
                                   "awesome", "awesome-gnome", "i3", ]:
                desktop_env = desktop_session
            # Special cases #
            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
            # There is no guarantee that they will not do the same with the other desktop environments.
            elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                desktop_env = "xfce4"
            elif desktop_session.startswith("ubuntu"):
                desktop_env = "unity"
            elif desktop_session.startswith("lubuntu"):
                desktop_env = "lxde"
            elif desktop_session.startswith("kubuntu"):
                desktop_env = "kde"
            elif desktop_session.startswith("razor"):  # e.g. razorkwin
                desktop_env = "razor-qt"
            elif desktop_session.startswith("wmaker"):  # e.g. wmaker-common
                desktop_env = "windowmaker"
        elif os.environ.get('KDE_FULL_SESSION') == 'true':
            desktop_env = "kde"
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            if "deprecated" not in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                desktop_env = "gnome2"
        elif is_running("xfce-mcs-manage"):
            desktop_env = "xfce4"
        elif is_running("ksmserver"):
            desktop_env = "kde"
    return desktop_env


def log_name():
    ''' Name of log file '''
    ldir = get_config_dir()
    if not os.path.exists(ldir):
        os.mkdir(ldir)
    logname = ldir + "/seenimages.log"
    if not os.path.exists(logname):
        with open(logname, "a+"):
            pass
    return logname


def log_image(image_path):
    ''' Log an image that has been used '''
    with open(log_name(), "a+") as log:
        log.write(image_path + "\n")


def is_running(process):
    ''' True if process is running, string matching '''
    import re
    try:  # Linux/Unix
        sout = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
    except:  # Windows
        sout = subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE)
    for proc in sout.stdout:
        if re.search(process, str(proc)):
            return True
    return False


if __name__ == '__main__':
    set_wallpaper(get_random_wallpaper())
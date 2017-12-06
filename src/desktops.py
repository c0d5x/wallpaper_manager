'''deal with desktops'''

import os
import sys
import subprocess
import utils


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
    try:
        args = ["feh", "--bg-center", file_path]
        subprocess.Popen(args)
    except:
        print("Error running feh, please check `feh` is in your $PATH")


def set_wallpaper_osx(file_path):
    """ osx all dirs """
    try:
        from appscript import app
        from appscript import mactypes
        from appscript.reference import CommandError
    except:
        raise

    try:
        sys_events = app('System Events')
        for desktop in sys_events.desktops.get():
            desktop.picture.set(mactypes.File(file_path))
    except CommandError as exception:
        print(exception.errormessage)


def set_wallpaper_kde(file_path):
    """ kde family"""
    # From http://ubuntuforums.org/archive/index.php/t-803417.html
    args = 'dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % file_path
    subprocess.Popen(args, shell=True)


def set_wallpaper_fluxbox(file_path):
    """ fluxbox family"""
    args = ["fbsetbg", file_path]
    subprocess.Popen(args)


def set_wallpaper_icewm(file_path):
    """icewm fam"""
    args = ["icewmbg", file_path]
    subprocess.Popen(args)


def set_wallpaper_blackbox(file_path):
    """blackbox family"""
    args = ["bsetbg", "-full", file_path]
    subprocess.Popen(args)


def set_wallpaper_lxde(file_path):
    """lxde family"""
    args = "pcmanfm --set-wallpaper %s --wallpaper-mode=scaled" % file_path
    subprocess.Popen(args, shell=True)


def set_wallpaper_windowmaker(file_path):
    """windowmaker family"""
    args = "wmsetbg -s -u %s" % file_path
    subprocess.Popen(args, shell=True)


def get_desktop_env():
    ''' Desktop environment for all platforms '''
    desktop_env = "unknown"

    if sys.platform in ["win32", "cygwin"]:
        desktop_env = "windows"
    elif sys.platform == "darwin":
        desktop_env = "mac"
    elif sys.platform.startswith("linux"):
        desktop_env = get_desktop_env_linux()
    return desktop_env


def get_desktop_env_linux():
    '''penguin'''
    desktop_env = 'unknown'
    desktop_session = os.environ.get('DESKTOP_SESSION')
    if desktop_session is not None:  # easier to match if we doesn't have to deal with caracter cases
        desktop_env = get_desktop_env_linux_session(desktop_session)
    elif os.environ.get('KDE_FULL_SESSION') == 'true':
        desktop_env = "kde"
    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        if "deprecated" not in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            desktop_env = "gnome2"
        else:
            desktop_env = "gnome3"
    elif utils.is_running("xfce-mcs-manage"):
        desktop_env = "xfce4"
    elif utils.is_running("ksmserver"):
        desktop_env = "kde"
    return desktop_env


def get_desktop_env_linux_session(desktop_session):
    '''parse desktop session'''
    desktop_env = 'unknown'
    desktop_session = desktop_session.lower()
    if desktop_session.startswith("i3"):
        desktop_env = "i3"
    elif desktop_session in ["gnome", "unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox",
                             "blackbox", "openbox", "icewm", "jwm", "afterstep", "trinity", "kde",
                             "awesome", "awesome-gnome"]:
        desktop_env = desktop_session
    elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
        desktop_env = "xfce4"
    elif desktop_session.startswith("ubuntu"):
        desktop_env = "unity"
        # TODO: ubuntu will move to gnome3 soon
    elif desktop_session.startswith("gnome3"):
        desktop_env = "gnome3"
    elif desktop_session.startswith("lubuntu"):
        desktop_env = "lxde"
    elif desktop_session.startswith("kubuntu"):
        desktop_env = "kde"
    elif desktop_session.startswith("wmaker"):  # e.g. wmaker-common
        desktop_env = "windowmaker"
    return desktop_env


def ignore_wallpaper(image_path=''):
    ''' for unknown desktop environments, we simply ignore the call'''
    pass


WMS = {"unknown": ignore_wallpaper,
       "gnome": set_wallpaper_gnomefamily,
       "gnome2": set_wallpaper_gnome2,
       "gnome3": set_wallpaper_gnomefamily,
       "unity": set_wallpaper_gnomefamily,
       "cinnamon": set_wallpaper_gnomefamily,
       "awesome-gnome": set_wallpaper_gnomefamily,
       "mac": set_wallpaper_osx,
       "mate": set_wallpaper_mate,
       "xfce4": set_wallpaper_xfce4,
       "windows": set_wallpaper_windows,
       "feh": set_wallpaper_feh,
       "kde3": set_wallpaper_kde,
       "trinity": set_wallpaper_kde,
       "blackbox": set_wallpaper_blackbox,
       "fluxbox": set_wallpaper_fluxbox,
       "jwm": set_wallpaper_fluxbox,
       "afterstep": set_wallpaper_fluxbox,
       "lxde": set_wallpaper_lxde,
       "windowmaker": set_wallpaper_windowmaker,
       "i3": set_wallpaper_gnomefamily}

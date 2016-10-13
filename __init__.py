import os
import wallpaper_manager as wm

IMG_DIR = wm.get_config_dir()
if not os.path.isdir(IMG_DIR):
    os.mkdir(IMG_DIR)

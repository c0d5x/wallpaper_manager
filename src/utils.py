"""
Utils
"""

import subprocess


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

"""
Utils
"""

import subprocess
import re


def is_running(process):
    """True if process is running, string matching"""
    try:  # Linux/Unix
        with subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE) as sout:
            for proc in sout.stdout:
                if re.search(process, str(proc)):
                    return True
    except subprocess.SubprocessError():  # Windows
        with subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE) as sout:
            for proc in sout.stdout:
                if re.search(process, str(proc)):
                    return True
    return False

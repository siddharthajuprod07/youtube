import os
import os.path
import re
import sys
import logging


def setup_python_path():
    # Exclude folder beneath other apps, Fix bug for rest_handler.py
    ta_name = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
    pattern = re.compile(r"[\\/]etc[\\/]apps[\\/][^\\/]+[\\/]bin[\\/]?$")
    new_paths = [path for path in sys.path if not pattern.search(path) or ta_name in path]
    new_paths.insert(0, os.path.dirname(__file__))
    sys.path = new_paths

    bindir = os.path.dirname(os.path.abspath(__file__))
    # We sort the precedence in a decending order since sys.path.insert(0, ...)
    # do the reversing.
    # Insert library folder
    for folder in ['3rdparty']:
        sharedpath = os.path.join(bindir, folder)
        sys.path.insert(0, sharedpath)

setup_python_path()
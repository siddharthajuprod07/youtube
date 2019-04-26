import os
import gc
import sys


__author__ = 'bchoi'


def disable_stdout_buffering():
    # Disable stdout buffering
    os.environ['PYTHONUNBUFFERED'] = '1'
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    gc.garbage.append(sys.stdout)

def get_app_path():
    path = os.path.dirname(__file__)
    marker = os.path.join(os.path.sep, 'etc', 'apps')
    start = path.rfind(marker)
    if start == -1:
        start = 0
    end = path.find('bin', start)
    if end != -1: 
        # strip the tail
        end = end - 1
        path = path[:end]
    return path

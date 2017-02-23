import os
import sys
import time

from nrepl import NAME


def console(msg, _name=None, _color=None):
    if _color:
        sys.stdout.write('\033[%sm' % _color)

    print('[{}]: {}'.format(_name or NAME, msg))

    if _color:
        sys.stdout.write('\033[0;0m')


def get_ts():
    return int(time.time())


def traverse_dir(dirpath, callback):
    for root, dirs, files in os.walk(dirpath, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            callback(filepath)

        for dir_ in dirs:
            dirpath = os.path.join(root, dir_)
            traverse_dir(dirpath, callback)

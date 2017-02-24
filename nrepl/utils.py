import os
import sys
import time
from datetime import datetime

from nrepl import NAME


def get_fmt_dt():
    return datetime.now().strftime('%Y-%m-%d %H:%I:%S')


def console(msg, _name=None, _color=None, _with_time=False):
    if _color:
        sys.stdout.write('\033[%sm' % _color)

    if _with_time:
        sys.stdout.write('[%s]' % get_fmt_dt())

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

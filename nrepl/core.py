from __future__ import print_function

import os
import sys
import time
import socket
import argparse
import subprocess

# compatibility support

PY2 = sys.version_info[0] == 2

if not PY2:
    text_type = str
    string_types = (str,)
    unichr = chr

    from urllib.parse import urlparse

else:
    text_type = unicode
    string_types = (str, unicode)
    unichr = chr

    from urlparse import urlparse


DEFAULT_nREPL_URI = "nrepl://localhost:31415"


_read_byte = lambda s: s.read(1)


def _write_data(fd, data):
    write = lambda x: fd.write(x)
    if isinstance(data, string_types):
        write(str(len(data)))
        write(":")
        write(data)
    elif isinstance(data, int):
        write("i")
        write(str(data))
        write("e")
    elif isinstance(data, (tuple, list)):
        write("l")
        for each in data:
            _write_data(fd, each)
        write("e")
    elif isinstance(data, dict):
        write("d")
        for k, v in data.items():
            _write_data(fd, k)
            _write_data(fd, v)
        write("e")
    fd.flush()


class BencodeIO(object):

    def __init__(self, fd, on_close=None):
        self.fd = fd
        self.on_close = on_close

    def write(self, data):
        return _write_data(self.fd, data)


def nrepl_connect(uri):
    uri = urlparse(uri)
    _socket = socket.create_connection(uri.netloc.split(":"))
    _fd = _socket.makefile('rw')
    return BencodeIO(_fd, on_close=_socket.close)


def get_ns_declare(fd):
    while True:
        line = fd.readline()
        if line.strip().startswith('(ns'):
            return line


def get_ns(filename):
    with open(filename, 'r') as infile:
        ns_declare = get_ns_declare(infile)
        _, ns = ns_declare.split()
        if ns.endswith(')'):
            ns = ns[:-1]
    return ns.strip()


def traverse_dir(dirpath, callback):
    for root, dirs, files in os.walk(dirpath, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            callback(filepath)

        for dir_ in dirs:
            dirpath = os.path.join(root, dir_)
            traverse_dir(dirpath, callback)


class Watcher(object):

    def __init__(self, uri):
        self._mtimes = {}
        self._client = nrepl_connect(uri)

    def trigger_reload(self, filename):
        filename = os.path.realpath(filename)
        print('Detected changes of %s, reloading' % filename)
        ns = get_ns(filename)
        self._client.write({
            'op': 'eval',
            'code': "(require '%s :reload)" % ns,
        })

    def reload_if_updated(self, filename):
        if filename.endswith('.clj'):
            try:
                mtime = os.stat(filename).st_mtime
            except OSError:
                return

            old_time = self._mtimes.get(filename)
            if old_time is None:
                self._mtimes[filename] = mtime
                return

            if mtime > old_time:
                self._mtimes[filename] = mtime
                self.trigger_reload(filename)

    def start(self, dirpath, interval=1):
        while True:
            traverse_dir(dirpath, self.reload_if_updated)
            time.sleep(interval)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default='.')
    parser.add_argument('-u', '--uri', default=DEFAULT_nREPL_URI)
    args = parser.parse_args()

    path = os.path.realpath(args.path)

    watcher = Watcher(args.uri)
    print("Start watching", path)
    watcher.start(path)


if __name__ == '__main__':
    cli()

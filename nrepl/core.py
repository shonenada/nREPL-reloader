from __future__ import print_function

import os
import sys
import time
import errno
import socket
import signal
import argparse
import threading
import subprocess

# compatibility support

NAME = 'nrepl'
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


DEFAULT_nREPL_URI = "nrepl://localhost:59258"


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


def console(msg, _name=None):
    print('[{}]: {}'.format(_name or NAME, msg))


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


def nrepl_connect(uri):
    uri = urlparse(uri)
    _socket = socket.create_connection(uri.netloc.split(":"))
    _fd = _socket.makefile('rw')
    return BencodeIO(_fd, on_close=_socket.close)


def get_ts():
    return int(time.time())


class TimeoutError(Exception):
    pass


class Watcher(object):

    def __init__(self, uri, timeout):
        self._mtimes = {}
        self.uri = uri
        self.timeout = timeout

    def trigger_reload(self, filename):
        filename = os.path.realpath(filename)
        console('Detected changes of %s, reloading' % filename)
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

    def start(self, dirpath, interval=3):
        start_ts = get_ts()
        while True:
            try:
                self._client = nrepl_connect(self.uri)
                break
            except socket.error, e:
                eno, _ = e
                if eno == errno.ECONNREFUSED:
                    ts = get_ts()
                    if (ts - start_ts) > self.timeout:
                        raise TimeoutError('%s (in %ss)' % (e, self.timeout))
                    else:
                        continue
                raise e
            time.sleep(interval)

        console("Started watching %s" % dirpath)

        while True:
            traverse_dir(dirpath, self.reload_if_updated)
            time.sleep(interval)


class Handler(threading.Thread):

    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self._cmd = cmd
        self._process = None

    def run(self):
        cmd = ' '.join(self._cmd)
        self._process = subprocess.Popen(cmd, shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT,
                                         preexec_fn=os.setsid)
        for line in iter(self._process.stdout.readline, b''):
            console(line.rstrip(), _name='lein')

    def stop(self):
        if self._process is not None:
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            self._process = None


def build_sig_handler(proc):
    def sig_handler(signum, frame):
        proc.stop()
        proc.join()
        sys.exit(0)
    return sig_handler


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', choices=['run', 'watch'])
    parser.add_argument('-u', '--uri', default=DEFAULT_nREPL_URI)
    parser.add_argument('-p', '--path', default='.')
    parser.add_argument('-t', '--timeout', type=int, default=60)
    args = parser.parse_args()

    path = os.path.realpath(args.path)

    if args.cmd == 'run':
        h = Handler(['lein', 'run'])
        h.start()

        signal.signal(signal.SIGTERM, build_sig_handler(h))
        signal.signal(signal.SIGINT, build_sig_handler(h))

        time.sleep(5)    # wait for start

        try:
            watcher = Watcher(args.uri, timeout=args.timeout)
            watcher.start(path)
            console("Started watching %s" % path)
        except Exception as e:
            h.stop()
            h.join()
            raise e

    if args.cmd == 'watch':
        watcher = Watcher(args.uri, timeout=args.timeout)
        watcher.start(path)


if __name__ == '__main__':
    cli()

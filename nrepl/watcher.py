import os
import time
import errno
import socket

from nrepl._compat import urlparse
from nrepl.clj import get_ns
from nrepl.utils import console, get_ts, traverse_dir
from nrepl.client import Client


def nrepl_connect(uri):
    uri = urlparse(uri)
    _socket = socket.create_connection(uri.netloc.split(":"))
    _fd = _socket.makefile('rw')
    return Client(_fd, on_close=_socket.close)


class Watcher(object):

    def __init__(self, uri, timeout):
        self._mtimes = {}
        self.uri = uri
        self.timeout = timeout

    def trigger_reload(self, filename):
        filename = os.path.realpath(filename)
        console('Detected changes of %s, reloading' % filename, _color='2')
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
        console("Connect to %s" % self.uri, _color='2')

        start_ts = get_ts()
        while True:
            try:
                self._client = nrepl_connect(self.uri)
                break
            except socket.error as e:
                eno, _ = e
                if eno == errno.ECONNREFUSED:
                    ts = get_ts()
                    if (ts - start_ts) > self.timeout:
                        raise TimeoutError('%s (in %ss)' % (e, self.timeout))
                    else:
                        continue
                raise e
            time.sleep(interval)

        console("Started watching %s" % dirpath, _color='2')

        while True:
            traverse_dir(dirpath, self.reload_if_updated)
            time.sleep(interval)

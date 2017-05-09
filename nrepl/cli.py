from __future__ import print_function

import os
import sys
import time
import signal
import argparse

from nrepl import __version__
from nrepl.watcher import Watcher
from nrepl.proc import build_sig_handler, Handler


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', choices=['run', 'watch'], nargs='?')
    parser.add_argument('-v', '--version', action='store_true', default=False)
    parser.add_argument('-u', '--uri', default=None)
    parser.add_argument('--host', default='localhost')
    parser.add_argument('-p', '--port', default=None)
    parser.add_argument('--profile', default=None)
    parser.add_argument('-w', '--watch-path', default='.')
    parser.add_argument('-t', '--timeout', type=int, default=60)
    parser.add_argument('-i', '--interval', type=int, default=3)
    args = parser.parse_args()

    if args.version is True:
        print(__version__)
        sys.exit(0)

    path = os.path.realpath(args.watch_path)
    uri = args.uri or 'nrepl://{}:{}'.format(args.host, args.port)

    if args.cmd == 'run':
        cmd = ['lein']
        if args.profile:
            cmd.append('with-profile')
            cmd.append(args.profile)
        cmd.append('run')
        h = Handler(cmd)
        h.start()

        signal.signal(signal.SIGTERM, build_sig_handler(h))
        signal.signal(signal.SIGINT, build_sig_handler(h))

        time.sleep(5)    # wait for start

        try:
            watcher = Watcher(uri, timeout=args.timeout)
            watcher.start(path, args.interval)
        except Exception as e:
            h.stop()
            h.join()
            raise e

    if args.cmd == 'watch':
        watcher = Watcher(uri, timeout=args.timeout)
        watcher.start(path, args.interval)

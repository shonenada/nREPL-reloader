import os
import sys
import signal
import threading
import subprocess

from nrepl.utils import console


class TimeoutError(Exception):
    pass


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

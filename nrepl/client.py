from nrepl._compat import string_types


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


class Client(object):

    def __init__(self, fd, on_close=None):
        self.fd = fd
        self.on_close = on_close

    def write(self, data):
        return _write_data(self.fd, data)

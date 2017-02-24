from nrepl._compat import string_types, StringIO


def _read_byte(fd):
    return fd.read(1)


def _read_int(fd, term=None, init_data=None):
    chrs = init_data or []
    while True:
        c = _read_byte(fd)
        if not c or not c.isdigit() or c == term:
            break
        else:
            chrs.append(c)
    return int(''.join(chrs))


def _read_list(fd):
    data = []
    while True:
        rv = _read_data(fd)
        if not rv:
            break
        data.append(rv)
    return data


def _read_map(fd):
    i = iter(_read_list(fd))
    return dict(zip(i, i))


def _read_bytes(fd, n):
    data = StringIO()
    cnt = 0
    while cnt < n:
        m = fd.read(n - cnt)
        if not m:
            raise Exception("Invalid bytestring, unexpected end of input.")
        data.write(m)
        cnt += len(m)
    data.flush()
    # Taking into account that Python3 can't decode strings
    try:
        ret = data.getvalue().decode("UTF-8")
    except AttributeError:
        ret = data.getvalue()
    return ret


def _read_delim(fd):
    delim = _read_byte(fd)
    if delim.isdigit():
        delim = _read_int(fd, ':', [delim])
    return delim


def _read_data_by_delim(fd, delim):
    if delim == 'i':
        return _read_int(fd)

    if delim == 'l':
        return _read_list(fd)

    if delim == 'd':
        return _read_map(fd)

    if delim == 'e':
        return None

    if delim is None:
        return None

    return _read_bytes(fd, delim)


def _read_data(fd):
    delim = _read_delim(fd)
    if delim:
        return _read_data_by_delim(fd, delim)


def _write_data(fd, data):
    write = fd.write
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

    def read(self):
        return _read_data(self.fd)

    def write(self, data):
        return _write_data(self.fd, data)

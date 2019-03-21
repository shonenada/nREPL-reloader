def get_ns_declare(fd):
    while True:
        line = fd.readline()
        if line.strip().startswith('(ns'):
            return line


def get_ns(filename):
    with open(filename, 'r') as infile:
        ns_declare = get_ns_declare(infile)
        splited = ns_declare.split()
        ns = splited[-1]
        if ns.endswith(')'):
            ns = ns[:-1]
    return ns.strip()

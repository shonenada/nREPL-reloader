import sys

PY2 = sys.version_info[0] == 2

# compatibility support
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"Special module to handle differences between Python 2 and 3 versions"

import sys

PY3K = sys.version_info >= (3, 0)

from PIL import Image
from six.moves.urllib.request import urlopen
from hashlib import md5  # python <2.6 not supported
from io import BytesIO  # python <2.6 not supported

import pickle
try:
    import cPickle as pickle
except ImportError as e:
    pass

def hashpath(fn):
    h = md5()
    if PY3K:
        h.update(fn.encode("UTF-8"))
    else:
        h.update(fn)
    return h.hexdigest()

def unescape2(*args, **kwargs):
    return HTMLParser().unescape(*args, **kwargs)

def unescape3(*args, **kwargs):
    import html
    return html.unescape(*args, **kwargs)

unescape = unescape3 if PY3K else unescape2

# why is this next part like this?
try:
	from HTMLParser import HTMLParser
except ImportError as e:
	from html.parser import HTMLParser

if PY3K:
    basestring = str
    unicode = str
    ord = lambda x: x
else:
    basestring = basestring
    unicode = unicode
    ord = ord

# shortcut to bytes conversion (b prefix)
def b(s): 
    if isinstance(s, basestring):
        return s.encode("latin1")
    elif isinstance(s, int):
        if PY3K:
            return bytes([s])  # http://bugs.python.org/issue4588
        else:
            return chr(s)

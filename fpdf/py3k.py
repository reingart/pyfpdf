#!/usr/bin/env python
# -*- coding: utf-8 -*-

"Special module to handle differences between Python 2 and 3 versions"

import sys

PY3K = sys.version_info >= (3, 0)

from PIL import Image
from six.moves.urllib.request import urlopen

try:
    import cPickle as pickle
except ImportError as e:
    import pickle

try:
    from io import BytesIO
except ImportError as e:
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError as e:
        from StringIO import StringIO as BytesIO

try:
    from hashlib import md5
except ImportError as e:
    try:
        from md5 import md5
    except ImportError as e:
        md5 = None
def hashpath(fn):
    h = md5()
    if PY3K:
        h.update(fn.encode("UTF-8"))
    else:
        h.update(fn)
    return h.hexdigest()

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
            return bytes([s])       # http://bugs.python.org/issue4588
        else:
            return chr(s)

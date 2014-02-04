#!/usr/bin/env python
# -*- coding: utf-8 -*-

"Special module to handle differences between Python 2 and 3 versions"

import sys

PY3K = sys.version_info >= (3, 0)

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
	from urllib import urlopen
except ImportError:
	from urllib.request import urlopen

# Check if PIL is available (tries importing both pypi version and corrected or manually installed versions).
# Necessary for JPEG and GIF support.
try:
    try:
        import Image
    except:
        from PIL import Image
        # TODO: Pillow support
except ImportError:
    Image = None

try:
	from HTMLParser import HTMLParser
except ImportError:
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
b = lambda s: s.encode("latin1")

def exception():
    "Return the current the exception instance currently being handled"
    # this is needed to support Python 2.5 that lacks "as" syntax
    return sys.exc_info()[1]



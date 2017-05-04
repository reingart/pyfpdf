# -*- coding: latin-1 -*-

"Utility Functions (previously FPDF#methods)"

import struct

def freadint(f):
    "Read a 4-byte integer from file"
    try:
        return struct.unpack('>I', f.read(4))[0]
    except:
        return None

def textstring(s):
    "Format a text string"
    return '(' + escape(s) + ')'

def escape(s):
    "Add \ before \, ( and )"
    return s.replace('\\', '\\\\') \
            .replace(')', '\\)') \
            .replace('(', '\\(') \
            .replace('\r', '\\r')

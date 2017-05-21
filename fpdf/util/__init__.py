# -*- coding: latin-1 -*-

"Utility Functions (previously FPDF#methods)"

import struct
from fpdf.php import sprintf

def freadint(f):
    "Read a 4-byte integer from file"
    try:
        return struct.unpack('>I', f.read(4))[0]
    except:
        return None

def textstring(s):
    "Format a text string"
    if s:
        return '(' + escape(s) + ')'
    else:
        return ''

def escape(s):
    "Add \ before \, ( and )"
    return s.replace('\\', '\\\\') \
            .replace(')', '\\)') \
            .replace('(', '\\(') \
            .replace('\r', '\\r')

def dochecks():
    # Check for locale-related bug
    # if (1.1==1):
    #     fpdf_error("Don\'t alter the locale before "
    #                "including class file")
    # Check for decimal separator
    if (sprintf('%.1f', 1.0) != '1.0'):
        import locale
        locale.setlocale(locale.LC_NUMERIC, 'C')

# Moved here from FPDF#__init__
dochecks()

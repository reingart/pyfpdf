# -*- coding: latin-1 -*-

"Utility Functions (previously FPDF#methods)"

import struct
from fpdf.php import sprintf


def textstring(s):
    "Format a text string"
    if s:
        return "(" + escape(s) + ")"
    else:
        return ""


def escape(s):
    "Add a backslash character before , ( and )"
    return (
        s.replace("\\", "\\\\")
        .replace(")", "\\)")
        .replace("(", "\\(")
        .replace("\r", "\\r")
    )


# shortcut to bytes conversion (b prefix)
def b(s):
    if isinstance(s, str):
        return s.encode("latin1")
    elif isinstance(s, int):
        return bytes([s])  # http://bugs.python.org/issue4588


def dochecks():
    # Check for locale-related bug
    # if (1.1==1):
    #     fpdf_error("Don\'t alter the locale before "
    #                "including class file")
    # Check for decimal separator
    if sprintf("%.1f", 1.0) != "1.0":
        import locale

        locale.setlocale(locale.LC_NUMERIC, "C")


# Moved here from FPDF#__init__
dochecks()

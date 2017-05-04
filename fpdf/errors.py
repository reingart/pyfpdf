# -*- coding: latin-1 -*-

"""FPDF Error classes"""

# this module is unwriteable without tests

def fpdf_error(message):
    raise RuntimeError('FPDF error: ' + message)

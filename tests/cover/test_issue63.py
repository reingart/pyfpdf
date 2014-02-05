# -*- coding: latin-1 -*-

"Basic test to reproduce issue 63: warning in unicode get_char_width"

import common
from fpdf import FPDF

import os, struct

def dotest(outputname, nostamp):

    pdf = FPDF()
    pdf.set_font('Arial','',14)  
    s = 'Texto largo que no cabe en esta celda pero que será ajustado'
    w = pdf.get_string_width(s)
    if not nostamp:
        print (s, w)
    assert round(w, 2) == 135.90
    pdf.add_font('DejaVu', '', './font/DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    s = u'Texto largo que no cabe en esta celda pero que será ajustado'
    w = pdf.get_string_width(s)
    if not nostamp:
        print (s, w)
    assert round(w, 2) == 153.64
                
if __name__ == "__main__":
    common.testmain(__file__, dotest)


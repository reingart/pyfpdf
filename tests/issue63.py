#!/usr/bin/env python
# -*- coding: latin1 -*-

"Basic test to reproduce issue 63: warning in unicode get_char_width"

from fpdf import FPDF
pdf = FPDF()
pdf.set_font('Arial','',14)  
s = 'Texto largo que no cabe en esta celda pero que será ajustado'
w = pdf.get_string_width(s)
print (s, w)
assert round(w, 2) == 135.90
pdf.add_font('DejaVu', '', './font/DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', '', 14)
s = u'Texto largo que no cabe en esta celda pero que será ajustado'
w = pdf.get_string_width(s)
print (s, w)
assert round(w, 2) == 153.64


#!/usr/bin/env python
# -*- coding: utf8 -*-

"Basic test to reproduce issue 60: RTL languages (arabian, hebrew, etc.)"

from fpdf import FPDF
pdf = FPDF()
pdf.compress = False
pdf.add_page()
pdf.add_font('DejaVu', '', './font/DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', '', 14)
# this will be displayed wrong as actually it is stored LTR:
text= u"این یک متن پارسی است. This is a Persian text !!"
pdf.write(8, text)
pdf.ln(8)
# Reverse the RLT using the Bidirectional Algorithm to be displayed correctly:
# (http://unicode.org/reports/tr9/)
from bidi.algorithm import get_display
rtl_text = get_display(text)
pdf.write(8, rtl_text)
fn = 'issue60.pdf'
pdf.output(fn,'F')
import os
try:
    os.startfile(fn)
except:
    os.system("xdg-open \"%s\"" % fn)

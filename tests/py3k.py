#!/usr/bin/env python
# -*- coding: latin-1 -*-

"Basic example to test py3k conversion"

import sys
from fpdf import FPDF
    
pdf = FPDF()
# compression is not yet supported in py3k version
pdf.compress = True
pdf.add_page()
# unicode is not yet supported in py3k version, use windows-1252 standards font
pdf.set_font('Arial','',14)  
pdf.ln(10)
pdf.write(5, 'hello world %s áéíóúüñ' % sys.version)
pdf.image("../tutorial/logo.png", 50, 50)
pdf.image("flower2.jpg", 100, 50)
pdf.image("lena.gif", 50, 75)

fn='py3k.pdf'
pdf.output(fn,'F')
import os
try:
    os.startfile(fn)
except:
    os.system("xdg-open \"%s\"" % fn)

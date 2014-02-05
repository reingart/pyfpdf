#!/usr/bin/env python
# -*- coding: utf-8 -*-

"Basic example to test py3k conversion"

import sys
from fpdf import FPDF
    
pdf = FPDF()
# compression also supported in py3k version
pdf.compress = True
pdf.add_page()
# unicode is not yet supported in py3k version, use windows-1252 standards font
pdf.set_font('Arial','',14)  
pdf.ln(10)
pdf.write(5, u'hello world %s áéíóúüñ' % sys.version)
pdf.image("../tutorial/logo.png", 50, 50)
pdf.image("flower2.jpg", 100, 50)
pdf.image("lena.gif", 50, 75)

# Add a DejaVu Unicode font (uses UTF-8)
# Supports more than 200 languages. For a coverage status see:
# http://dejavu.svn.sourceforge.net/viewvc/dejavu/trunk/dejavu-fonts/langcover.txt
pdf.add_font('DejaVu','','DejaVuSansCondensed.ttf',uni=True)
pdf.set_font('DejaVu','',14)
pdf.ln(10)
pdf.write(8, u"Hello world in Russian: Здравствулте мир")

fn='py3k.pdf'
pdf.output(fn,'F')
import os
try:
    os.startfile(fn)
except:
    os.system("xdg-open \"%s\"" % fn)

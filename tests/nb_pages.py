#!/usr/bin/env python

"Simple test to check alias_nb_pages replacement under unicode fonts"

from fpdf import FPDF

pdf=FPDF()

# set default alias: {nb} that will be replaced with total page count
pdf.alias_nb_pages()

# Add a Unicode font (uses UTF-8)
pdf.add_font('DejaVu','','DejaVuSansCondensed.ttf',uni=True)
pdf.set_font('DejaVu','',14)

for i in range(5):
    pdf.add_page()
    pdf.set_font('Arial','B',16)
    pdf.cell(40,10,'Hello World! {nb}')
    pdf.set_font('DejaVu','',14)
    pdf.cell(40,10,'Hello World! unicode {nb}')
    
pdf.output('nb_pages.pdf','F')

import os
try:
    os.startfile(fn)
except:
    os.system("xdg-open \"%s\"" % fn)

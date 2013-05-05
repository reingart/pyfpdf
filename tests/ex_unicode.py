# Example of unicode support based on tfPDF
# http://www.fpdf.org/en/script/script92.php

from fpdf import FPDF
import sys

pdf = FPDF()
pdf.add_page()

# Add a Unicode font (uses UTF-8)
pdf.add_font('DejaVu','','DejaVuSansCondensed.ttf',uni=True)
pdf.set_font('DejaVu','',14)
fn = 'ex.pdf'

# Load a UTF-8 string from a file and print it
txt = open('HelloWorld.txt').read()
pdf.write(8, txt)

# Select a standard font (uses windows-1252)
pdf.set_font('Arial','',14)
pdf.ln(10)
pdf.write(5, 'The file size of this PDF is only 12 KB.')

pdf.output(fn,'F')
import os
try:
    os.startfile(fn)
except:
    os.system("xdg-open \"%s\"" % fn)

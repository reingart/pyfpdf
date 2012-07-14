# Example of unicode support based on tfPDF
# http://www.fpdf.org/en/script/script92.php

import sys
import fpdf

# Set system font path
fpdf.set_global('SYSTEM_TTFONTS', r"c:\WINDOWS\Fonts")

pdf = fpdf.FPDF()
pdf.add_page()

# Add a Windows System font (uses UTF-8)
pdf.add_font('sysfont','','arial.ttf',uni=True)
pdf.set_font('sysfont','',14)
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
    os.system("evince %s" % fn)

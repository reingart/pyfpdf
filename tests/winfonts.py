# Example of unicode support based on tfPDF
# http://www.fpdf.org/en/script/script92.php

import sys
import time
import fpdf

# Set system font path
fpdf.set_global('SYSTEM_TTFONTS', r"c:\WINDOWS\Fonts")

pdf = fpdf.FPDF()
pdf.add_page()

# Add a Windows System font (uses UTF-8)
t0 = time.time()
pdf.add_font('sysfont','','arial.ttf',uni=True)
pdf.set_font('sysfont','',14)
t1 = time.time()
print "ttf loading time", t1-t0
fn = 'winfonts.pdf'

# Load a UTF-8 string from a file and print it
txt = open('HelloWorld.txt').read()
pdf.multi_cell(15, 5, txt)

pdf.text(100, 5, '1234')

pdf.write(5,'To find out what\'s new in self tutorial, click ')
pdf.set_font('','U')
link=pdf.add_link()
pdf.write(5,'here',link)

# Select a standard font (uses windows-1252)
pdf.set_font('Arial','',14)
pdf.ln(10)
pdf.write(5, 'The file size of this PDF is only 12 KB.')

pdf.output(fn,'F')
import os
os.startfile(fn)

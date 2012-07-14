#!/usr/bin/env python
# -*- coding: utf8 -*-

from fpdf import FPDF
import sys

fn = 'ex.pdf'

pdf = FPDF()
pdf.add_page()

# Add a Standard Unicode font (uses UTF-8)
pdf.add_font('DejaVu','','DejaVuSansCondensed.ttf',uni=True)
pdf.set_font('DejaVu','',14)

# Load a UTF-8 string from a file and print it
txt = open('HelloWorld.txt').read()
pdf.write(8, txt)


# Add a East-Asia Unicode font (uses UTF-8)
pdf.add_font('fireflysung','','fireflysung.ttf',uni=True)
pdf.set_font('fireflysung','',14)

pdf.ln(10)

pdf.write(8, 'Chinese: 你好世界\n')
pdf.write(8, 'Japanese: こんにちは世界\n')
pdf.write(8, 'Korean: 안녕하세요\n')

# Select a standard font (uses windows-1252)
pdf.set_font('Arial','',14)
pdf.ln(10)
pdf.write(5, 'The is standard built in font')

pdf.output(fn,'F')
import os
try:
    os.startfile(fn)
except:
    os.system("evince %s" % fn)

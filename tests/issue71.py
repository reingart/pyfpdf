#!/usr/bin/env python
# -*- coding: utf8 -*-

"Basic test to check issue 70: raise an exception if add_page was not called"


import fpdf
# Portrait, millimeter units, A4 page size     
pdf=fpdf.FPDF("P", "mm", "A4")
# Set font: Times, normal, size 10
pdf.add_page()
url = "http://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Code_3_of_9.svg/262px-Code_3_of_9.svg.png"
pdf.image(url, 10, 10)
pdf.code39("*wikipedia*", 12.75, 7, 1.49)
fn = 'issue71.pdf'
pdf.output(fn,'F')

import os
try:
    os.startfile(fn)
except:
    os.system("xdg-open \"%s\"" % fn)

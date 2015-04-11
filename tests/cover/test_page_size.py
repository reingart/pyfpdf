# -*- coding: utf-8 -*-

"Test page sizes and orientation"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=page_size.pdf
#PyFPDF-cover-test:hash=be021da05095336223c011d0a23bc40f

import os

import common
from fpdf import FPDF

def page(pdf, text, orientation, format):
    pdf.add_page(orientation = orientation, format = format)
    pdf.write(8, text)
    pdf.ln(8)

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF(orientation = "L", format = (100, 250))
    pdf.compress = False
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)
    pdf.set_font('Arial', '', 14)
    for i in range(16):
        o = ["p", "l"][i % 2]
        f = ["a3", "a4", "a5", "letter", "legal", "",
            (100, 250), (320, 240)][i % 8]
        page(pdf, "Page %d from 16\nFormat: %s\nOrientation: %s" % 
            (i + 1, f, o), o, f)
    pdf.output(outputname, 'F')

def main():
    return common.testmain(__file__, dotest)

if __name__ == "__main__":
    main()


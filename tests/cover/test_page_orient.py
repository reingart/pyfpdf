# -*- coding: utf-8 -*-

"Test page orientation"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=page_orient.pdf
#PyFPDF-cover-test:hash=5adb1bc3a5c384e140c71e530f0f735a

import os

import common
from fpdf import FPDF

def page(pdf, text, orientation):
    pdf.add_page(orientation = orientation)
    pdf.write(8, text)
    pdf.ln(8)

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF(orientation = "L", format = "A5")
    pdf.compress = False
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)
    pdf.set_font('Arial', '', 14)
    for i in range(10):
        o = ["p", "L", "P", "l"][i % 4]
        page(pdf, "Page %d from 10\nOrientation: %s" % (i + 1, o), o)
    pdf.output(outputname, 'F')
    
def main():
    return common.testmain(__file__, dotest)
    
if __name__ == "__main__":
    main()


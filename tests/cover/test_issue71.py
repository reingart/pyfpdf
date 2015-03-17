# -*- coding: utf-8 -*-

"Basic test to check issue 71: test Code39"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=issue_71.pdf
#PyFPDF-cover-test:hash=1575947cac5b0a8cdceedf9b525ee6db
# get res from http://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Code_3_of_9.svg/262px-Code_3_of_9.svg.png
# PyFPDF-cover-test:res=.png

import common
from fpdf import FPDF

import os

@common.add_unittest
def dotest(outputname, nostamp):
    # Portrait, millimeter units, A4 page size     
    pdf = FPDF("P", "mm", "A4")
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)
    # Set font: Times, normal, size 10
    pdf.add_page()
    if not nostamp:
        # do not show picture in batch
        url = "http://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Code_3_of_9.svg/262px-Code_3_of_9.svg.png"
        pdf.image(url, 10, 10)

    pdf.code39("*wikipedia*", 12.75, 7, 1.49)

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


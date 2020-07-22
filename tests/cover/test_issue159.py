# -*- coding: utf-8 -*-

"Basic test for set_link"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=issue_159.pdf
#PyFPDF-cover-test:hash=e91dc694a1b39a64750d5960f84c8cae

import common
from fpdf import FPDF

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()

    link_to_page(pdf, 1, 100, 100, 500, 500)

    pdf.output(outputname, 'F')

def link_to_page(pdf, page_id, x, y, width, height):
    link = pdf.add_link()
    pdf.set_link(link, page=page_id)
    pdf.link(x, y, width, height, link)

if __name__ == "__main__":
    common.testmain(__file__, dotest)


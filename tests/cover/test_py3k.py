# -*- coding: latin-1 -*-

"Basic example to test py3k conversion"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=py3k.pdf
#PyFPDF-cover-test:hash=52e9af3018aa8020316b290e837eb8ad
#PyFPDF-cover-test:python2=no

import common # test utilities
from fpdf import FPDF

import sys

def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)
    # compression is not yet supported in py3k version
    pdf.compress = False
    pdf.add_page()
    # unicode is not yet supported in py3k version, use windows-1252 standards font
    pdf.set_font('Arial', '', 14)  
    pdf.ln(10)
    if nostamp:
        data = "TEST-TEST-TEST"
    else:
        data = sys.version
    # Note: file encoding is latin-1
    pdf.write(5, 'hello world %s áéíóúüñ' % data)
    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


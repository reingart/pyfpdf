# -*- coding: utf-8 -*-

"Basic example to test py3k conversion"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=py3k.pdf
#PyFPDF-cover-test:hash=ecf5ec7b9a3bb6015b4c9f0546f62e84
#PyFPDF-cover-test:python2=no

import common # test utilities
from fpdf import FPDF

import sys

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()
    pdf.set_font('Arial', '', 14)  
    pdf.ln(10)
    if nostamp:
        data = "TEST-TEST-TEST"
    else:
        data = sys.version

    #áéíóúüñ
    # This string converted with errors in py2.x 
    pdf.write(5, ('hello world %s áéíóúüñ' % data))

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


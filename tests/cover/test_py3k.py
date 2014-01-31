# -*- coding: latin-1 -*-

"Basic example to test py3k conversion"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=py3k.pdf
#PyFPDF-cover-test:hash=2b136c8ca150bf3f0d245aa4bf6fc3d6
#PyFPDF-cover-test:python2=no

import common # test utilities
from fpdf import FPDF

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
    pdf.write(5, 'hello world %s áéíóúüñ' % range(4))
    pdf.output(outputname, 'F')


if __name__ == "__main__":
    common.testmain(__file__, dotest)


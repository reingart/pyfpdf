# -*- coding: utf-8 -*-

"Basic example to test PyFPDF"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=simple.pdf
#PyFPDF-cover-test:hash=1fd821a42cb5029a51727a6107b623ec
#PyFPDF-cover-test:pil=yes
#PyFPDF-cover-test:res=../tutorial/logo.png
#PyFPDF-cover-test:res=flower2.jpg
#PyFPDF-cover-test:res=lena.gif

import common # test utilities
from fpdf import FPDF

import sys
import os, os.path

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

    pdf.write(5, 'hello world %s' % data)
    path = os.path.join(common.basepath, os.pardir, "tutorial", "logo.png")
    pdf.image(path, 50, 50)
    pdf.image(os.path.join(common.basepath, "flower2.jpg"), 100, 50)
    pdf.image(os.path.join(common.basepath, "lena.gif"), 50, 75)
    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


# -*- coding: utf-8 -*-

"Example of unicode support based on tfPDF http://www.fpdf.org/en/script/script92.php"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=ex.pdf
#PyFPDF-cover-test:hash=f77f71491e1662a732212861a2d87928
#PyFPDF-cover-test:res=font/DejaVuSansCondensed.ttf
#PyFPDF-cover-test:res=HelloWorld.txt

import common
from fpdf import FPDF

import os

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()
    # Add a Unicode font (uses UTF-8)
    pdf.add_font('DejaVu', '', \
        os.path.join(common.basepath, "font", 'DejaVuSansCondensed.ttf'), \
        uni = True)
    pdf.set_font('DejaVu','',14)

    # Load a UTF-8 string from a file and print it
    txt = open(os.path.join(common.basepath, "HelloWorld.txt"), "rb").\
        read().decode("UTF-8")
    pdf.write(8, txt)


    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


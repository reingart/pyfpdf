
# -*- coding: utf-8 -*-

"Basic test for rotation"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=rotation.pdf
#PyFPDF-cover-test:hash=5dbe8d24682841efaccc5b48e590111e

import os
import common
from fpdf import FPDF

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()

    with pdf.rotation(90, x=16, y=16):
        pdf.image(os.path.join(common.basepath, "lena.gif"), x=0, y=0)

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)
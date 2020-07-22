# -*- coding: utf-8 -*-

"Basic test for rect_clip"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=rect_clip.pdf
#PyFPDF-cover-test:hash=2ab48819c54cb0b3f48514667441c952

import os
import common
from fpdf import FPDF

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()

    with pdf.rect_clip(x=16, y=16, w=16, h=16):
        pdf.image(os.path.join(common.basepath, "lena.gif"), x=0, y=0)

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)

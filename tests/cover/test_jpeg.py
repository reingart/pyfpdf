# -*- coding: utf-8 -*-

"Test jpeg image embedding"

# Note: img_cmyk.jpg has no color profile, PDF rendering may vary

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=jpeg.pdf
#PyFPDF-cover-test:hash=eb8db8f336226f6de671a3e515b9cc61
#PyFPDF-cover-test:res=img_gray.jpg
#PyFPDF-cover-test:res=img_rgb.jpg
#PyFPDF-cover-test:res=img_cmyk.jpg

import common # test utilities
from fpdf import FPDF

import os.path

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()
    pdf.set_font('Arial', '', 14)  

    pdf.text(10, 57, 'DeviceGray')
    pdf.image(os.path.join(common.basepath, "img_gray.jpg"), 55, 5)

    pdf.text(10, 157, 'DeviceRGB')
    pdf.image(os.path.join(common.basepath, "img_rgb.jpg"), 55, 105)

    pdf.text(10, 257, 'DeviceCMYK')
    pdf.image(os.path.join(common.basepath, "img_cmyk.jpg"), 55, 205)

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


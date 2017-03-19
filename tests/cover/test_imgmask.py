# -*- coding: utf-8 -*-

"Test image masking"
# https://github.com/reingart/pyfpdf/pull/80

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=masking.pdf
#PyFPDF-cover-test:hash=53abdb706882ecdedf5ee4c59852ae48
#PyFPDF-cover-test:res=masking.png
#PyFPDF-cover-test:res=lena.gif
#PyFPDF-cover-test:res=img_gray.jpg
#PyFPDF-cover-test:res=img_cmyk.jpg
#PyFPDF-cover-test:res=img_rgb.jpg
#PyFPDF-cover-test:pil=yes

import common
from fpdf import FPDF

import os

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()
    pdf.set_font('Arial', '', 14)  

    for i in range(0, 270, 5):
        pdf.text(i % 40 + 20, i + 20, "Image masking " * 4)
    mask = pdf.image(os.path.join(common.basepath, "masking.png"), 
        is_mask = True)
    pdf.image(os.path.join(common.basepath, "lena.gif"), 
        40.0, 20.0, w = 120, mask_image = mask)

    pdf.image(os.path.join(common.basepath, "img_gray.jpg"), 
        20.0, 200.0, w = 50, mask_image = mask)
    pdf.image(os.path.join(common.basepath, "img_rgb.jpg"), 
        80.0, 200.0, w = 50, mask_image = mask)
    pdf.image(os.path.join(common.basepath, "img_cmyk.jpg"), 
        140.0, 200.0, w = 50, mask_image = mask)

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


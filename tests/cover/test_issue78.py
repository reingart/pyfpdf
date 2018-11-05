# -*- coding: utf-8 -*-

"Test RGB image with transparency"
# https://github.com/reingart/pyfpdf/issues/78

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=issue_78.pdf
#PyFPDF-cover-test:hash=295ef37323b3115da64fcc47c1aca8dc
#PyFPDF-cover-test:res=../tutorial/logo.png
#PyFPDF-cover-test:pil=yes

import common
from fpdf import FPDF

import os
import tempfile
try:
    try:
        import Image
    except:
        from PIL import Image
except ImportError:
    Image = None

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF(orientation = "L", unit = "in")
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()

    img_path = os.path.join(common.basepath, '../tutorial/logo.png')
    img = Image.open(img_path)
    w, h = img.size
    width = 8
    height = width * (h // w)
    with tempfile.NamedTemporaryFile(delete = False, suffix = ".png") as f:
        img_new = f.name
    # convert to RGBA
    img2 = img.convert(mode = "RGBA")
    img2.save(img_new)
    # create pdf
    pdf.image(img_new, x = 1, y = 1, w = width, h = height)

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


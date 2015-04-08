# -*- coding: utf-8 -*-

"Example of font stretching and spacing"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=stretch.pdf
#PyFPDF-cover-test:hash=5d4986d871e909b08bf69d0ed3050d83
#PyFPDF-cover-test:res=font/DejaVuSans.ttf
#PyFPDF-cover-test:res=HelloWorld.txt

import common
import fpdf
from fpdf import FPDF

import os

def text(pdf, txt, stretching, nostamp):
    pdf.set_stretching(100)
    if not nostamp:
        pdf.write(8, "Text: stretching %.2f%%\n" %(stretching))
    pdf.set_stretching(stretching)
    if not nostamp:
        pdf.write(8, txt)
    if not nostamp:
        txtc = "Cell example: stretching %.2f%%" %(stretching)
        for a in ["L", "C", "R"]:
            pdf.cell(w = 0, h = 8, txt = txtc, border = 1, align = a)
            pdf.write(8, "\n")
        pdf.write(8, "\n")
    if not nostamp:
        txtm = "MultiCell example: stretching %.2f%%" %(stretching) + " and words" * 50 + "\n"
    else:
        txtm = "Stretch=%.2f, Align=" % (stretching)
    for a in ["L", "C", "R", "J"]:
        if nostamp and a == "J":
            txtw = txt.replace("\n", " ")
        else:
            txtw = txt
        pdf.multi_cell(w = 0, h = 8, txt = txtm + a + "\n" + txtw, border = 1, align = a)
        pdf.write(8, "\n")
    pdf.write(8, "\n")
    

@common.add_unittest
def dotest(outputname, nostamp):
    fpdf.set_global("FPDF_CACHE_MODE", 1)
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()
    # Add a Unicode font (uses UTF-8)
    pdf.add_font('DejaVu', '', \
        os.path.join(common.basepath, "font", 'DejaVuSans.ttf'), \
        uni = True)
    pdf.set_font('DejaVu', '', 14)
    with open(os.path.join(common.basepath, "HelloWorld.txt"), "rb") as file:
        txt = file.read().decode("UTF-8")

    if not nostamp:
        text(pdf, txt, 100, nostamp)
    text(pdf, txt, 75, nostamp)
    text(pdf, txt, 125, nostamp)

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


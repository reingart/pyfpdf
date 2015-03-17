# -*- coding: utf-8 -*-

"Simple test to check alias_nb_pages replacement under unicode fonts"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=nb_pages.pdf
#PyFPDF-cover-test:hash=071fab0d32afcbe780e171c0da50865a
#PyFPDF-cover-test:res=font/DejaVuSansCondensed.ttf

import common
import fpdf

import os

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = fpdf.FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    fpdf.set_global("FPDF_CACHE_MODE", 1)
    # set default alias: {nb} that will be replaced with total page count
    pdf.alias_nb_pages()

    # Add a Unicode font (uses UTF-8)
    pdf.add_font('DejaVu', '', \
        os.path.join(common.basepath, "font", 'DejaVuSansCondensed.ttf'), \
        uni = True)
    pdf.set_font('DejaVu', '', 14)

    for i in range(5):
        pdf.add_page()
        pdf.set_font('Arial','B',16)
        pdf.cell(40,10,'Hello World! Page %d from {nb}' % (i + 1))
        pdf.set_font('DejaVu','',14)
        pdf.cell(40,30,'Hello World! unicode {nb}')


    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


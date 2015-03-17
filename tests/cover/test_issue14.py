# -*- coding: utf-8 -*-

"Test images flow mode (cell-like, trigger page breaks)"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=issue_14.pdf
#PyFPDF-cover-test:hash=7e4a5b0a77c4eaefa475bb7db655fcd9
#PyFPDF-cover-test:res=../tutorial/logo_pb.png

import common
from fpdf import FPDF

import os

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()

    for i in range(1,41):
        # for flow mode, do not pass x or y:
        pdf.image(os.path.join(common.basepath, '../tutorial/logo_pb.png'))

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


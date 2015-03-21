# -*- coding: utf-8 -*-

"Basic test to reproduce issue 60: RTL languages (arabian, hebrew, etc.)"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=issue_60.pdf
#PyFPDF-cover-test:hash=ef5e4effbe67ced3b1fbb1a7db53d7da
#PyFPDF-cover-test:res=font/DejaVuSans.ttf

import common
from fpdf import FPDF

import sys, traceback, os

@common.add_unittest
def dotest(outputname, nostamp):
    try:
        from bidi.algorithm import get_display
    except ImportError:
        from unittest import SkipTest
        raise SkipTest("Need python-bidi")
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.compress = False
    pdf.add_page()
    pdf.add_font('DejaVu', '', \
        os.path.join(common.basepath, 'font/DejaVuSans.ttf'), uni=True)
    pdf.set_font('DejaVu', '', 14)
    # this will be displayed wrong as actually it is stored LTR:
    text= u"این یک متن پارسی است. This is a Persian text !!"
    pdf.write(8, text)
    pdf.ln(8)
    # Reverse the RLT using the Bidirectional Algorithm to be displayed correctly:
    # (http://unicode.org/reports/tr9/)
    rtl_text = get_display(text)
    pdf.write(8, rtl_text)

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    try:
        from bidi.algorithm import get_display
    except ImportError:
        traceback.print_exc()
        common.err("This test requre PyBiDi (https://pypi.python.org/pypi/python-bidi)")
        common.log("SKIP")
        sys.exit(0)
    common.testmain(__file__, dotest)


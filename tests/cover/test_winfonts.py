# -*- coding: utf-8 -*-

"Example of unicode support winfonts based on tfPDF"
# http://www.fpdf.org/en/script/script92.php

from __future__ import with_statement

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=winfonts.pdf
#PyFPDF-cover-test:platform=win32
#PyFPDF-cover-test:res=HelloWorld.txt

# This test can't calc hash because TTF fonts can vary on systems

import common
import fpdf

import os, time

@common.add_unittest
def dotest(outputname, nostamp):
    fpdf.set_global('SYSTEM_TTFONTS', "c:\\WINDOWS\\Fonts")

    pdf = fpdf.FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)

    pdf.add_page()
    # Add a Windows System font (uses UTF-8)
    t0 = time.time()
    pdf.add_font('sysfont','','arial.ttf',uni=True)
    pdf.set_font('sysfont','',14)
    t1 = time.time()
    if not nostamp:
        common.log("ttf loading time", t1-t0)

    # Load a UTF-8 string from a file and print it
    with open(os.path.join(common.basepath, "HelloWorld.txt"), "rb") as file:
        txt = file.read().decode("UTF-8")
    pdf.multi_cell(25, 5, txt)

    pdf.text(100, 5, '1234')

    pdf.write(5,'To find out what\'s new in self tutorial, click ')
    pdf.set_font('','U')
    link=pdf.add_link()
    pdf.write(5,'here',link)

    # Select a standard font (uses windows-1252)
    pdf.set_font('Arial','',14)
    pdf.ln(10)
    pdf.write(5, 'The file size of this PDF is only 12 KB.')

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)


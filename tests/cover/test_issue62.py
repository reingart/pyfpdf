# -*- coding: utf-8 -*-

"Test issue 62 (Can't render unicode character letter c with caron)"

# This was issue to c with caron due
#   U+010C (uppercase Č) 
#   U+010D (lowercase č).
# and not properly escaping

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=issue_62.pdf
#PyFPDF-cover-test:hash=44624598b76bd4a18c6b14d3e00563e7
#PyFPDF-cover-test:res=font/DejaVuSansCondensed.ttf

import os

import common
from fpdf import FPDF

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)
    pdf.add_page()
    pdf.add_font('DejaVu', '', os.path.join(common.basepath, 
        'font/DejaVuSansCondensed.ttf'), uni = True)
    pdf.set_font('DejaVu', '', 14)

    # Note: this line cause syntax error in Python 3.0-3.2
    text = u"""
Veľké písmená
A   Á   Ä   B   C   Č   D   Ď   DZ  DŽ  E   É   F   G   H   CH  I   Í   J   K   L   Ĺ   Ľ
Malé písmená
a   á   ä   b   c   č   d   ď   dz  dž  e   é   f   g   h   ch  i   í   j   k   l   ĺ   ľ
Veľké písmená
M   N   Ň   O   Ó   Ô   P   Q   R   Ŕ   S   Š   T   Ť   U   Ú   V   W   X   Y   Ý   Z   Ž
Malé písmená
m   n   ň   o   ó   ô   p   q   r   ŕ   s   š   t   ť   u   ú   v   w   x   y   ý   z   ž
"""

    pdf.write(8, text)
    pdf.ln(8)
    pdf.output(outputname, 'F')
    
def main():
    return common.testmain(__file__, dotest)
    
if __name__ == "__main__":
    main()


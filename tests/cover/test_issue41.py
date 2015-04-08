# -*- coding: utf-8 -*-

"Test issue 41 (escape CR char)"

from __future__ import with_statement

#PyFPDF-cover-test:format=TXT
#PyFPDF-cover-test:fn=issue_41.txt
#PyFPDF-cover-test:hash=c576afec3362a7cc3b4b07a12feeefd3

import common # common set of utilities
import fpdf

import sys

@common.add_unittest
def dotest(outputname, nostamp):
    txt = "This is test string for issue41 with special symbols \n" +\
        "ln - \n\n" +\
        "cr - \r\n" +\
        "\\ ( ) abcdef..xyz 01234\n" +\
        "| [ ] ABCDEF..XYZ 56789\n"
         
    pdf = fpdf.FPDF()
    with open(outputname, "wb") as f:
        f.write(pdf._escape(txt).encode("latin1"))

def main():
    return common.testmain(__file__, dotest)
    
if __name__ == "__main__":
    main()


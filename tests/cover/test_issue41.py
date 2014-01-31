# -*- coding: utf-8 -*-

"Test issue 41 (escape CR char)"

#PyFPDF-cover-test:format=TXT
#PyFPDF-cover-test:fn=issue_41.txt
#PyFPDF-cover-test:hash=c576afec3362a7cc3b4b07a12feeefd3

import common # common set of utilities
import fpdf

import sys

def dotest(outputname, nostamp):
    txt = "This is test string for issue41 with special symbols \n" +\
        "ln - \n\n" +\
        "cr - \r\n" +\
        "\\ ( ) abcdef..xyz 01234\n" +\
        "| [ ] ABCDEF..XYZ 56789\n"
         
    pdf = fpdf.FPDF()
    f = open(outputname, "w")
    f.write(pdf._escape(txt))
    f.close()

def main():
    si = common.readcoverinfo(__file__)
    da = common.parsetestargs(sys.argv, si["fn"])
    if not common.checkenv(si, da):
        return
    dotest(da["fn"], da["autotest"] or da["check"])
    common.checkresult(si, da)
    
if __name__ == "__main__":
    main()


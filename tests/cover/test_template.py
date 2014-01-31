"This is test template"
# Lines below must not be separated by blank line
# output formats PDF (can be auto-opened), TXT
#PyFPDF-cover-test:output=PDF
# default filename
#PyFPDF-cover-test:fn=template.pdf
# hash stamp for compare in --check mode (insert your hash)
#PyFPDF-cover-test:hash=b1812fffdcf175976e80317b3766a0f0
# use 2to3 tool (default - no)
#PyFPDF-cover-test:2to3=no
# can be used in python2 (by default - yes)
#PyFPDF-cover-test:python2=yes
# can be used in python3 (by default - yes)
#PyFPDF-cover-test:python3=yes
# is PIL required (by default - no)
#PyFPDF-cover-test:pil=no

import common # common set of utilities
import fpdf

import sys

def dotest(filename, nostamp):
    # filename - output filename
    # nostamp - do no use stamp in result file
    
    pdf = fpdf.FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)
    pdf.add_page()
    pdf.set_font('Arial', '', 16)
    pdf.write(8, "Test template")
    pdf.output(filename, 'F')

def main():
    # read PyFPDF-cover-test settings
    si = common.readcoverinfo(__file__)
    # parse command line aguments (see --help)
    da = common.parsetestargs(sys.argv, si["fn"])
    # test environment
    if not common.checkenv(si, da):
        return
    # start test
    dotest(da["fn"], da["autotest"] or da["check"])
    # finish test
    common.checkresult(si, da)
    
if __name__ == "__main__":
    main()

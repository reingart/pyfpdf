# -*- coding: utf-8 -*-

"Basic test to check issue 70: raise an exception if add_page was not called"

import common
from fpdf import FPDF

import os, struct

@common.add_unittest
def dotest(outputname, nostamp):
    try:
        # Portrait, millimeter units, A4 page size     
        pdf = FPDF("P", "mm", "A4")
        # Set font: Times, normal, size 10
        pdf.set_font('Times','', 12)
        ##pdf.add_page()
        # Layout cell: 0 x 5 mm, text, no border, Left
        pdf.cell(0,5,'Input 1 : ',border=0,align="L")
        pdf.cell(0,5,'Input 2 : ', border=0,align="L")
        pdf.cell(0,5,'Recomendation : ', border=0, align="L")
        pdf.cell(0,5,'Data 1 :', border=0, align="L" )
        pdf.cell(0,5,'Data 2 :', border=0, align="L" )
        pdf.output(outputname,'F')
    except RuntimeError as e:
        assert e.args[0] == "FPDF error: No page open, you need to call add_page() first"
    else:
        raise RuntimeError("Exception not raised!")
                
if __name__ == "__main__":
    common.testmain(__file__, dotest)


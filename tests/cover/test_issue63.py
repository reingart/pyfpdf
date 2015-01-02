# -*- coding: latin-1 -*-

"Basic test to reproduce issue 63: warning in unicode get_char_width"

#PyFPDF-cover-test:res=font/DejaVuSans.ttf

import common
from fpdf import FPDF

import os.path, struct

if common.PY3K:
    def u(x):
        return x
else:
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]

@common.add_unittest
def dotest(outputname, nostamp):

    pdf = FPDF()
    pdf.set_font('Arial','',14)
    s = 'Texto largo que no cabe en esta celda pero que será ajustado'
    w = pdf.get_string_width(s)
    if not nostamp:
        print (s, w)
    assert round(w, 2) == 135.90
    font = os.path.join(common.basepath, 'font', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', '', font, uni=True)
    pdf.set_font('DejaVu', '', 14)
    s = u('Texto largo que no cabe en esta celda pero que será ajustado') 
    w = pdf.get_string_width(s)
    if not nostamp:
        print (s, w)
    assert round(w, 2) == 153.64
                
if __name__ == "__main__":
    common.testmain(__file__, dotest)


# -*- coding: utf-8 -*-

"Test get_string_width for missing glyphs (issue 82)"

#PyFPDF-cover-test:res=font/DejaVuSansCondensed.ttf
#PyFPDF-cover-test:res=HelloWorld.txt

import common
import fpdf

import os, shutil, time

def check_width(req, new):
    return round(new, 4) == round(req, 4)

@common.add_unittest
def dotest(outputname, nostamp):
    fpdf.set_global("FPDF_CACHE_MODE", 1)
    pdf = fpdf.FPDF()
    pdf.add_font('DejaVu', '', \
        os.path.join(common.basepath, "font", 'DejaVuSansCondensed.ttf'), \
        uni = True)
    pdf.set_font('DejaVu','',14)

    with open(os.path.join(common.basepath, "HelloWorld.txt"), "rb") as file:
        txt = file.read().decode("UTF-8")
    std_ln = [27.0849, 37.9455, 30.4927, 25.7711, 41.0175, 38.7406, 30.3445, 
        22.1163, 34.8314, 12.0813, 20.0829, 14.7485, 33.4188]
    for line, reqw in zip(txt.split("\n"), std_ln):
        if line[-1:] == "\r":
            line = line[:-1]
        lang = line.split(":", 1)
        w = pdf.get_string_width(lang[1])
        c = check_width(reqw, w)
        if not nostamp:
            s = lang[0] + ": "
            if c:
                s += "Ok"
            else:
                s += "%.4f != %.4f" % (w, reqw)
            common.log(s)
        assert c, "Glyph widths for \"" + lang[0] + "\" wrong!"

if __name__ == "__main__":
    common.testmain(__file__, dotest)


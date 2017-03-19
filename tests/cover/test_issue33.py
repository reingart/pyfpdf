# -*- coding: utf-8 -*-

"Test issue 33 (Cannot import GIF files that don't have transparency)"

from __future__ import with_statement

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=issue_33.pdf
#PyFPDF-cover-test:hash=be95c7ef3a5b14b5a54a52f7eaf3a9e4
#PyFPDF-cover-test:2to3=no
#PyFPDF-cover-test:pil=yes

import common
from fpdf import FPDF

import os, sys, tempfile
try:
    try:
        import Image
    except:
        from PIL import Image
except ImportError:
    Image = None


def genbar():
    # bg
    bg = Image.new("L", (112, 1), 1)
    bg = bg.resize((112, 11))
    # stripes
    vbarnum = [0x4F43484B, 0xEE90D642, 0xF11A2735, 0xD71A]
    vbar = Image.new("L", (112, 1), 1)
    pix = vbar.load()
    pos = 0
    for b in vbarnum:
        for i in range(32):
            pix[pos, 0] = 0 if (b & 1) else 1
            b = b >> 1
            pos += 1
            if pos >= 112: break    
    vbar = vbar.resize((112, 31), Image.NEAREST)
    # digit
    dignum = [0x398, 0x6dc, 0x61a, 0x31b, 0x1bf, 0x6d8, 0x7d8]
    dbar = Image.new("L", (16, 7), 1)
    pix = dbar.load()
    pos = 0
    ypos = 0
    for b in dignum:
        for i in range(16):
            pix[pos, ypos] = 0 if (b & 1) else 1
            b = b >> 1
            pos += 1
        ypos += 1
        pos = 0
    # result
    bar = Image.new("L", (114, 44), 2)
    bar.paste(vbar, (1, 1))
    bar.paste(bg, (1, 32))
    for i in range(4):
        bar.paste(dbar, (35 + i * 12, 34))
    return bar


@common.add_unittest
def dotest(outputname, nostamp):
    plane = genbar()
    palette = (0,0,0, 255,255,255) + (128,128,128)*254
    try:    
        img = Image.frombytes("P", plane.size, plane.tobytes())
    except AttributeError:
        # note: https://github.com/python-pillow/Pillow/issues/63
        img = Image.fromstring("P", plane.size, plane.tostring())
    img.putpalette(palette)

    with tempfile.NamedTemporaryFile(delete = False, suffix = ".gif") as f:
        gif1 = f.name
    with tempfile.NamedTemporaryFile(delete = False, suffix = ".gif") as f:
        gif2 = f.name

    img.save(gif1, "GIF", optimize = 0)
    img.save(gif2, "GIF", transparency = 1, optimize = 0)

    pdf = FPDF()
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)
    pdf.add_page()
    pdf.set_font('Arial', '', 16)
    pdf.write(8, "Transparency")
    pdf.ln()
    pdf.write(8, "    Transparency")
    pdf.ln()
    pdf.write(8, "        Transparency")
    pdf.ln()
    pdf.image(gif1, x = 15, y = 15)

    pdf.write(8, "Transparency")
    pdf.ln()
    pdf.write(8, "    Transparency")
    pdf.ln()
    pdf.write(8, "        Transparency")
    pdf.ln()
    pdf.image(gif2, x = 15, y = 39)

    pdf.output(outputname, 'F')

    os.unlink(gif1)
    os.unlink(gif2)
    
def main():
    return common.testmain(__file__, dotest)
    
if __name__ == "__main__":
    main()


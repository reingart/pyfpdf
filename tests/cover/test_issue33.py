"Test issue 33 (Cannot import GIF files that don't have transparency)"
#PyFPDF-cover-test:output=PDF
#PyFPDF-cover-test:fn=issue_33.pdf
#PyFPDF-cover-test:hash=be95c7ef3a5b14b5a54a52f7eaf3a9e4
#PyFPDF-cover-test:2to3=no
#PyFPDF-cover-test:pil=yes

import common # test utilities
from fpdf import FPDF, FPDF_VERSION

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
    bg = Image.new("L", (112, 1), 255)
    bg = bg.resize((112, 11))
    # stripes
    vbarnum = [0x4F43484B, 0xEE90D642, 0xF11A2735, 0xD71A]
    vbar = Image.new("L", (112, 1), 192)
    pix = vbar.load()
    pos = 0
    for b in vbarnum:
        for i in range(32):
            pix[pos, 0] = 0 if (b & 1) else 255
            b = b >> 1
            pos += 1
            if pos >= 112: break    
    vbar = vbar.resize((112, 31), Image.NEAREST)
    # digit
    dignum = [0x398, 0x6dc, 0x61a, 0x31b, 0x1bf, 0x6d8, 0x7d8]
    dbar = Image.new("L", (16, 7), 160)
    pix = dbar.load()
    pos = 0
    ypos = 0
    for b in dignum:
        for i in range(16):
            pix[pos, ypos] = 0 if (b & 1) else 255
            b = b >> 1
            pos += 1
        ypos += 1
        pos = 0
    # result
    bar = Image.new("L", (114, 44), 128)
    bar.paste(vbar, (1, 1))
    bar.paste(bg, (1, 32))
    for i in range(4):
        bar.paste(dbar, (35 + i * 12, 34))
    return bar


def dotest(outputname, nostamp = False):
    plane = genbar()
    pal_image = Image.new("P", (1,1))
    pal_image.putpalette( (0,0,0, 255,255,255) + (128,128,128)*254)

    img = Image.merge("RGB", (plane, plane, plane))
    img = img.quantize(palette = pal_image)

    f = tempfile.NamedTemporaryFile(delete = False, suffix = ".gif")
    gif1 = f.name
    f.close()
    f = tempfile.NamedTemporaryFile(delete = False, suffix = ".gif")
    gif2 = f.name
    f.close()

    img.save(gif1, "GIF")
    img.save(gif2, "GIF", transparency = 1)


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
    si = common.readcoverinfo(__file__)
    da = common.parsetestargs(sys.argv, si["fn"])
    if not common.checkenv(si, da):
        return
    dotest(da["fn"], da["autotest"] or da["check"])
    common.checkresult(si, da)
    
if __name__ == "__main__":
    main()

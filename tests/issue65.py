"Test issue 65: twitter.png error (urlopen, transparency, internal regex error)"

from fpdf import FPDF, FPDF_VERSION

pdf=FPDF()
pdf.compress = False
pdf.add_page()
png = "https://g.twimg.com/Twitter_logo_blue.png"
pdf.image(png, x = 15, y = 15)

fn = 'issue65.pdf'
pdf.output(fn,'F')

import os
try:
    os.startfile(fn)
except:
    os.system("xdg-open \"%s\"" % fn)

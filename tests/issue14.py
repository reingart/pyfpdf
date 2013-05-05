"Test images flow mode (cell-like, trigger page breaks)"

from fpdf import FPDF, FPDF_VERSION

print FPDF_VERSION

pdf=FPDF()
pdf.add_page()
for i in range(1,41):
    # for flow mode, do not pass x or y:
    pdf.image('../tutorial/logo_pb.png')

fn = 'issue14.pdf'
pdf.output(fn,'F')
import os
try:
    os.startfile(fn)
except:
    os.system("xdg-open \"%s\"" % fn)

"Tests new dashed line feature (issue 35)"

from fpdf import FPDF

import os

pdf=FPDF()
pdf.add_page()

pdf.dashed_line(10, 10, 110, 10)
pdf.dashed_line(10, 20, 110, 20, 5, 5)
pdf.dashed_line(10, 30, 110, 30, 1, 10)

fn = 'dashed_line_issue35.pdf'
pdf.output(fn,'F')
os.startfile(fn)
    

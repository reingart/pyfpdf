from fpdf import FPDF

pdf = FPDF()
pdf.add_page()

# Add a Unicode font (uses UTF-8)
pdf.add_font('DejaVu','','DejaVuSansCondensed.ttf',uni=True)
pdf.set_font('DejaVu','',14)

# Load a UTF-8 string from a file and print it
txt = open('HelloWorld.txt').read()
pdf.write(8, txt)

# Select a standard font (uses windows-1252)
pdf.set_font('Arial','',14)
pdf.ln(10)
pdf.write(5, 'The file size of this PDF is only 12 KB.')

pdf.output('ex.pdf','F')
import os
os.system("evince ex.pdf")

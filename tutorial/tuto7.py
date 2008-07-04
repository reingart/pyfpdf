from FPDF import *

pdf=FPDF()
pdf.AddFont('Calligrapher','','calligra.py')
pdf.AddPage()
pdf.SetFont('Calligrapher','',35)
pdf.Cell(0,10,'Enjoy new fonts with FPDF!')
pdf.Output('tuto7.pdf','F')

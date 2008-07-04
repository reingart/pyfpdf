from FPDF import *

pdf=FPDF()
pdf.AddPage()
pdf.SetFont('Arial','B',16)
pdf.Cell(40,10,'Hello World!')
pdf.Output('tuto1.pdf','F')

from FPDF import *

class PDF(FPDF):
	def Header(this):
		# Logo
		this.Image('logo_pb.png',10,8,33)
		# Arial bold 15
		this.SetFont('Arial','B',15)
		# Move to the right
		this.Cell(80)
		# Title
		this.Cell(30,10,'Title',1,0,'C')
		# Line break
		this.Ln(20)

	# Page footer
	def Footer(this):
		# Position at 1.5 cm from bottom
		this.SetY(-15)
		# Arial italic 8
		this.SetFont('Arial','I',8)
		# Page number
		this.Cell(0,10,'Page '+str(this.PageNo())+'/{nb}',0,0,'C')

# Instanciation of inherited class
pdf=PDF()
pdf.AliasNbPages()
pdf.AddPage()
pdf.SetFont('Times','',12)
for i in range(1,41):
	pdf.Cell(0,10,'Printing line number '+str(i),0,1)
pdf.Output('tuto2.pdf','F')

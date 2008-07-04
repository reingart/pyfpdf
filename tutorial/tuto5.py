from FPDF import *

class PDF(FPDF):
	#Load data
	def LoadData(this, name):
		#Read file lines
		data=[]
		for line in file(name):
			data += [line[:-1].split(';')]
		return data

	#Simple table
	def BasicTable(this,header,data):
		#Header
		for col in header:
			this.Cell(40,7,col,1)
		this.Ln()
		#Data
		for row in data:
			for col in row:
				this.Cell(40,6,col,1)
			this.Ln()

	#Better table
	def ImprovedTable(this,header,data):
		#Column widths
		w=[40,35,40,45]
		#Header
		for i in range(0,len(header)):
			this.Cell(w[i],7,header[i],1,0,'C')
		this.Ln()
		#Data
		for row in data:
			this.Cell(w[0],6,row[0],'LR')
			this.Cell(w[1],6,row[1],'LR')
			this.Cell(w[2],6,row[2],'LR',0,'R')
			this.Cell(w[3],6,row[3],'LR',0,'R')
			this.Ln()
		#Closure line
		this.Cell(sum(w),0,'','T')

	#Colored table
	def FancyTable(this,header,data):
		#Colors, line width and bold font
		this.SetFillColor(255,0,0)
		this.SetTextColor(255)
		this.SetDrawColor(128,0,0)
		this.SetLineWidth(.3)
		this.SetFont('','B')
		#Header
		w=[40,35,40,45]
		for i in range(0,len(header)):
			this.Cell(w[i],7,header[i],1,0,'C',1)
		this.Ln()
		#Color and font restoration
		this.SetFillColor(224,235,255)
		this.SetTextColor(0)
		this.SetFont('')
		#Data
		fill=0
		for row in data:
			this.Cell(w[0],6,row[0],'LR',0,'L',fill)
			this.Cell(w[1],6,row[1],'LR',0,'L',fill)
			this.Cell(w[2],6,row[2],'LR',0,'R',fill)
			this.Cell(w[3],6,row[3],'LR',0,'R',fill)
			this.Ln()
			fill=not fill
		this.Cell(sum(w),0,'','T')

pdf=PDF()
#Column titles
header=['Country','Capital','Area (sq km)','Pop. (thousands)']
#Data loading
data=pdf.LoadData('countries.txt')
pdf.SetFont('Arial','',14)
pdf.AddPage()
pdf.BasicTable(header,data)
pdf.AddPage()
pdf.ImprovedTable(header,data)
pdf.AddPage()
pdf.FancyTable(header,data)
pdf.Output('tuto5.pdf','F')

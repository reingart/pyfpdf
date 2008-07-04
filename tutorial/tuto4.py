from FPDF import *

class PDF(FPDF):
#Current column
	col=0
#Ordinate of column start
	y0=0
	def Header(this):
		#Page header
		this.SetFont('Arial','B',15)
		w=this.GetStringWidth(title)+6
		this.SetX((210-w)/2.0)
		this.SetDrawColor(0,80,180)
		this.SetFillColor(230,230,0)
		this.SetTextColor(220,50,50)
		this.SetLineWidth(1)
		this.Cell(w,9,title,1,1,'C',1)
		this.Ln(10)
		#Save ordinate
		this.y0=this.GetY()

	def Footer(this):
		#Page footer
		this.SetY(-15)
		this.SetFont('Arial','I',8)
		this.SetTextColor(128)
		this.Cell(0,10,'Page '+str(this.PageNo()),0,0,'C')

	def SetCol(this, col):
		#Set position at a given column
		this.col=col
		x=10+col*65.0
		this.SetLeftMargin(x)
		this.SetX(x)

	def AcceptPageBreak(this):
		#Method accepting or not automatic page break
		if(this.col<2):
			#Go to next column
			this.SetCol(this.col+1)
			#Set ordinate to top
			this.SetY(this.y0)
			#Keep on page
			return 0
		else:
			#Go back to first column
			this.SetCol(0)
			#Page break
			return 1

	def ChapterTitle(this,num,label):
		#Title
		this.SetFont('Arial','',12)
		this.SetFillColor(200,220,255)
		this.Cell(0,6,"Chapter %d : %s"%(num,label),0,1,'L',1)
		this.Ln(4)
		#Save ordinate
		this.y0=this.GetY()

	def ChapterBody(this, fichier):
		#Read text file
		txt=file(fichier).read()
		#Font
		this.SetFont('Times','',12)
		#Output text in a 6 cm width column
		this.MultiCell(60,5,txt)
		this.Ln()
		#Mention
		this.SetFont('','I')
		this.Cell(0,5,'(end of excerpt)')
		#Go back to first column
		this.SetCol(0)

	def PrintChapter(this,num,title,name):
		#Add chapter
		this.AddPage()
		this.ChapterTitle(num,title)
		this.ChapterBody(name)

pdf=PDF()
title='20000 Leagues Under the Seas'
pdf.SetTitle(title)
pdf.SetAuthor('Jules Verne')
pdf.PrintChapter(1,'A RUNAWAY REEF','20k_c1.txt')
pdf.PrintChapter(2,'THE PROS AND CONS','20k_c2.txt')
pdf.Output('tuto4.pdf','F')

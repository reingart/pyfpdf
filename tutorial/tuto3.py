from FPDF import *

title='20000 Leagues Under the Seas'

class PDF(FPDF):
	def Header(this):
		#Arial bold 15
		this.SetFont('Arial','B',15)
		#Calculate width of title and position
		w=this.GetStringWidth(title)+6
		this.SetX((210-w)/2)
		#Colors of frame, background and text
		this.SetDrawColor(0,80,180)
		this.SetFillColor(230,230,0)
		this.SetTextColor(220,50,50)
		#Thickness of frame (1 mm)
		this.SetLineWidth(1)
		#Title
		this.Cell(w,9,title,1,1,'C',1)
		#Line break
		this.Ln(10)

	def Footer(this):
		#Position at 1.5 cm from bottom
		this.SetY(-15)
		#Arial italic 8
		this.SetFont('Arial','I',8)
		#Text color in gray
		this.SetTextColor(128)
		#Page number
		this.Cell(0,10,'Page '+str(this.PageNo()),0,0,'C')

	def ChapterTitle(this,num,label):
		#Arial 12
		this.SetFont('Arial','',12)
		#Background color
		this.SetFillColor(200,220,255)
		#Title
		this.Cell(0,6,"Chapter %d : %s"%(num,label),0,1,'L',1)
		#Line break
		this.Ln(4)

	def ChapterBody(this,name):
		#Read text file
		txt=file(name).read()
		#Times 12
		this.SetFont('Times','',12)
		#Output justified text
		this.MultiCell(0,5,txt)
		#Line break
		this.Ln()
		#Mention in italics
		this.SetFont('','I')
		this.Cell(0,5,'(end of excerpt)')

	def PrintChapter(this,num,title,name):
		this.AddPage()
		this.ChapterTitle(num,title)
		this.ChapterBody(name)


pdf=PDF()
pdf.SetTitle(title)
pdf.SetAuthor('Jules Verne')
pdf.PrintChapter(1,'A RUNAWAY REEF','20k_c1.txt')
pdf.PrintChapter(2,'THE PROS AND CONS','20k_c2.txt')
pdf.Output('tuto3.pdf','F')

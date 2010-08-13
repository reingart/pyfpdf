from FPDF import *

class TOC(FPDF):
	def __init__(this, orientation='P',unit='mm',format='A4'):
		this._toc=[]
		this._numbering=0
		this._numberingFooter=0
		this._numPageNum=1
		FPDF.__init__(this,orientation,unit,format)

	def AddPage(this,orientation=''):
		FPDF.AddPage(this,orientation)
		if(this._numbering):
			this._numPageNum+=1

	def startPageNums(this):
		this._numbering=1
		this._numberingFooter=1

	def stopPageNums(this):
		this._numbering=0

	def numPageNo(this):
		return this._numPageNum

	def TOC_Entry(this,txt,level=0):
		this._toc+=[{'t':txt,'l':level,'p':this.numPageNo()}]

	def insertTOC(this,location=1,labelSize=20,entrySize=10,tocfont='Times',label='Table of Contents'):
		#make toc at end
		this.stopPageNums()
		this.AddPage()
		tocstart=this.page

		this.SetFont(tocfont,'B',labelSize)
		this.Cell(0,5,label,0,1,'C')
		this.Ln(10)

		for t in this._toc:
			#Offset
			level=t['l']
			if(level>0):
				this.Cell(level*8)
			weight=''
			if(level==0):
				weight='B'
			Str=t['t']
			this.SetFont(tocfont,weight,entrySize)
			strsize=this.GetStringWidth(Str)
			this.Cell(strsize+2,this.FontSize+2,Str)

			#Filling dots
			this.SetFont(tocfont,'',entrySize)
			PageCellSize=this.GetStringWidth(str(t['p']))+2
			w=this.w-this.lMargin-this.rMargin-PageCellSize-(level*8)-(strsize+2)
			nb=w/this.GetStringWidth('.')
			dots=str_repeat('.',nb)
			this.Cell(w,this.FontSize+2,dots,0,0,'R')

			#Page number
			this.Cell(PageCellSize,this.FontSize+2,str(t['p']),0,1,'R')

		#grab it and move to selected location
		n=this.page
		n_toc = n - tocstart + 1
		last = []

		#store toc pages
		for i in xrange(tocstart,n+1):
			last+=[this.pages[i]]

		#move pages
		for i in xrange(tocstart-1,location-1,-1):
		#~ for(i=tocstart - 1;i>=location-1;i--)
			this.pages[i+n_toc]=this.pages[i]

		#Put toc pages at insert point
		for i in xrange(0,n_toc):
			this.pages[location + i]=last[i]

	def Footer(this):
		if(this._numberingFooter==0):
			return
		#Go to 1.5 cm from bottom
		this.SetY(-15)
		#Select Arial italic 8
		this.SetFont('Arial','I',8)
		this.Cell(0,7,str(this.numPageNo()),0,0,'C');
		if(this._numbering==0):
			this._numberingFooter=0

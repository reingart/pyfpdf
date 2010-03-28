from FPDF import *

class Bookmark(FPDF):
	def __init__(this,orientation='P',unit='mm',format='A4'):
		FPDF.__init__(this,orientation,unit,format)
		this.outlines=[]
		this.OutlineRoot=None

	def Bookmark(this,txt,level=0,y=0):
		if(y==-1):
			y=this.GetY()
		this.outlines+=[{'t':txt,'l':level,'y':y,'p':this.PageNo()}]

	def _putbookmarks(this):
		nb=count(this.outlines)
		if(nb==0):
			return
		lru={}
		level=0
		for i in range(len(this.outlines)):
			o=this.outlines[i]
			if(o['l']>0):
				parent=lru[o['l']-1]
				#Set parent and last pointers
				this.outlines[i]['parent']=parent
				this.outlines[parent]['last']=i
				if(o['l']>level):
					#Level increasing: set first pointer
					this.outlines[parent]['first']=i
			else:
				this.outlines[i]['parent']=nb
			if(o['l']<=level and i>0):
				#Set prev and next pointers
				prev=lru[o['l']]
				this.outlines[prev]['next']=i
				this.outlines[i]['prev']=prev
			lru[o['l']]=i
			level=o['l']
		#Outline items
		n=this.n+1
		for i in range(len(this.outlines)):
			o=this.outlines[i]
			this._newobj()
			this._out('<</Title '+this._textstring(o['t']))
			this._out('/Parent '+str(n+o['parent'])+' 0 R')
			if 'prev' in o:
				this._out('/Prev '+str(n+o['prev'])+' 0 R')
			if 'next' in o:
				this._out('/Next '+str(n+o['next'])+' 0 R')
			if 'first' in o:
				this._out('/First '+str(n+o['first'])+' 0 R')
			if 'last' in o:
				this._out('/Last '+str(n+o['last'])+' 0 R')
			this._out(sprintf('/Dest [%d 0 R /XYZ 0 %.2f null]',1+2*o['p'],(this.h-o['y'])*this.k))
			this._out('/Count 0>>')
			this._out('endobj')
		#Outline root
		this._newobj()
		this.OutlineRoot=this.n
		this._out('<</Type /Outlines /First '+str(n)+' 0 R')
		this._out('/Last '+str(n+lru[0])+' 0 R>>')
		this._out('endobj')


	def _putresources(this):
	    FPDF._putresources(this)
	    this._putbookmarks()

	def _putcatalog(this):
		FPDF._putcatalog(this)
		if(count(this.outlines)>0):
			this._out('/Outlines '+str(this.OutlineRoot)+' 0 R')
			this._out('/PageMode /UseOutlines')

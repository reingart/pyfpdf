# -*- coding: iso-8859-1 -*-
# ******************************************************************************
# * Software: FPDF                                                               *
# * Version:  1.53                                                               *
# * Date:     2004-12-31                                                         *
# * Author:   Olivier PLATHEY                                                    *
# * License:  Freeware                                                           *
# *                                                                              *
# * You may use and modify this software as you wish.                            *
# * Ported to Python 2.4 by Max (maxpat78@yahoo.it) on 2006-05                   *
# * NOTE: 'I' and 'D' destinations are disabled, and simply print to STDOUT      *
# * ALSO IT CAN'T HANDLE JPEG FILES, SINCE WE HAVEN'T PHP'S GetImageSize()	 *
# *******************************************************************************/
from PHPutils import *
from datetime import datetime
import os, sys, zlib, struct

# Global variables
FPDF_VERSION='1.53'
FPDF_FONT_DIR=os.path.join(os.path.dirname(__file__),'font')
fpdf_charwidths = {}

class FPDF:
#Private properties
#~ page;               #current page number
#~ n;                  #current object number
#~ offsets;            #array of object offsets
#~ buffer;             #buffer holding in-memory PDF
#~ pages;              #array containing pages
#~ state;              #current document state
#~ compress;           #compression flag
#~ DefOrientation;     #default orientation
#~ CurOrientation;     #current orientation
#~ OrientationChanges; #array indicating orientation changes
#~ k;                  #scale factor (number of points in user unit)
#~ fwPt,fhPt;         #dimensions of page format in points
#~ fw,fh;             #dimensions of page format in user unit
#~ wPt,hPt;           #current dimensions of page in points
#~ w,h;               #current dimensions of page in user unit
#~ lMargin;            #left margin
#~ tMargin;            #top margin
#~ rMargin;            #right margin
#~ bMargin;            #page break margin
#~ cMargin;            #cell margin
#~ x,y;               #current position in user unit for cell positioning
#~ lasth;              #height of last cell printed
#~ LineWidth;          #line width in user unit
#~ CoreFonts;          #array of standard font names
#~ fonts;              #array of used fonts
#~ FontFiles;          #array of font files
#~ diffs;              #array of encoding differences
#~ images;             #array of used images
#~ PageLinks;          #array of links in pages
#~ links;              #array of internal links
#~ FontFamily;         #current font family
#~ FontStyle;          #current font style
#~ underline;          #underlining flag
#~ CurrentFont;        #current font info
#~ FontSizePt;         #current font size in points
#~ FontSize;           #current font size in user unit
#~ DrawColor;          #commands for drawing color
#~ FillColor;          #commands for filling color
#~ TextColor;          #commands for text color
#~ ColorFlag;          #indicates whether fill and text colors are different
#~ ws;                 #word spacing
#~ AutoPageBreak;      #automatic page breaking
#~ PageBreakTrigger;   #threshold used to trigger page breaks
#~ InFooter;           #flag set when processing footer
#~ ZoomMode;           #zoom display mode
#~ LayoutMode;         #layout display mode
#~ title;              #title
#~ subject;            #subject
#~ author;             #author
#~ keywords;           #keywords
#~ creator;            #creator
#~ AliasNbPages;       #alias for total number of pages
#~ PDFVersion;         #PDF version number

# ******************************************************************************
# *                                                                              *
# *                               Public methods                                 *
# *                                                                              *
# *******************************************************************************/
	def __init__(this, orientation='P',unit='mm',format='A4'):
		#Some checks
		this._dochecks()
		#Initialization of properties
		this.offsets={}
		this.page=0
		this.n=2
		this.buffer=''
		this.pages={}
		this.OrientationChanges={}
		this.state=0
		this.fonts={}
		this.FontFiles={}
		this.diffs=[]
		this.images={}
		this.PageLinks={}
		this.links={}
		this.InFooter=0
		this.lastw=0
		this.lasth=0
		this.FontFamily=''
		this.FontStyle=''
		this.FontSizePt=12
		this.underline=0
		this.DrawColor='0 G'
		this.FillColor='0 g'
		this.TextColor='0 g'
		this.ColorFlag=0
		this.ws=0
		#Standard fonts
		this.CoreFonts={'courier':'Courier','courierB':'Courier-Bold','courierI':'Courier-Oblique','courierBI':'Courier-BoldOblique',
			'helvetica':'Helvetica','helveticaB':'Helvetica-Bold','helveticaI':'Helvetica-Oblique','helveticaBI':'Helvetica-BoldOblique',
			'times':'Times-Roman','timesB':'Times-Bold','timesI':'Times-Italic','timesBI':'Times-BoldItalic',
			'symbol':'Symbol','zapfdingbats':'ZapfDingbats'}
		#Scale factor
		if(unit=='pt'):
			this.k=1
		elif(unit=='mm'):
			this.k=72/25.4
		elif(unit=='cm'):
			this.k=72/2.54
		elif(unit=='in'):
			this.k=72
		else:
			this.Error('Incorrect unit: '+unit)
		#Page format
		if(is_string(format)):
			format=strtolower(format)
			if(format=='a3'):
				format=(841.89,1190.55)
			elif(format=='a4'):
				format=(595.28,841.89)
			elif(format=='a5'):
				format=(420.94,595.28)
			elif(format=='letter'):
				format=(612,792)
			elif(format=='legal'):
				format=(612,1008)
			else:
				this.Error('Unknown page format: '+format)
			this.fwPt=format[0]
			this.fhPt=format[1]
		else:
			this.fwPt=format[0]*this.k
			this.fhPt=format[1]*this.k
		this.fw=this.fwPt/this.k
		this.fh=this.fhPt/this.k
		#Page orientation
		orientation=strtolower(orientation)
		if(orientation=='p' or orientation=='portrait'):
			this.DefOrientation='P'
			this.wPt=this.fwPt
			this.hPt=this.fhPt
		elif(orientation=='l' or orientation=='landscape'):
			this.DefOrientation='L'
			this.wPt=this.fhPt
			this.hPt=this.fwPt
		else:
			this.Error('Incorrect orientation: '+orientation)
		this.CurOrientation=this.DefOrientation
		this.w=this.wPt/this.k
		this.h=this.hPt/this.k
		#Page margins (1 cm)
		margin=28.35/this.k
		this.SetMargins(margin,margin)
		#Interior cell margin (1 mm)
		this.cMargin=margin/10.0
		#Line width (0.2 mm)
		this.LineWidth=.567/this.k
		#Automatic page break
		this.SetAutoPageBreak(1,2*margin)
		#Full width display mode
		this.SetDisplayMode('fullwidth')
		#Enable compression
		this.SetCompression(1)
		#Set default PDF version number
		this.PDFVersion='1.3'

	def SetMargins(this, left,top,right=-1):
		#Set left, top and right margins
		this.lMargin=left
		this.tMargin=top
		if(right==-1):
			right=left
		this.rMargin=right

	def SetLeftMargin(this, margin):
		#Set left margin
		this.lMargin=margin
		if(this.page>0 and this.x<margin):
			this.x=margin

	def SetTopMargin(this, margin):
		#Set top margin
		this.tMargin=margin

	def SetRightMargin(this, margin):
		#Set right margin
		this.rMargin=margin

	def SetAutoPageBreak(this, auto,margin=0):
		#Set auto page break mode and triggering margin
		this.AutoPageBreak=auto
		this.bMargin=margin
		this.PageBreakTrigger=this.h-margin

	def SetDisplayMode(this, zoom,layout='continuous'):
		#Set display mode in viewer
		if(zoom=='fullpage' or zoom=='fullwidth' or zoom=='real' or zoom=='default' or not is_string(zoom)):
			this.ZoomMode=zoom
		else:
			this.Error('Incorrect zoom display mode: '+zoom)
		if(layout=='single' or layout=='continuous' or layout=='two' or layout=='default'):
			this.LayoutMode=layout
		else:
			this.Error('Incorrect layout display mode: '+layout)

	def SetCompression(this, compress):
		#Set page compression
		this.compress=compress

	def SetTitle(this, title):
		#Title of document
		this.title=title

	def SetSubject(this, subject):
		#Subject of document
		this.subject=subject

	def SetAuthor(this, author):
		#Author of document
		this.author=author

	def SetKeywords(this, keywords):
		#Keywords of document
		this.keywords=keywords

	def SetCreator(this, creator):
		#Creator of document
		this.creator=creator

	def AliasNbPages(this, alias='{nb}'):
		#Define an alias for total number of pages
		this.StrAliasNbPages=alias

	def Error(this, msg):
		#Fatal error
		print 'FPDF error: '+msg
		sys.exit(-1)

	def Open(this):
		#Begin document
		this.state=1

	def Close(this):
		#Terminate document
		if(this.state==3):
			return
		if(this.page==0):
			this.AddPage()
		#Page footer
		this.InFooter=1
		this.Footer()
		this.InFooter=0
		#Close page
		this._endpage()
		#Close document
		this._enddoc()

	def AddPage(this, orientation=''):
		#Start a new page
		if(this.state==0):
			this.Open()
		family=this.FontFamily
		if this.underline:
			style = this.FontStyle + 'U'
		else:
			style = this.FontStyle
		size=this.FontSizePt
		lw=this.LineWidth
		dc=this.DrawColor
		fc=this.FillColor
		tc=this.TextColor
		cf=this.ColorFlag
		if(this.page>0):
			#Page footer
			this.InFooter=1
			this.Footer()
			this.InFooter=0
			#Close page
			this._endpage()
		#Start new page
		this._beginpage(orientation)
		#Set line cap style to square
		this._out('2 J')
		#Set line width
		this.LineWidth=lw
		this._out(sprintf('%.2f w',lw*this.k))
		#Set font
		if(family):
			this.SetFont(family,style,size)
		#Set colors
		this.DrawColor=dc
		if(dc!='0 G'):
			this._out(dc)
		this.FillColor=fc
		if(fc!='0 g'):
			this._out(fc)
		this.TextColor=tc
		this.ColorFlag=cf
		#Page header
		this.Header()
		#Restore line width
		if(this.LineWidth!=lw):
			this.LineWidth=lw
			this._out(sprintf('%.2f w',lw*this.k))
		#Restore font
		if(family):
			this.SetFont(family,style,size)
		#Restore colors
		if(this.DrawColor!=dc):
			this.DrawColor=dc
			this._out(dc)
		if(this.FillColor!=fc):
			this.FillColor=fc
			this._out(fc)
		this.TextColor=tc
		this.ColorFlag=cf

	def Header(this):
		#To be implemented in your own inherited class
		pass

	def Footer(this):
		#To be implemented in your own inherited class
		pass

	def PageNo(this):
		#Get current page number
		return this.page

	def SetDrawColor(this, r,g=-1,b=-1):
		#Set color for all stroking operations
		if((r==0 and g==0 and b==0) or g==-1):
			this.DrawColor=sprintf('%.3f G',r/255.0)
		else:
			this.DrawColor=sprintf('%.3f %.3f %.3f RG',r/255.0,g/255.0,b/255.0)
		if(this.page>0):
			this._out(this.DrawColor)

	def SetFillColor(this,r,g=-1,b=-1):
		#Set color for all filling operations
		if((r==0 and g==0 and b==0) or g==-1):
			this.FillColor=sprintf('%.3f g',r/255.0)
		else:
			this.FillColor=sprintf('%.3f %.3f %.3f rg',r/255.0,g/255.0,b/255.0)
		this.ColorFlag=(this.FillColor!=this.TextColor)
		if(this.page>0):
			this._out(this.FillColor)

	def SetTextColor(this, r,g=-1,b=-1):
		#Set color for text
		if((r==0 and g==0 and b==0) or g==-1):
			this.TextColor=sprintf('%.3f g',r/255.0)
		else:
			this.TextColor=sprintf('%.3f %.3f %.3f rg',r/255.0,g/255.0,b/255.0)
		this.ColorFlag=(this.FillColor!=this.TextColor)

	def GetStringWidth(this, s):
		#Get width of a string in the current font
		cw=this.CurrentFont['cw']
		w=0
		l=len(s)
		for i in xrange(0, l):
			w += cw[s[i]]
		return w*this.FontSize/1000.0

	def SetLineWidth(this, width):
		#Set line width
		this.LineWidth=width
		if(this.page>0):
			this._out(sprintf('%.2f w',width*this.k))

	def Line(this, x1,y1,x2,y2):
		#Draw a line
		this._out(sprintf('%.2f %.2f m %.2f %.2f l S',x1*this.k,(this.h-y1)*this.k,x2*this.k,(this.h-y2)*this.k))

	def Rect(this, x,y,w,h,style=''):
		#Draw a rectangle
		if(style=='F'):
			op='f'
		elif(style=='FD' or style=='DF'):
			op='B'
		else:
			op='S'
		this._out(sprintf('%.2f %.2f %.2f %.2f re %s',x*this.k,(this.h-y)*this.k,w*this.k,-h*this.k,op))

	def AddFont(this, family,style='',fname=''):
		#Add a TrueType or Type1 font
		family=strtolower(family)
		if(fname==''):
			fname=str_replace(' ','',family).lower(style)+'.py'
		fname=os.path.join(FPDF_FONT_DIR,fname)
		if(family=='arial'):
			family='helvetica'
		style=strtoupper(style)
		if(style=='IB'):
			style='BI'
		fontkey=family+style
		if fontkey in this.fonts:
			this.Error('Font already added: '+family+' '+style)
		execfile(fname, globals(), globals())
		if 'name' not in globals():
			this.Error('Could not include font definition file')
		i=len(this.fonts)+1
		this.fonts[fontkey]={'i':i,'type':type,'name':name,'desc':desc,'up':up,'ut':ut,'cw':cw,'enc':enc,'file':filename}
		if(diff):
			#Search existing encodings
			d=0
			nb=len(this.diffs)
			for i in xrange(1,nb+1):
				if(this.diffs[i]==diff):
					d=i
					break
			if(d==0):
				d=nb+1
				this.diffs[d]=diff
			this.fonts[fontkey]['diff']=d
		if(filename):
			if(type=='TrueType'):
				this.FontFiles[filename]={'length1':originalsize}
			else:
				this.FontFiles[filename]={'length1':size1,'length2':size2}

	def SetFont(this, family,style='',size=0):
		#Select a font; size given in points
		family=strtolower(family)
		if(family==''):
			family=this.FontFamily
		if(family=='arial'):
			family='helvetica'
		elif(family=='symbol' or family=='zapfdingbats'):
			style=''
		style=strtoupper(style)
		if(strpos(style,'U')!=-1):
			this.underline=1
			style=str_replace('U','',style)
		else:
			this.underline=0
		if(style=='IB'):
			style='BI'
		if(size==0):
			size=this.FontSizePt
		#Test if font is already selected
		if(this.FontFamily==family and this.FontStyle==style and this.FontSizePt==size):
			return
		#Test if used for the first time
		fontkey=family+style
		if fontkey not in this.fonts:
			#Check if one of the standard fonts
			if fontkey in this.CoreFonts:
				if fontkey not in fpdf_charwidths:
					#Load metric file
					name=os.path.join(FPDF_FONT_DIR,family)
					if(family=='times' or family=='helvetica'):
						name+=strtolower(style)
					execfile(name+'.py')
					if fontkey not in fpdf_charwidths:
						this.Error('Could not include font metric file for'+fontkey)
				i=len(this.fonts)+1
				this.fonts[fontkey]={'i':i,'type':'core','name':this.CoreFonts[fontkey],'up':-100,'ut':50,'cw':fpdf_charwidths[fontkey]}
			else:
				this.Error('Undefined font: '+family+' '+style)
		#Select it
		this.FontFamily=family
		this.FontStyle=style
		this.FontSizePt=size
		this.FontSize=size/this.k
		this.CurrentFont=this.fonts[fontkey]
		if(this.page>0):
			this._out(sprintf('BT /F%d %.2f Tf ET',this.CurrentFont['i'],this.FontSizePt))

	def SetFontSize(this, size):
		#Set font size in points
		if(this.FontSizePt==size):
			return
		this.FontSizePt=size
		this.FontSize=size/this.k
		if(this.page>0):
			this._out(sprintf('BT /F%d %.2f Tf ET',this.CurrentFont['i'],this.FontSizePt))

	def AddLink(this):
		#Create a new internal link
		n=len(this.links)+1
		this.links[n]=(0,0)
		return n

	def SetLink(this, link,y=0,page=-1):
		#Set destination of internal link
		if(y==-1):
			y=this.y
		if(page==-1):
			page=this.page
		this.links[link]=[page,y]

	def Link(this, x,y,w,h,link):
		#Put a link on the page
		if not this.page in this.PageLinks:
			this.PageLinks[this.page] = []
		this.PageLinks[this.page] += [(x*this.k,this.hPt-y*this.k,w*this.k,h*this.k,link),]

	def Text(this, x,y,txt):
		#Output a string
		s=sprintf('BT %.2f %.2f Td (%s) Tj ET',x*this.k,(this.h-y)*this.k,this._escape(txt))
		if(this.underline and txt!=''):
			s+=' '+this._dounderline(x,y,txt)
		if(this.ColorFlag):
			s='q '+this.TextColor+' '+s+' Q'
		this._out(s)

	def AcceptPageBreak(this):
		#Accept automatic page break or not
		return this.AutoPageBreak

	def Cell(this, w,h=0,txt='',border=0,ln=0,align='',fill=0,link=''):
		#Output a cell
		k=this.k
		if(this.y+h>this.PageBreakTrigger and not this.InFooter and this.AcceptPageBreak()):
			#Automatic page break
			x=this.x
			ws=this.ws
			if(ws>0):
				this.ws=0
				this._out('0 Tw')
			this.AddPage(this.CurOrientation)
			this.x=x
			if(ws>0):
				this.ws=ws
				this._out(sprintf('%.3f Tw',ws*k))
		if(w==0):
			w=this.w-this.rMargin-this.x
		s=''
		if(fill==1 or border==1):
			if(fill==1):
				if border==1:
					op='B'
				else:
					op='f'
			else:
				op='S'
			s=sprintf('%.2f %.2f %.2f %.2f re %s ',this.x*k,(this.h-this.y)*k,w*k,-h*k,op)
		if(is_string(border)):
			x=this.x
			y=this.y
			if(strpos(border,'L')!=-1):
				s+=sprintf('%.2f %.2f m %.2f %.2f l S ',x*k,(this.h-y)*k,x*k,(this.h-(y+h))*k)
			if(strpos(border,'T')!=-1):
				s+=sprintf('%.2f %.2f m %.2f %.2f l S ',x*k,(this.h-y)*k,(x+w)*k,(this.h-y)*k)
			if(strpos(border,'R')!=-1):
				s+=sprintf('%.2f %.2f m %.2f %.2f l S ',(x+w)*k,(this.h-y)*k,(x+w)*k,(this.h-(y+h))*k)
			if(strpos(border,'B')!=-1):
				s+=sprintf('%.2f %.2f m %.2f %.2f l S ',x*k,(this.h-(y+h))*k,(x+w)*k,(this.h-(y+h))*k)
		if(txt!=''):
			if(align=='R'):
				dx=w-this.cMargin-this.GetStringWidth(txt)
			elif(align=='C'):
				dx=(w-this.GetStringWidth(txt))/2.0
			else:
				dx=this.cMargin
			if(this.ColorFlag):
				s+='q '+this.TextColor+' '
			txt2=str_replace(')','\\)',str_replace('(','\\(',str_replace('\\','\\\\',txt)))
			s+=sprintf('BT %.2f %.2f Td (%s) Tj ET',(this.x+dx)*k,(this.h-(this.y+.5*h+.3*this.FontSize))*k,txt2)
			if(this.underline):
				s+=' '+this._dounderline(this.x+dx,this.y+.5*h+.3*this.FontSize,txt)
			if(this.ColorFlag):
				s+=' Q'
			if(link):
				this.Link(this.x+dx,this.y+.5*h-.5*this.FontSize,this.GetStringWidth(txt),this.FontSize,link)
		if(s):
			this._out(s)
		this.lasth=h
		if(ln>0):
			#Go to next line
			this.y+=h
			if(ln==1):
				this.x=this.lMargin
		else:
			this.x+=w

	def MultiCell(this, w,h,txt,border=0,align='J',fill=0):
		#Output text with automatic or explicit line breaks
		cw=this.CurrentFont['cw']
		if(w==0):
			w=this.w-this.rMargin-this.x
		wmax=(w-2*this.cMargin)*1000.0/this.FontSize
		s=str_replace("\r",'',txt)
		nb=len(s)
		if(nb>0 and s[nb-1]=="\n"):
			nb-=1
		b=0
		if(border):
			if(border==1):
				border='LTRB'
				b='LRT'
				b2='LR'
			else:
				b2=''
				if(strpos(border,'L')!=-1):
					b2+='L'
				if(strpos(border,'R')!=-1):
					b2+='R'
				if (strpos(border,'T')!=-1):
					b=b2+'T'
				else:
					b=b2
		sep=-1
		i=0
		j=0
		l=0
		ns=0
		nl=1
		while(i<nb):
			#Get next character
			c=s[i]
			if(c=="\n"):
				#Explicit line break
				if(this.ws>0):
					this.ws=0
					this._out('0 Tw')
				this.Cell(w,h,substr(s,j,i-j),b,2,align,fill)
				i+=1
				sep=-1
				j=i
				l=0
				ns=0
				nl+=1
				if(border and nl==2):
					b=b2
				continue
			if(c==' '):
				sep=i
				ls=l
				ns+=1
			l+=cw[c]
			if(l>wmax):
				#Automatic line break
				if(sep==-1):
					if(i==j):
						i+=1
					if(this.ws>0):
						this.ws=0
						this._out('0 Tw')
					this.Cell(w,h,substr(s,j,i-j),b,2,align,fill)
				else:
					if(align=='J'):
						if ns>1:
							this.ws=(wmax-ls)/1000.0*this.FontSize/(ns-1)
						else:
							this.ws=0
						this._out(sprintf('%.3f Tw',this.ws*this.k))
					this.Cell(w,h,substr(s,j,sep-j),b,2,align,fill)
					i=sep+1
				sep=-1
				j=i
				l=0
				ns=0
				nl+=1
				if(border and nl==2):
					b=b2
			else:
				i+=1
		#Last chunk
		if(this.ws>0):
			this.ws=0
			this._out('0 Tw')
		if(border and strpos(border,'B')!=-1):
			b+='B'
		this.Cell(w,h,substr(s,j,i-j),b,2,align,fill)
		this.x=this.lMargin

	def Write(this, h,txt,link=''):
		#Output text in flowing mode
		cw=this.CurrentFont['cw']
		w=this.w-this.rMargin-this.x
		wmax=(w-2*this.cMargin)*1000.0/this.FontSize
		s=str_replace("\r",'',txt)
		nb=len(s)
		sep=-1
		i=0
		j=0
		l=0
		nl=1
		while(i<nb):
			#Get next character
			c=s[i]
			if(c=="\n"):
				#Explicit line break
				this.Cell(w,h,substr(s,j,i-j),0,2,'',0,link)
				i+=1
				sep=-1
				j=i
				l=0
				if(nl==1):
					this.x=this.lMargin
					w=this.w-this.rMargin-this.x
					wmax=(w-2*this.cMargin)*1000.0/this.FontSize
				nl+=1
				continue
			if(c==' '):
				sep=i
			l+=cw[c]
			if(l>wmax):
				#Automatic line break
				if(sep==-1):
					if(this.x>this.lMargin):
						#Move to next line
						this.x=this.lMargin
						this.y+=h
						w=this.w-this.rMargin-this.x
						wmax=(w-2*this.cMargin)*1000.0/this.FontSize
						i+=1
						nl+=1
						continue
					if(i==j):
						i+=1
					this.Cell(w,h,substr(s,j,i-j),0,2,'',0,link)
				else:
					this.Cell(w,h,substr(s,j,sep-j),0,2,'',0,link)
					i=sep+1
				sep=-1
				j=i
				l=0
				if(nl==1):
					this.x=this.lMargin
					w=this.w-this.rMargin-this.x
					wmax=(w-2*this.cMargin)*1000.0/this.FontSize
				nl+=1
			else:
				i+=1
		#Last chunk
		if(i!=j):
			this.Cell(l/1000.0*this.FontSize,h,substr(s,j),0,0,'',0,link)

	def Image(this, name,x,y,w=0,h=0,type='',link=''):
		#Put an image on the page
		if not name in this.images:
			#First use of image, get info
			if(type==''):
				pos=strrpos(name,'.')
				if(not pos):
					this.Error('Image file has no extension and no type was specified: '+name)
				type=substr(name,pos+1)
			type=strtolower(type)
			if(type=='jpg' or type=='jpeg'):
				info=this._parsejpg(name)
			elif(type=='png'):
				info=this._parsepng(name)
			else:
				#Allow for additional formats
				mtd='_parse'+type
				if not hasattr(this,mtd):
					this.Error('Unsupported image type: '+type)
				info=this.mtd(name)
			info['i']=len(this.images)+1
			this.images[name]=info
		else:
			info=this.images[name]
		#Automatic width and height calculation if needed
		if(w==0 and h==0):
			#Put image at 72 dpi
			w=info['w']/this.k
			h=info['h']/this.k
		if(w==0):
			w=h*info['w']/info['h']
		if(h==0):
			h=w*info['h']/info['w']
		this._out(sprintf('q %.2f 0 0 %.2f %.2f %.2f cm /I%d Do Q',w*this.k,h*this.k,x*this.k,(this.h-(y+h))*this.k,info['i']))
		if(link):
			this.Link(x,y,w,h,link)

	def Ln(this, h=''):
		#Line feed; default value is last cell height
		this.x=this.lMargin
		if(is_string(h)):
			this.y+=this.lasth
		else:
			this.y+=h

	def GetX(this):
		#Get x position
		return this.x

	def SetX(this, x):
		#Set x position
		if(x>=0):
			this.x=x
		else:
			this.x=this.w+x

	def GetY(this):
		#Get y position
		return this.y

	def SetY(this, y):
		#Set y position and reset x
		this.x=this.lMargin
		if(y>=0):
			this.y=y
		else:
			this.y=this.h+y

	def SetXY(this, x,y):
		#Set x and y positions
		this.SetY(y)
		this.SetX(x)

	def Output(this, name='',dest=''):
		#Output PDF to some destination
		#Finish document if necessary
		if(this.state<3):
			this.Close()
		#Normalize parameters
		if(is_bool(dest)):
			if dest:
				dest='D'
			else:
				dest='F'
		dest=strtoupper(dest)
		if(dest==''):
			if(name==''):
				name='doc.pdf'
				dest='I'
			else:
				dest='F'
		if dest=='I':
			#Send to standard output
			#~ if(ob_get_contents()):
				#~ this.Error('Some data has already been output, can\'t send PDF file')
			#~ if(php_sapi_name()!='cli'):
				#~ #We send to a browser
				#~ header('Content-Type: application/pdf')
				#~ if(headers_sent()):
					#~ this.Error('Some data has already been output to browser, can\'t send PDF file')
				#~ header('Content-Length: '+len(this.buffer))
				#~ header('Content-disposition: inline; filename="'+name+'"')
			print this.buffer
		elif dest=='D':
			#Download file
			#~ if(ob_get_contents()):
				#~ this.Error('Some data has already been output, can\'t send PDF file')
			#~ if(isset(_SERVER['HTTP_USER_AGENT']) and strpos(_SERVER['HTTP_USER_AGENT'],'MSIE')):
				#~ header('Content-Type: application/force-download')
			#~ else:
				#~ header('Content-Type: application/octet-stream')
			#~ if(headers_sent()):
				#~ this.Error('Some data has already been output to browser, can\'t send PDF file')
			#~ header('Content-Length: '+len(this.buffer))
			#~ header('Content-disposition: attachment; filename="'+name+'"')
			print this.buffer
		elif dest=='F':
			#Save to local file
			f=file(name,'wb')
			if(not f):
				this.Error('Unable to create output file: '+name)
			f.write(this.buffer)
			f.close()
		elif dest=='S':
			#Return as a string
			return this.buffer
		else:
			this.Error('Incorrect output destination: '+dest)
		return ''

# ******************************************************************************
# *                                                                              *
# *                              Protected methods                               *
# *                                                                              *
# *******************************************************************************/
	def _dochecks(this):
		#Check for locale-related bug
		if(1.1==1):
			this.Error("Don\'t alter the locale before including class file");
		#Check for decimal separator
		if(sprintf('%.1f',1.0)!='1.0'):
			setlocale(LC_NUMERIC,'C')

	def _getfontpath(this):
		return FPDF_FONT_DIR+'/'

	def _putpages(this):
		nb=this.page
		if hasattr(this,'StrAliasNbPages'):
			#Replace number of pages
			for n in xrange(1,nb+1):
				this.pages[n]=str_replace(this.StrAliasNbPages,str(nb),this.pages[n])
		if(this.DefOrientation=='P'):
			wPt=this.fwPt
			hPt=this.fhPt
		else:
			wPt=this.fhPt
			hPt=this.fwPt
		if this.compress:
			filter='/Filter /FlateDecode '
		else:
			filter=''
		for n in xrange(1,nb+1):
			#Page
			this._newobj()
			this._out('<</Type /Page')
			this._out('/Parent 1 0 R')
			if n in this.OrientationChanges:
				this._out(sprintf('/MediaBox [0 0 %.2f %.2f]',hPt,wPt))
			this._out('/Resources 2 0 R')
			if this.PageLinks and n in this.PageLinks:
				#Links
				annots='/Annots ['
				for pl in this.PageLinks[n]:
					rect=sprintf('%.2f %.2f %.2f %.2f',pl[0],pl[1],pl[0]+pl[2],pl[1]-pl[3])
					annots+='<</Type /Annot /Subtype /Link /Rect ['+rect+'] /Border [0 0 0] '
					if(is_string(pl[4])):
						annots+='/A <</S /URI /URI '+this._textstring(pl[4])+'>>>>'
					else:
						l=this.links[pl[4]]
						if l[0] in this.OrientationChanges:
							h=wPt
						else:
							h=hPt
						annots+=sprintf('/Dest [%d 0 R /XYZ 0 %.2f null]>>',1+2*l[0],h-l[1]*this.k)
				this._out(annots+']')
			this._out('/Contents '+str(this.n+1)+' 0 R>>')
			this._out('endobj')
			#Page content
			if this.compress:
				p = zlib.compress(this.pages[n].encode("latin1"))
			else:
				p = this.pages[n]
			this._newobj()
			this._out('<<'+filter+'/Length '+str(len(p))+'>>')
			this._putstream(p)
			this._out('endobj')
		#Pages root
		this.offsets[1]=len(this.buffer)
		this._out('1 0 obj')
		this._out('<</Type /Pages')
		kids='/Kids ['
		for i in xrange(0,nb):
			kids+=str(3+2*i)+' 0 R '
		this._out(kids+']')
		this._out('/Count '+str(nb))
		this._out(sprintf('/MediaBox [0 0 %.2f %.2f]',wPt,hPt))
		this._out('>>')
		this._out('endobj')

	def _putfonts(this):
		nf=this.n
		for diff in this.diffs:
			#Encodings
			this._newobj()
			this._out('<</Type /Encoding /BaseEncoding /WinAnsiEncoding /Differences ['+diff+']>>')
			this._out('endobj')
		for name,info in this.FontFiles.iteritems():
			#Font file embedding
			this._newobj()
			this.FontFiles[name]['n']=this.n
			font=''
			f=file(this._getfontpath()+name,'rb',1)
			if(not f):
				this.Error('Font file not found')
			font=f.read()
			f.close()
			compressed=(substr(name,-2)=='.z')
			if(not compressed and 'length2' in info):
				header=(ord(font[0])==128)
				if(header):
					#Strip first binary header
					font=substr(font,6)
				if(header and ord(font[info['length1']])==128):
					#Strip second binary header
					font=substr(font,0,info['length1'])+substr(font,info['length1']+6)
			this._out('<</Length '+str(len(font)))
			if(compressed):
				this._out('/Filter /FlateDecode')
			this._out('/Length1 '+str(info['length1']))
			if('length2' in info):
				this._out('/Length2 '+str(info['length2'])+' /Length3 0')
			this._out('>>')
			this._putstream(font)
			this._out('endobj')
		for k,font in this.fonts.iteritems():
			#Font objects
			this.fonts[k]['n']=this.n+1
			type=font['type']
			name=font['name']
			if(type=='core'):
				#Standard font
				this._newobj()
				this._out('<</Type /Font')
				this._out('/BaseFont /'+name)
				this._out('/Subtype /Type1')
				if(name!='Symbol' and name!='ZapfDingbats'):
					this._out('/Encoding /WinAnsiEncoding')
				this._out('>>')
				this._out('endobj')
			elif(type=='Type1' or type=='TrueType'):
				#Additional Type1 or TrueType font
				this._newobj()
				this._out('<</Type /Font')
				this._out('/BaseFont /'+name)
				this._out('/Subtype /'+type)
				this._out('/FirstChar 32 /LastChar 255')
				this._out('/Widths '+str(this.n+1)+' 0 R')
				this._out('/FontDescriptor '+str(this.n+2)+' 0 R')
				if(font['enc']):
					if('diff' in font):
						this._out('/Encoding '+(nf+font['diff'])+' 0 R')
					else:
						this._out('/Encoding /WinAnsiEncoding')
				this._out('>>')
				this._out('endobj')
				#Widths
				this._newobj()
				cw=font['cw']
				s='['
				for i in xrange(32,256):
					# Get doesn't rise exception; returns 0 instead of None if not set
					s+=str(cw.get(chr(i)) or 0)+' '
				this._out(s+']')
				this._out('endobj')
				#Descriptor
				this._newobj()
				s='<</Type /FontDescriptor /FontName /'+name
				for k,v in font['desc'].iteritems():
					s+=' /'+str(k)+' '+str(v)
				filename=font['file']
				if(filename):
					s+=' /FontFile'
					if type!='Type1':
						s+='2'
					s+=' '+str(this.FontFiles[filename]['n'])+' 0 R'
				this._out(s+'>>')
				this._out('endobj')
			else:
				#Allow for additional types
				mtd='_put'+strtolower(type)
				if(not method_exists(this,mtd)):
					this.Error('Unsupported font type: '+type)
				this.mtd(font)

	def _putimages(this):
		filter=''
		if this.compress:
			filter='/Filter /FlateDecode '
		for filename,info in this.images.iteritems():
			this._newobj()
			this.images[filename]['n']=this.n
			this._out('<</Type /XObject')
			this._out('/Subtype /Image')
			this._out('/Width '+str(info['w']))
			this._out('/Height '+str(info['h']))
			if(info['cs']=='Indexed'):
				this._out('/ColorSpace [/Indexed /DeviceRGB '+str(len(info['pal'])/3-1)+' '+str(this.n+1)+' 0 R]')
			else:
				this._out('/ColorSpace /'+info['cs'])
				if(info['cs']=='DeviceCMYK'):
					this._out('/Decode [1 0 1 0 1 0 1 0]')
			this._out('/BitsPerComponent '+str(info['bpc']))
			if 'f' in info:
				this._out('/Filter /'+info['f'])
			if 'parms' in info:
				this._out(info['parms'])
			if('trns' in info and type([])==info['trns']):
				trns=''
				for i in xrange(0,len(info['trns'])):
					trns+=str(info['trns'][i])+' '+str(info['trns'][i])+' '
				this._out('/Mask ['+trns+']')
			this._out('/Length '+str(len(info['data']))+'>>')
			this._putstream(info['data'])
			this.images[filename]['data'] = None
			this._out('endobj')
			#Palette
			if(info['cs']=='Indexed'):
				this._newobj()
				if this.compress:
					pal=zlib.compress(info['pal'])
				else:
					pal=info['pal']
				this._out('<<'+filter+'/Length '+str(len(pal))+'>>')
				this._putstream(pal)
				this._out('endobj')

	def _putxobjectdict(this):
		for image in this.images.values():
			this._out('/I'+str(image['i'])+' '+str(image['n'])+' 0 R')

	def _putresourcedict(this):
		this._out('/ProcSet [/PDF /Text /ImageB /ImageC /ImageI]')
		this._out('/Font <<')
		for font in this.fonts.values():
			this._out('/F'+str(font['i'])+' '+str(font['n'])+' 0 R')
		this._out('>>')
		this._out('/XObject <<')
		this._putxobjectdict()
		this._out('>>')

	def _putresources(this):
		this._putfonts()
		this._putimages()
		#Resource dictionary
		this.offsets[2]=len(this.buffer)
		this._out('2 0 obj')
		this._out('<<')
		this._putresourcedict()
		this._out('>>')
		this._out('endobj')

	def _putinfo(this):
		this._out('/Producer '+this._textstring('FPDF '+FPDF_VERSION+' for Python'))
		if hasattr(this,'title'):
			this._out('/Title '+this._textstring(this.title))
		if hasattr(this,'subject'):
			this._out('/Subject '+this._textstring(this.subject))
		if hasattr(this,'author'):
			this._out('/Author '+this._textstring(this.author))
		if hasattr (this,'keywords'):
			this._out('/Keywords '+this._textstring(this.keywords))
		if hasattr(this,'creator'):
			this._out('/Creator '+this._textstring(this.creator))
		this._out('/CreationDate '+this._textstring('D:'+datetime.now().strftime('%Y%m%d%H%M%S')))

	def _putcatalog(this):
		this._out('/Type /Catalog')
		this._out('/Pages 1 0 R')
		if(this.ZoomMode=='fullpage'):
			this._out('/OpenAction [3 0 R /Fit]')
		elif(this.ZoomMode=='fullwidth'):
			this._out('/OpenAction [3 0 R /FitH null]')
		elif(this.ZoomMode=='real'):
			this._out('/OpenAction [3 0 R /XYZ null null 1]')
		elif(not is_string(this.ZoomMode)):
			this._out('/OpenAction [3 0 R /XYZ null null '+(this.ZoomMode/100)+']')
		if(this.LayoutMode=='single'):
			this._out('/PageLayout /SinglePage')
		elif(this.LayoutMode=='continuous'):
			this._out('/PageLayout /OneColumn')
		elif(this.LayoutMode=='two'):
			this._out('/PageLayout /TwoColumnLeft')

	def _putheader(this):
		this._out('%PDF-'+this.PDFVersion)

	def _puttrailer(this):
		this._out('/Size '+str(this.n+1))
		this._out('/Root '+str(this.n)+' 0 R')
		this._out('/Info '+str(this.n-1)+' 0 R')

	def _enddoc(this):
		this._putheader()
		this._putpages()
		this._putresources()
		#Info
		this._newobj()
		this._out('<<')
		this._putinfo()
		this._out('>>')
		this._out('endobj')
		#Catalog
		this._newobj()
		this._out('<<')
		this._putcatalog()
		this._out('>>')
		this._out('endobj')
		#Cross-ref
		o=len(this.buffer)
		this._out('xref')
		this._out('0 '+(str(this.n+1)))
		this._out('0000000000 65535 f ')
		for i in xrange(1,this.n+1):
			this._out(sprintf('%010d 00000 n ',this.offsets[i]))
		#Trailer
		this._out('trailer')
		this._out('<<')
		this._puttrailer()
		this._out('>>')
		this._out('startxref')
		this._out(o)
		this._out('%%EOF')
		this.state=3

	def _beginpage(this, orientation):
		this.page+=1
		this.pages[this.page]=''
		this.state=2
		this.x=this.lMargin
		this.y=this.tMargin
		this.FontFamily=''
		#Page orientation
		if(not orientation):
			orientation=this.DefOrientation
		else:
			orientation=strtoupper(orientation[0])
			if(orientation!=this.DefOrientation):
				this.OrientationChanges[this.page]=1
		if(orientation!=this.CurOrientation):
			#Change orientation
			if(orientation=='P'):
				this.wPt=this.fwPt
				this.hPt=this.fhPt
				this.w=this.fw
				this.h=this.fh
			else:
				this.wPt=this.fhPt
				this.hPt=this.fwPt
				this.w=this.fh
				this.h=this.fw
			this.PageBreakTrigger=this.h-this.bMargin
			this.CurOrientation=orientation

	def _endpage(this):
		#End of page contents
		this.state=1

	def _newobj(this):
		#Begin a new object
		this.n+=1
		this.offsets[this.n]=len(this.buffer)
		this._out(str(this.n)+' 0 obj')

	def _dounderline(this, x,y,txt):
		#Underline text
		up=this.CurrentFont['up']
		ut=this.CurrentFont['ut']
		w=this.GetStringWidth(txt)+this.ws*substr_count(txt,' ')
		return sprintf('%.2f %.2f %.2f %.2f re f',x*this.k,(this.h-(y-up/1000.0*this.FontSize))*this.k,w*this.k,-ut/1000.0*this.FontSizePt)

	def _parsejpg(this, filename):
		#Extract info from a JPEG file
		a=GetImageSize(filename)
		if(not a):
			this.Error('Missing or incorrect image file: '+filename)
		if(a[2]!=2):
			this.Error('Not a JPEG file: '+filename)
		if(not isset(a['channels']) or a['channels']==3):
			colspace='DeviceRGB'
		elif(a['channels']==4):
			colspace='DeviceCMYK'
		else:
			colspace='DeviceGray'
		if isset(a['bits']):
			bpc=a['bits']
		else:
			bpc=8
		#Read whole file
		f=fopen(filename,'rb')
		data=''
		while(not feof(f)):
			data+=f.read(4096)
		fclose(f)
		return {'w':a[0],'h':a[1],'cs':colspace,'bpc':bpc,'f':'DCTDecode','data':data}

	def _parsepng(this, name):
		#Extract info from a PNG file
		f=file(name,'rb')
		if(not f):
			this.Error("Can't open image file: "+name)
		#Check signature
		if(f.read(8)!=chr(137)+'PNG'+chr(13)+chr(10)+chr(26)+chr(10)):
			this.Error('Not a PNG file: '+name)
		#Read header chunk
		f.read(4)
		if(f.read(4)!='IHDR'):
			this.Error('Incorrect PNG file: '+name)
		w=this._freadint(f)
		h=this._freadint(f)
		bpc=ord(f.read(1))
		if(bpc>8):
			this.Error('16-bit depth not supported: '+name)
		ct=ord(f.read(1))
		if(ct==0):
			colspace='DeviceGray'
		elif(ct==2):
			colspace='DeviceRGB'
		elif(ct==3):
			colspace='Indexed'
		else:
			this.Error('Alpha channel not supported: '+name)
		if(ord(f.read(1))!=0):
			this.Error('Unknown compression method: '+name)
		if(ord(f.read(1))!=0):
			this.Error('Unknown filter method: '+name)
		if(ord(f.read(1))!=0):
			this.Error('Interlacing not supported: '+name)
		f.read(4)
		parms='/DecodeParms <</Predictor 15 /Colors '
		if ct==2:
			parms+='3'
		else:
			parms+='1'
		parms+=' /BitsPerComponent '+str(bpc)+' /Columns '+str(w)+'>>'
		#Scan chunks looking for palette, transparency and image data
		pal=''
		trns=''
		data=''
		n=1
		while n != None:
			n=this._freadint(f)
			type=f.read(4)
			if(type=='PLTE'):
				#Read palette
				pal=f.read(n)
				f.read(4)
			elif(type=='tRNS'):
				#Read transparency info
				t=f.read(n)
				if(ct==0):
					trns=[ord(substr(t,1,1)),]
				elif(ct==2):
					trns=[ord(substr(t,1,1)),ord(substr(t,3,1)),ord(substr(t,5,1))]
				else:
					pos=strpos(t,chr(0))
					if(pos!=-1):
						trns=[pos,]
				f.read(4)
			elif(type=='IDAT'):
				#Read image data block
				data+=f.read(n)
				f.read(4)
			elif(type=='IEND'):
				break
			else:
				f.read(n+4)
		if(colspace=='Indexed' and not pal):
			this.Error('Missing palette in '+name)
		f.close()
		return {'w':w,'h':h,'cs':colspace,'bpc':bpc,'f':'FlateDecode','parms':parms,'pal':pal,'trns':trns,'data':data}

	def _freadint(this, f):
		#Read a 4-byte integer from file
		try:
			return struct.unpack('>HH',f.read(4))[1]
		except:
			return None

	def _textstring(this, s):
		#Format a text string
		return '('+this._escape(s)+')'

	def _escape(this, s):
		#Add \ before \, ( and )
		return str_replace(')','\\)',str_replace('(','\\(',str_replace('\\','\\\\',s)))

	def _putstream(this, s):
		this._out('stream')
		this._out(s)
		this._out('endstream')

	def _out(this, s):
		#Add a line to the document
		if(this.state==2):
			this.pages[this.page]+=s+"\n"
		else:
			this.buffer+=str(s)+"\n"
#End of class

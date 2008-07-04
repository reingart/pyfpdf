from FPDF import *
import re

class PDF(FPDF):
		def __init__(this, orientation='P',unit='mm',format='A4'):
			#Call parent constructor
			FPDF.__init__(this,orientation,unit,format) # is this right?
			#Initialization
			this.B=0
			this.I=0
			this.U=0
			this.HREF=''
			this.PageLinks={}

		def WriteHTML(this, html):
			#HTML parser
			html=str_replace("\n",' ',html)
			a=re.split('<(.*?)>',html)
			for i,e in enumerate(a):
				if(i%2==0):
					#Text
					if(this.HREF):
						this.PutLink(this.HREF,e)
					else:
						this.Write(5,e)
				else:
					#Tag
					if(e[0]=='/'):
						this.CloseTag(strtoupper(substr(e,1)))
					else:
						#Extract attributes
						attr={}
						a2=e.split(' ')
						tag=strtoupper(a2.pop(0))
						for v in a2:
							a3 = re.findall('''^([^=]*)=["']?([^"']*)["']?''',v)[0]
							if a3:
								attr[strtoupper(a3[0])]=a3[1]
						this.OpenTag(tag,attr)

		def OpenTag(this, tag,attr):
			#Opening tag
			if(tag=='B' or tag=='I' or tag=='U'):
				this.SetStyle(tag,1)
			if(tag=='A'):
				this.HREF=attr['HREF']
			if(tag=='BR'):
				this.Ln(5)

		def CloseTag(this, tag):
			#Closing tag
			if(tag=='B' or tag=='I' or tag=='U'):
				this.SetStyle(tag,0)
			if(tag=='A'):
				this.HREF=''

		def SetStyle(this, tag,enable):
			#Modify style and select corresponding font
			T = getattr(this,tag)
			if enable:
				T+=1
			else:
				T+=-1
			setattr(this,tag,T)
			style=''
			for s in ('B','I','U'):
				if(getattr(this,s)>0):
					style+=s
			this.SetFont('',style)

		def PutLink(this, URL,txt):
			#Put a hyperlink
			this.SetTextColor(0,0,255)
			this.SetStyle('U',1)
			this.Write(5,txt,URL)
			this.SetStyle('U',0)
			this.SetTextColor(0)

html="""You can now easily print text mixing different
styles : <B>bold</B>, <I>italic</I>, <U>underlined</U>, or
<B><I><U>all at once</U></I></B>!<BR>You can also insert links
on text, such as <A HREF="http:#www.fpdf.org">www.fpdf.org</A>,
or on an image: click on the logo."""

pdf=PDF()
#First page
pdf.AddPage()
pdf.SetFont('Arial','',20)
pdf.Write(5,'To find out what\'s new in this tutorial, click ')
pdf.SetFont('','U')
link=pdf.AddLink()
pdf.Write(5,'here',link)
pdf.SetFont('')
#Second page
pdf.AddPage()
pdf.SetLink(link)
pdf.Image('logo.png',10,10,30,0,'','http:#www.fpdf.org')
pdf.SetLeftMargin(45)
pdf.SetFontSize(14)
pdf.WriteHTML(html)
pdf.Output('tuto6.pdf','F')

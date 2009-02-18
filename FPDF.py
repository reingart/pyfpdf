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
import math
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
        this.angle=0
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
        raise RuntimeError('FPDF error: '+msg)

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
            w += cw.get(s[i],0)
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
            fname=str_replace(' ','',family).lower(style)+'.font'
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
                    execfile(name+'.font')
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

    def Rotate(this, angle, x=None, y=None):
        if x is None:
            x = this.x
        if y is None:
            y = this.y;
        if this.angle!=0:
            this._out('Q')
        this.angle = angle
        if angle!=0:
            angle *= math.pi/180;
            c = math.cos(angle);
            s = math.sin(angle);
            cx = x*this.k;
            cy = (this.h-y)*this.k
            s = sprintf('q %.5F %.5F %.5F %.5F %.2F %.2F cm 1 0 0 1 %.2F %.2F cm',c,s,-s,c,cx,cy,-cx,-cy)
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
            l+=cw.get(c,0)
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
            l+=cw.get(c,0)
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
#        if(1.1==1):
#            this.Error("Don\'t alter the locale before including class file");
        #Check for decimal separator
        if(sprintf('%.1f',1.0)!='1.0'):
            import locale
            locale.setlocale(locale.LC_NUMERIC,'C')

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
                p = zlib.compress(this.pages[n])
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

    def Interleaved2of5(self, txt, x, y, w=1.0, h=10.0):
        "Código Entrelazado 2 de 5 (numérico), la longitud debe ser par, sino agrega un 0"
        narrow = w / 3.0 
        wide = w
        
        # wide/narrow codes for the digits
        barChar={}
        barChar['0'] = 'nnwwn'
        barChar['1'] = 'wnnnw'
        barChar['2'] = 'nwnnw'
        barChar['3'] = 'wwnnn'
        barChar['4'] = 'nnwnw'
        barChar['5'] = 'wnwnn'
        barChar['6'] = 'nwwnn'
        barChar['7'] = 'nnnww'
        barChar['8'] = 'wnnwn'
        barChar['9'] = 'nwnwn'
        barChar['A'] = 'nn'
        barChar['Z'] = 'wn'
           
        self.SetFillColor(0)
        code = txt
        # add leading zero if code-length is odd
        if len(code) % 2 != 0:
            code = '0' + code
        
        # add start and stop codes
        code = 'AA' + code.lower() + 'ZA'

        for i in xrange(0, len(code), 2):
            # choose next pair of digits
            charBar = code[i];
            charSpace = code[i+1];
            # check whether it is a valid digit
            if not charBar in barChar.keys():
                raise RuntimeError ('Caractér "%s" inválido para el código de barras I25: ' % charBar)
            if not charSpace in barChar.keys():
                raise RuntimeError ('Caractér "%s" inválido para el código de barras I25: ' % charSpace)

            # create a wide/narrow-sequence (first digit=bars, second digit=spaces)
            seq = ''
            for s in xrange(0, len(barChar[charBar])):
                seq += barChar[charBar][s] + barChar[charSpace][s]

            for bar in xrange(0, len(seq)):
                # set lineWidth depending on value
                if seq[bar] == 'n':
                    lineWidth = narrow
                else:
                    lineWidth = wide

                # draw every second value, because the second digit of the pair is represented by the spaces
                if bar % 2 == 0:
                    self.Rect(x, y, lineWidth, h, 'F')

                x += lineWidth

#End of class

# Fonts:
    
fpdf_charwidths['courier']={}

for i in xrange(0,256):
    fpdf_charwidths['courier'][chr(i)]=600
    fpdf_charwidths['courierB']=fpdf_charwidths['courier']
    fpdf_charwidths['courierI']=fpdf_charwidths['courier']
    fpdf_charwidths['courierBI']=fpdf_charwidths['courier']

fpdf_charwidths['helvetica']={
    chr(0):278,chr(1):278,chr(2):278,chr(3):278,chr(4):278,chr(5):278,chr(6):278,chr(7):278,chr(8):278,chr(9):278,chr(10):278,chr(11):278,chr(12):278,chr(13):278,chr(14):278,chr(15):278,chr(16):278,chr(17):278,chr(18):278,chr(19):278,chr(20):278,chr(21):278,
    chr(22):278,chr(23):278,chr(24):278,chr(25):278,chr(26):278,chr(27):278,chr(28):278,chr(29):278,chr(30):278,chr(31):278,' ':278,'!':278,'"':355,'#':556,'$':556,'%':889,'&':667,'\'':191,'(':333,')':333,'*':389,'+':584,
    ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':278,';':278,'<':584,'=':584,'>':584,'?':556,'@':1015,'A':667,
    'B':667,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':500,'K':667,'L':556,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
    'X':667,'Y':667,'Z':611,'[':278,'\\':278,']':278,'^':469,'_':556,'`':333,'a':556,'b':556,'c':500,'d':556,'e':556,'f':278,'g':556,'h':556,'i':222,'j':222,'k':500,'l':222,'m':833,
    'n':556,'o':556,'p':556,'q':556,'r':333,'s':500,'t':278,'u':556,'v':500,'w':722,'x':500,'y':500,'z':500,'{':334,'|':260,'}':334,'~':584,chr(127):350,chr(128):556,chr(129):350,chr(130):222,chr(131):556,
    chr(132):333,chr(133):1000,chr(134):556,chr(135):556,chr(136):333,chr(137):1000,chr(138):667,chr(139):333,chr(140):1000,chr(141):350,chr(142):611,chr(143):350,chr(144):350,chr(145):222,chr(146):222,chr(147):333,chr(148):333,chr(149):350,chr(150):556,chr(151):1000,chr(152):333,chr(153):1000,
    chr(154):500,chr(155):333,chr(156):944,chr(157):350,chr(158):500,chr(159):667,chr(160):278,chr(161):333,chr(162):556,chr(163):556,chr(164):556,chr(165):556,chr(166):260,chr(167):556,chr(168):333,chr(169):737,chr(170):370,chr(171):556,chr(172):584,chr(173):333,chr(174):737,chr(175):333,
    chr(176):400,chr(177):584,chr(178):333,chr(179):333,chr(180):333,chr(181):556,chr(182):537,chr(183):278,chr(184):333,chr(185):333,chr(186):365,chr(187):556,chr(188):834,chr(189):834,chr(190):834,chr(191):611,chr(192):667,chr(193):667,chr(194):667,chr(195):667,chr(196):667,chr(197):667,
    chr(198):1000,chr(199):722,chr(200):667,chr(201):667,chr(202):667,chr(203):667,chr(204):278,chr(205):278,chr(206):278,chr(207):278,chr(208):722,chr(209):722,chr(210):778,chr(211):778,chr(212):778,chr(213):778,chr(214):778,chr(215):584,chr(216):778,chr(217):722,chr(218):722,chr(219):722,
    chr(220):722,chr(221):667,chr(222):667,chr(223):611,chr(224):556,chr(225):556,chr(226):556,chr(227):556,chr(228):556,chr(229):556,chr(230):889,chr(231):500,chr(232):556,chr(233):556,chr(234):556,chr(235):556,chr(236):278,chr(237):278,chr(238):278,chr(239):278,chr(240):556,chr(241):556,
    chr(242):556,chr(243):556,chr(244):556,chr(245):556,chr(246):556,chr(247):584,chr(248):611,chr(249):556,chr(250):556,chr(251):556,chr(252):556,chr(253):500,chr(254):556,chr(255):500}

fpdf_charwidths['helveticaB']={
    chr(0):278,chr(1):278,chr(2):278,chr(3):278,chr(4):278,chr(5):278,chr(6):278,chr(7):278,chr(8):278,chr(9):278,chr(10):278,chr(11):278,chr(12):278,chr(13):278,chr(14):278,chr(15):278,chr(16):278,chr(17):278,chr(18):278,chr(19):278,chr(20):278,chr(21):278,
    chr(22):278,chr(23):278,chr(24):278,chr(25):278,chr(26):278,chr(27):278,chr(28):278,chr(29):278,chr(30):278,chr(31):278,' ':278,'!':333,'"':474,'#':556,'$':556,'%':889,'&':722,'\'':238,'(':333,')':333,'*':389,'+':584,
    ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':333,';':333,'<':584,'=':584,'>':584,'?':611,'@':975,'A':722,
    'B':722,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':556,'K':722,'L':611,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
    'X':667,'Y':667,'Z':611,'[':333,'\\':278,']':333,'^':584,'_':556,'`':333,'a':556,'b':611,'c':556,'d':611,'e':556,'f':333,'g':611,'h':611,'i':278,'j':278,'k':556,'l':278,'m':889,
    'n':611,'o':611,'p':611,'q':611,'r':389,'s':556,'t':333,'u':611,'v':556,'w':778,'x':556,'y':556,'z':500,'{':389,'|':280,'}':389,'~':584,chr(127):350,chr(128):556,chr(129):350,chr(130):278,chr(131):556,
    chr(132):500,chr(133):1000,chr(134):556,chr(135):556,chr(136):333,chr(137):1000,chr(138):667,chr(139):333,chr(140):1000,chr(141):350,chr(142):611,chr(143):350,chr(144):350,chr(145):278,chr(146):278,chr(147):500,chr(148):500,chr(149):350,chr(150):556,chr(151):1000,chr(152):333,chr(153):1000,
    chr(154):556,chr(155):333,chr(156):944,chr(157):350,chr(158):500,chr(159):667,chr(160):278,chr(161):333,chr(162):556,chr(163):556,chr(164):556,chr(165):556,chr(166):280,chr(167):556,chr(168):333,chr(169):737,chr(170):370,chr(171):556,chr(172):584,chr(173):333,chr(174):737,chr(175):333,
    chr(176):400,chr(177):584,chr(178):333,chr(179):333,chr(180):333,chr(181):611,chr(182):556,chr(183):278,chr(184):333,chr(185):333,chr(186):365,chr(187):556,chr(188):834,chr(189):834,chr(190):834,chr(191):611,chr(192):722,chr(193):722,chr(194):722,chr(195):722,chr(196):722,chr(197):722,
    chr(198):1000,chr(199):722,chr(200):667,chr(201):667,chr(202):667,chr(203):667,chr(204):278,chr(205):278,chr(206):278,chr(207):278,chr(208):722,chr(209):722,chr(210):778,chr(211):778,chr(212):778,chr(213):778,chr(214):778,chr(215):584,chr(216):778,chr(217):722,chr(218):722,chr(219):722,
    chr(220):722,chr(221):667,chr(222):667,chr(223):611,chr(224):556,chr(225):556,chr(226):556,chr(227):556,chr(228):556,chr(229):556,chr(230):889,chr(231):556,chr(232):556,chr(233):556,chr(234):556,chr(235):556,chr(236):278,chr(237):278,chr(238):278,chr(239):278,chr(240):611,chr(241):611,
    chr(242):611,chr(243):611,chr(244):611,chr(245):611,chr(246):611,chr(247):584,chr(248):611,chr(249):611,chr(250):611,chr(251):611,chr(252):611,chr(253):556,chr(254):611,chr(255):556
}

fpdf_charwidths['helveticaBI']={
    chr(0):278,chr(1):278,chr(2):278,chr(3):278,chr(4):278,chr(5):278,chr(6):278,chr(7):278,chr(8):278,chr(9):278,chr(10):278,chr(11):278,chr(12):278,chr(13):278,chr(14):278,chr(15):278,chr(16):278,chr(17):278,chr(18):278,chr(19):278,chr(20):278,chr(21):278,
    chr(22):278,chr(23):278,chr(24):278,chr(25):278,chr(26):278,chr(27):278,chr(28):278,chr(29):278,chr(30):278,chr(31):278,' ':278,'!':333,'"':474,'#':556,'$':556,'%':889,'&':722,'\'':238,'(':333,')':333,'*':389,'+':584,
    ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':333,';':333,'<':584,'=':584,'>':584,'?':611,'@':975,'A':722,
    'B':722,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':556,'K':722,'L':611,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
    'X':667,'Y':667,'Z':611,'[':333,'\\':278,']':333,'^':584,'_':556,'`':333,'a':556,'b':611,'c':556,'d':611,'e':556,'f':333,'g':611,'h':611,'i':278,'j':278,'k':556,'l':278,'m':889,
    'n':611,'o':611,'p':611,'q':611,'r':389,'s':556,'t':333,'u':611,'v':556,'w':778,'x':556,'y':556,'z':500,'{':389,'|':280,'}':389,'~':584,chr(127):350,chr(128):556,chr(129):350,chr(130):278,chr(131):556,
    chr(132):500,chr(133):1000,chr(134):556,chr(135):556,chr(136):333,chr(137):1000,chr(138):667,chr(139):333,chr(140):1000,chr(141):350,chr(142):611,chr(143):350,chr(144):350,chr(145):278,chr(146):278,chr(147):500,chr(148):500,chr(149):350,chr(150):556,chr(151):1000,chr(152):333,chr(153):1000,
    chr(154):556,chr(155):333,chr(156):944,chr(157):350,chr(158):500,chr(159):667,chr(160):278,chr(161):333,chr(162):556,chr(163):556,chr(164):556,chr(165):556,chr(166):280,chr(167):556,chr(168):333,chr(169):737,chr(170):370,chr(171):556,chr(172):584,chr(173):333,chr(174):737,chr(175):333,
    chr(176):400,chr(177):584,chr(178):333,chr(179):333,chr(180):333,chr(181):611,chr(182):556,chr(183):278,chr(184):333,chr(185):333,chr(186):365,chr(187):556,chr(188):834,chr(189):834,chr(190):834,chr(191):611,chr(192):722,chr(193):722,chr(194):722,chr(195):722,chr(196):722,chr(197):722,
    chr(198):1000,chr(199):722,chr(200):667,chr(201):667,chr(202):667,chr(203):667,chr(204):278,chr(205):278,chr(206):278,chr(207):278,chr(208):722,chr(209):722,chr(210):778,chr(211):778,chr(212):778,chr(213):778,chr(214):778,chr(215):584,chr(216):778,chr(217):722,chr(218):722,chr(219):722,
    chr(220):722,chr(221):667,chr(222):667,chr(223):611,chr(224):556,chr(225):556,chr(226):556,chr(227):556,chr(228):556,chr(229):556,chr(230):889,chr(231):556,chr(232):556,chr(233):556,chr(234):556,chr(235):556,chr(236):278,chr(237):278,chr(238):278,chr(239):278,chr(240):611,chr(241):611,
    chr(242):611,chr(243):611,chr(244):611,chr(245):611,chr(246):611,chr(247):584,chr(248):611,chr(249):611,chr(250):611,chr(251):611,chr(252):611,chr(253):556,chr(254):611,chr(255):556}

fpdf_charwidths['helveticaI']={
    chr(0):278,chr(1):278,chr(2):278,chr(3):278,chr(4):278,chr(5):278,chr(6):278,chr(7):278,chr(8):278,chr(9):278,chr(10):278,chr(11):278,chr(12):278,chr(13):278,chr(14):278,chr(15):278,chr(16):278,chr(17):278,chr(18):278,chr(19):278,chr(20):278,chr(21):278,
    chr(22):278,chr(23):278,chr(24):278,chr(25):278,chr(26):278,chr(27):278,chr(28):278,chr(29):278,chr(30):278,chr(31):278,' ':278,'!':278,'"':355,'#':556,'$':556,'%':889,'&':667,'\'':191,'(':333,')':333,'*':389,'+':584,
    ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':278,';':278,'<':584,'=':584,'>':584,'?':556,'@':1015,'A':667,
    'B':667,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':500,'K':667,'L':556,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
    'X':667,'Y':667,'Z':611,'[':278,'\\':278,']':278,'^':469,'_':556,'`':333,'a':556,'b':556,'c':500,'d':556,'e':556,'f':278,'g':556,'h':556,'i':222,'j':222,'k':500,'l':222,'m':833,
    'n':556,'o':556,'p':556,'q':556,'r':333,'s':500,'t':278,'u':556,'v':500,'w':722,'x':500,'y':500,'z':500,'{':334,'|':260,'}':334,'~':584,chr(127):350,chr(128):556,chr(129):350,chr(130):222,chr(131):556,
    chr(132):333,chr(133):1000,chr(134):556,chr(135):556,chr(136):333,chr(137):1000,chr(138):667,chr(139):333,chr(140):1000,chr(141):350,chr(142):611,chr(143):350,chr(144):350,chr(145):222,chr(146):222,chr(147):333,chr(148):333,chr(149):350,chr(150):556,chr(151):1000,chr(152):333,chr(153):1000,
    chr(154):500,chr(155):333,chr(156):944,chr(157):350,chr(158):500,chr(159):667,chr(160):278,chr(161):333,chr(162):556,chr(163):556,chr(164):556,chr(165):556,chr(166):260,chr(167):556,chr(168):333,chr(169):737,chr(170):370,chr(171):556,chr(172):584,chr(173):333,chr(174):737,chr(175):333,
    chr(176):400,chr(177):584,chr(178):333,chr(179):333,chr(180):333,chr(181):556,chr(182):537,chr(183):278,chr(184):333,chr(185):333,chr(186):365,chr(187):556,chr(188):834,chr(189):834,chr(190):834,chr(191):611,chr(192):667,chr(193):667,chr(194):667,chr(195):667,chr(196):667,chr(197):667,
    chr(198):1000,chr(199):722,chr(200):667,chr(201):667,chr(202):667,chr(203):667,chr(204):278,chr(205):278,chr(206):278,chr(207):278,chr(208):722,chr(209):722,chr(210):778,chr(211):778,chr(212):778,chr(213):778,chr(214):778,chr(215):584,chr(216):778,chr(217):722,chr(218):722,chr(219):722,
    chr(220):722,chr(221):667,chr(222):667,chr(223):611,chr(224):556,chr(225):556,chr(226):556,chr(227):556,chr(228):556,chr(229):556,chr(230):889,chr(231):500,chr(232):556,chr(233):556,chr(234):556,chr(235):556,chr(236):278,chr(237):278,chr(238):278,chr(239):278,chr(240):556,chr(241):556,
    chr(242):556,chr(243):556,chr(244):556,chr(245):556,chr(246):556,chr(247):584,chr(248):611,chr(249):556,chr(250):556,chr(251):556,chr(252):556,chr(253):500,chr(254):556,chr(255):500}

fpdf_charwidths['symbol']={
    chr(0):250,chr(1):250,chr(2):250,chr(3):250,chr(4):250,chr(5):250,chr(6):250,chr(7):250,chr(8):250,chr(9):250,chr(10):250,chr(11):250,chr(12):250,chr(13):250,chr(14):250,chr(15):250,chr(16):250,chr(17):250,chr(18):250,chr(19):250,chr(20):250,chr(21):250,
    chr(22):250,chr(23):250,chr(24):250,chr(25):250,chr(26):250,chr(27):250,chr(28):250,chr(29):250,chr(30):250,chr(31):250,' ':250,'!':333,'"':713,'#':500,'$':549,'%':833,'&':778,'\'':439,'(':333,')':333,'*':500,'+':549,
    ',':250,'-':549,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':278,';':278,'<':549,'=':549,'>':549,'?':444,'@':549,'A':722,
    'B':667,'C':722,'D':612,'E':611,'F':763,'G':603,'H':722,'I':333,'J':631,'K':722,'L':686,'M':889,'N':722,'O':722,'P':768,'Q':741,'R':556,'S':592,'T':611,'U':690,'V':439,'W':768,
    'X':645,'Y':795,'Z':611,'[':333,'\\':863,']':333,'^':658,'_':500,'`':500,'a':631,'b':549,'c':549,'d':494,'e':439,'f':521,'g':411,'h':603,'i':329,'j':603,'k':549,'l':549,'m':576,
    'n':521,'o':549,'p':549,'q':521,'r':549,'s':603,'t':439,'u':576,'v':713,'w':686,'x':493,'y':686,'z':494,'{':480,'|':200,'}':480,'~':549,chr(127):0,chr(128):0,chr(129):0,chr(130):0,chr(131):0,
    chr(132):0,chr(133):0,chr(134):0,chr(135):0,chr(136):0,chr(137):0,chr(138):0,chr(139):0,chr(140):0,chr(141):0,chr(142):0,chr(143):0,chr(144):0,chr(145):0,chr(146):0,chr(147):0,chr(148):0,chr(149):0,chr(150):0,chr(151):0,chr(152):0,chr(153):0,
    chr(154):0,chr(155):0,chr(156):0,chr(157):0,chr(158):0,chr(159):0,chr(160):750,chr(161):620,chr(162):247,chr(163):549,chr(164):167,chr(165):713,chr(166):500,chr(167):753,chr(168):753,chr(169):753,chr(170):753,chr(171):1042,chr(172):987,chr(173):603,chr(174):987,chr(175):603,
    chr(176):400,chr(177):549,chr(178):411,chr(179):549,chr(180):549,chr(181):713,chr(182):494,chr(183):460,chr(184):549,chr(185):549,chr(186):549,chr(187):549,chr(188):1000,chr(189):603,chr(190):1000,chr(191):658,chr(192):823,chr(193):686,chr(194):795,chr(195):987,chr(196):768,chr(197):768,
    chr(198):823,chr(199):768,chr(200):768,chr(201):713,chr(202):713,chr(203):713,chr(204):713,chr(205):713,chr(206):713,chr(207):713,chr(208):768,chr(209):713,chr(210):790,chr(211):790,chr(212):890,chr(213):823,chr(214):549,chr(215):250,chr(216):713,chr(217):603,chr(218):603,chr(219):1042,
    chr(220):987,chr(221):603,chr(222):987,chr(223):603,chr(224):494,chr(225):329,chr(226):790,chr(227):790,chr(228):786,chr(229):713,chr(230):384,chr(231):384,chr(232):384,chr(233):384,chr(234):384,chr(235):384,chr(236):494,chr(237):494,chr(238):494,chr(239):494,chr(240):0,chr(241):329,
    chr(242):274,chr(243):686,chr(244):686,chr(245):686,chr(246):384,chr(247):384,chr(248):384,chr(249):384,chr(250):384,chr(251):384,chr(252):494,chr(253):494,chr(254):494,chr(255):0}
    
fpdf_charwidths['times']={
    chr(0):250,chr(1):250,chr(2):250,chr(3):250,chr(4):250,chr(5):250,chr(6):250,chr(7):250,chr(8):250,chr(9):250,chr(10):250,chr(11):250,chr(12):250,chr(13):250,chr(14):250,chr(15):250,chr(16):250,chr(17):250,chr(18):250,chr(19):250,chr(20):250,chr(21):250,
    chr(22):250,chr(23):250,chr(24):250,chr(25):250,chr(26):250,chr(27):250,chr(28):250,chr(29):250,chr(30):250,chr(31):250,' ':250,'!':333,'"':408,'#':500,'$':500,'%':833,'&':778,'\'':180,'(':333,')':333,'*':500,'+':564,
    ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':278,';':278,'<':564,'=':564,'>':564,'?':444,'@':921,'A':722,
    'B':667,'C':667,'D':722,'E':611,'F':556,'G':722,'H':722,'I':333,'J':389,'K':722,'L':611,'M':889,'N':722,'O':722,'P':556,'Q':722,'R':667,'S':556,'T':611,'U':722,'V':722,'W':944,
    'X':722,'Y':722,'Z':611,'[':333,'\\':278,']':333,'^':469,'_':500,'`':333,'a':444,'b':500,'c':444,'d':500,'e':444,'f':333,'g':500,'h':500,'i':278,'j':278,'k':500,'l':278,'m':778,
    'n':500,'o':500,'p':500,'q':500,'r':333,'s':389,'t':278,'u':500,'v':500,'w':722,'x':500,'y':500,'z':444,'{':480,'|':200,'}':480,'~':541,chr(127):350,chr(128):500,chr(129):350,chr(130):333,chr(131):500,
    chr(132):444,chr(133):1000,chr(134):500,chr(135):500,chr(136):333,chr(137):1000,chr(138):556,chr(139):333,chr(140):889,chr(141):350,chr(142):611,chr(143):350,chr(144):350,chr(145):333,chr(146):333,chr(147):444,chr(148):444,chr(149):350,chr(150):500,chr(151):1000,chr(152):333,chr(153):980,
    chr(154):389,chr(155):333,chr(156):722,chr(157):350,chr(158):444,chr(159):722,chr(160):250,chr(161):333,chr(162):500,chr(163):500,chr(164):500,chr(165):500,chr(166):200,chr(167):500,chr(168):333,chr(169):760,chr(170):276,chr(171):500,chr(172):564,chr(173):333,chr(174):760,chr(175):333,
    chr(176):400,chr(177):564,chr(178):300,chr(179):300,chr(180):333,chr(181):500,chr(182):453,chr(183):250,chr(184):333,chr(185):300,chr(186):310,chr(187):500,chr(188):750,chr(189):750,chr(190):750,chr(191):444,chr(192):722,chr(193):722,chr(194):722,chr(195):722,chr(196):722,chr(197):722,
    chr(198):889,chr(199):667,chr(200):611,chr(201):611,chr(202):611,chr(203):611,chr(204):333,chr(205):333,chr(206):333,chr(207):333,chr(208):722,chr(209):722,chr(210):722,chr(211):722,chr(212):722,chr(213):722,chr(214):722,chr(215):564,chr(216):722,chr(217):722,chr(218):722,chr(219):722,
    chr(220):722,chr(221):722,chr(222):556,chr(223):500,chr(224):444,chr(225):444,chr(226):444,chr(227):444,chr(228):444,chr(229):444,chr(230):667,chr(231):444,chr(232):444,chr(233):444,chr(234):444,chr(235):444,chr(236):278,chr(237):278,chr(238):278,chr(239):278,chr(240):500,chr(241):500,
    chr(242):500,chr(243):500,chr(244):500,chr(245):500,chr(246):500,chr(247):564,chr(248):500,chr(249):500,chr(250):500,chr(251):500,chr(252):500,chr(253):500,chr(254):500,chr(255):500}

fpdf_charwidths['timesB']={
    chr(0):250,chr(1):250,chr(2):250,chr(3):250,chr(4):250,chr(5):250,chr(6):250,chr(7):250,chr(8):250,chr(9):250,chr(10):250,chr(11):250,chr(12):250,chr(13):250,chr(14):250,chr(15):250,chr(16):250,chr(17):250,chr(18):250,chr(19):250,chr(20):250,chr(21):250,
    chr(22):250,chr(23):250,chr(24):250,chr(25):250,chr(26):250,chr(27):250,chr(28):250,chr(29):250,chr(30):250,chr(31):250,' ':250,'!':333,'"':555,'#':500,'$':500,'%':1000,'&':833,'\'':278,'(':333,')':333,'*':500,'+':570,
    ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':333,';':333,'<':570,'=':570,'>':570,'?':500,'@':930,'A':722,
    'B':667,'C':722,'D':722,'E':667,'F':611,'G':778,'H':778,'I':389,'J':500,'K':778,'L':667,'M':944,'N':722,'O':778,'P':611,'Q':778,'R':722,'S':556,'T':667,'U':722,'V':722,'W':1000,
    'X':722,'Y':722,'Z':667,'[':333,'\\':278,']':333,'^':581,'_':500,'`':333,'a':500,'b':556,'c':444,'d':556,'e':444,'f':333,'g':500,'h':556,'i':278,'j':333,'k':556,'l':278,'m':833,
    'n':556,'o':500,'p':556,'q':556,'r':444,'s':389,'t':333,'u':556,'v':500,'w':722,'x':500,'y':500,'z':444,'{':394,'|':220,'}':394,'~':520,chr(127):350,chr(128):500,chr(129):350,chr(130):333,chr(131):500,
    chr(132):500,chr(133):1000,chr(134):500,chr(135):500,chr(136):333,chr(137):1000,chr(138):556,chr(139):333,chr(140):1000,chr(141):350,chr(142):667,chr(143):350,chr(144):350,chr(145):333,chr(146):333,chr(147):500,chr(148):500,chr(149):350,chr(150):500,chr(151):1000,chr(152):333,chr(153):1000,
    chr(154):389,chr(155):333,chr(156):722,chr(157):350,chr(158):444,chr(159):722,chr(160):250,chr(161):333,chr(162):500,chr(163):500,chr(164):500,chr(165):500,chr(166):220,chr(167):500,chr(168):333,chr(169):747,chr(170):300,chr(171):500,chr(172):570,chr(173):333,chr(174):747,chr(175):333,
    chr(176):400,chr(177):570,chr(178):300,chr(179):300,chr(180):333,chr(181):556,chr(182):540,chr(183):250,chr(184):333,chr(185):300,chr(186):330,chr(187):500,chr(188):750,chr(189):750,chr(190):750,chr(191):500,chr(192):722,chr(193):722,chr(194):722,chr(195):722,chr(196):722,chr(197):722,
    chr(198):1000,chr(199):722,chr(200):667,chr(201):667,chr(202):667,chr(203):667,chr(204):389,chr(205):389,chr(206):389,chr(207):389,chr(208):722,chr(209):722,chr(210):778,chr(211):778,chr(212):778,chr(213):778,chr(214):778,chr(215):570,chr(216):778,chr(217):722,chr(218):722,chr(219):722,
    chr(220):722,chr(221):722,chr(222):611,chr(223):556,chr(224):500,chr(225):500,chr(226):500,chr(227):500,chr(228):500,chr(229):500,chr(230):722,chr(231):444,chr(232):444,chr(233):444,chr(234):444,chr(235):444,chr(236):278,chr(237):278,chr(238):278,chr(239):278,chr(240):500,chr(241):556,
    chr(242):500,chr(243):500,chr(244):500,chr(245):500,chr(246):500,chr(247):570,chr(248):500,chr(249):556,chr(250):556,chr(251):556,chr(252):556,chr(253):500,chr(254):556,chr(255):500}
    
fpdf_charwidths['timesBI']={
    chr(0):250,chr(1):250,chr(2):250,chr(3):250,chr(4):250,chr(5):250,chr(6):250,chr(7):250,chr(8):250,chr(9):250,chr(10):250,chr(11):250,chr(12):250,chr(13):250,chr(14):250,chr(15):250,chr(16):250,chr(17):250,chr(18):250,chr(19):250,chr(20):250,chr(21):250,
    chr(22):250,chr(23):250,chr(24):250,chr(25):250,chr(26):250,chr(27):250,chr(28):250,chr(29):250,chr(30):250,chr(31):250,' ':250,'!':389,'"':555,'#':500,'$':500,'%':833,'&':778,'\'':278,'(':333,')':333,'*':500,'+':570,
    ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':333,';':333,'<':570,'=':570,'>':570,'?':500,'@':832,'A':667,
    'B':667,'C':667,'D':722,'E':667,'F':667,'G':722,'H':778,'I':389,'J':500,'K':667,'L':611,'M':889,'N':722,'O':722,'P':611,'Q':722,'R':667,'S':556,'T':611,'U':722,'V':667,'W':889,
    'X':667,'Y':611,'Z':611,'[':333,'\\':278,']':333,'^':570,'_':500,'`':333,'a':500,'b':500,'c':444,'d':500,'e':444,'f':333,'g':500,'h':556,'i':278,'j':278,'k':500,'l':278,'m':778,
    'n':556,'o':500,'p':500,'q':500,'r':389,'s':389,'t':278,'u':556,'v':444,'w':667,'x':500,'y':444,'z':389,'{':348,'|':220,'}':348,'~':570,chr(127):350,chr(128):500,chr(129):350,chr(130):333,chr(131):500,
    chr(132):500,chr(133):1000,chr(134):500,chr(135):500,chr(136):333,chr(137):1000,chr(138):556,chr(139):333,chr(140):944,chr(141):350,chr(142):611,chr(143):350,chr(144):350,chr(145):333,chr(146):333,chr(147):500,chr(148):500,chr(149):350,chr(150):500,chr(151):1000,chr(152):333,chr(153):1000,
    chr(154):389,chr(155):333,chr(156):722,chr(157):350,chr(158):389,chr(159):611,chr(160):250,chr(161):389,chr(162):500,chr(163):500,chr(164):500,chr(165):500,chr(166):220,chr(167):500,chr(168):333,chr(169):747,chr(170):266,chr(171):500,chr(172):606,chr(173):333,chr(174):747,chr(175):333,
    chr(176):400,chr(177):570,chr(178):300,chr(179):300,chr(180):333,chr(181):576,chr(182):500,chr(183):250,chr(184):333,chr(185):300,chr(186):300,chr(187):500,chr(188):750,chr(189):750,chr(190):750,chr(191):500,chr(192):667,chr(193):667,chr(194):667,chr(195):667,chr(196):667,chr(197):667,
    chr(198):944,chr(199):667,chr(200):667,chr(201):667,chr(202):667,chr(203):667,chr(204):389,chr(205):389,chr(206):389,chr(207):389,chr(208):722,chr(209):722,chr(210):722,chr(211):722,chr(212):722,chr(213):722,chr(214):722,chr(215):570,chr(216):722,chr(217):722,chr(218):722,chr(219):722,
    chr(220):722,chr(221):611,chr(222):611,chr(223):500,chr(224):500,chr(225):500,chr(226):500,chr(227):500,chr(228):500,chr(229):500,chr(230):722,chr(231):444,chr(232):444,chr(233):444,chr(234):444,chr(235):444,chr(236):278,chr(237):278,chr(238):278,chr(239):278,chr(240):500,chr(241):556,
    chr(242):500,chr(243):500,chr(244):500,chr(245):500,chr(246):500,chr(247):570,chr(248):500,chr(249):556,chr(250):556,chr(251):556,chr(252):556,chr(253):444,chr(254):500,chr(255):444}

fpdf_charwidths['timesI']={
    chr(0):250,chr(1):250,chr(2):250,chr(3):250,chr(4):250,chr(5):250,chr(6):250,chr(7):250,chr(8):250,chr(9):250,chr(10):250,chr(11):250,chr(12):250,chr(13):250,chr(14):250,chr(15):250,chr(16):250,chr(17):250,chr(18):250,chr(19):250,chr(20):250,chr(21):250,
    chr(22):250,chr(23):250,chr(24):250,chr(25):250,chr(26):250,chr(27):250,chr(28):250,chr(29):250,chr(30):250,chr(31):250,' ':250,'!':333,'"':420,'#':500,'$':500,'%':833,'&':778,'\'':214,'(':333,')':333,'*':500,'+':675,
    ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':333,';':333,'<':675,'=':675,'>':675,'?':500,'@':920,'A':611,
    'B':611,'C':667,'D':722,'E':611,'F':611,'G':722,'H':722,'I':333,'J':444,'K':667,'L':556,'M':833,'N':667,'O':722,'P':611,'Q':722,'R':611,'S':500,'T':556,'U':722,'V':611,'W':833,
    'X':611,'Y':556,'Z':556,'[':389,'\\':278,']':389,'^':422,'_':500,'`':333,'a':500,'b':500,'c':444,'d':500,'e':444,'f':278,'g':500,'h':500,'i':278,'j':278,'k':444,'l':278,'m':722,
    'n':500,'o':500,'p':500,'q':500,'r':389,'s':389,'t':278,'u':500,'v':444,'w':667,'x':444,'y':444,'z':389,'{':400,'|':275,'}':400,'~':541,chr(127):350,chr(128):500,chr(129):350,chr(130):333,chr(131):500,
    chr(132):556,chr(133):889,chr(134):500,chr(135):500,chr(136):333,chr(137):1000,chr(138):500,chr(139):333,chr(140):944,chr(141):350,chr(142):556,chr(143):350,chr(144):350,chr(145):333,chr(146):333,chr(147):556,chr(148):556,chr(149):350,chr(150):500,chr(151):889,chr(152):333,chr(153):980,
    chr(154):389,chr(155):333,chr(156):667,chr(157):350,chr(158):389,chr(159):556,chr(160):250,chr(161):389,chr(162):500,chr(163):500,chr(164):500,chr(165):500,chr(166):275,chr(167):500,chr(168):333,chr(169):760,chr(170):276,chr(171):500,chr(172):675,chr(173):333,chr(174):760,chr(175):333,
    chr(176):400,chr(177):675,chr(178):300,chr(179):300,chr(180):333,chr(181):500,chr(182):523,chr(183):250,chr(184):333,chr(185):300,chr(186):310,chr(187):500,chr(188):750,chr(189):750,chr(190):750,chr(191):500,chr(192):611,chr(193):611,chr(194):611,chr(195):611,chr(196):611,chr(197):611,
    chr(198):889,chr(199):667,chr(200):611,chr(201):611,chr(202):611,chr(203):611,chr(204):333,chr(205):333,chr(206):333,chr(207):333,chr(208):722,chr(209):667,chr(210):722,chr(211):722,chr(212):722,chr(213):722,chr(214):722,chr(215):675,chr(216):722,chr(217):722,chr(218):722,chr(219):722,
    chr(220):722,chr(221):556,chr(222):611,chr(223):500,chr(224):500,chr(225):500,chr(226):500,chr(227):500,chr(228):500,chr(229):500,chr(230):667,chr(231):444,chr(232):444,chr(233):444,chr(234):444,chr(235):444,chr(236):278,chr(237):278,chr(238):278,chr(239):278,chr(240):500,chr(241):500,
    chr(242):500,chr(243):500,chr(244):500,chr(245):500,chr(246):500,chr(247):675,chr(248):500,chr(249):500,chr(250):500,chr(251):500,chr(252):500,chr(253):444,chr(254):500,chr(255):444}

fpdf_charwidths['zapfdingbats']={
    chr(0):0,chr(1):0,chr(2):0,chr(3):0,chr(4):0,chr(5):0,chr(6):0,chr(7):0,chr(8):0,chr(9):0,chr(10):0,chr(11):0,chr(12):0,chr(13):0,chr(14):0,chr(15):0,chr(16):0,chr(17):0,chr(18):0,chr(19):0,chr(20):0,chr(21):0,
    chr(22):0,chr(23):0,chr(24):0,chr(25):0,chr(26):0,chr(27):0,chr(28):0,chr(29):0,chr(30):0,chr(31):0,' ':278,'!':974,'"':961,'#':974,'$':980,'%':719,'&':789,'\'':790,'(':791,')':690,'*':960,'+':939,
    ',':549,'-':855,'.':911,'/':933,'0':911,'1':945,'2':974,'3':755,'4':846,'5':762,'6':761,'7':571,'8':677,'9':763,':':760,';':759,'<':754,'=':494,'>':552,'?':537,'@':577,'A':692,
    'B':786,'C':788,'D':788,'E':790,'F':793,'G':794,'H':816,'I':823,'J':789,'K':841,'L':823,'M':833,'N':816,'O':831,'P':923,'Q':744,'R':723,'S':749,'T':790,'U':792,'V':695,'W':776,
    'X':768,'Y':792,'Z':759,'[':707,'\\':708,']':682,'^':701,'_':826,'`':815,'a':789,'b':789,'c':707,'d':687,'e':696,'f':689,'g':786,'h':787,'i':713,'j':791,'k':785,'l':791,'m':873,
    'n':761,'o':762,'p':762,'q':759,'r':759,'s':892,'t':892,'u':788,'v':784,'w':438,'x':138,'y':277,'z':415,'{':392,'|':392,'}':668,'~':668,chr(127):0,chr(128):390,chr(129):390,chr(130):317,chr(131):317,
    chr(132):276,chr(133):276,chr(134):509,chr(135):509,chr(136):410,chr(137):410,chr(138):234,chr(139):234,chr(140):334,chr(141):334,chr(142):0,chr(143):0,chr(144):0,chr(145):0,chr(146):0,chr(147):0,chr(148):0,chr(149):0,chr(150):0,chr(151):0,chr(152):0,chr(153):0,
    chr(154):0,chr(155):0,chr(156):0,chr(157):0,chr(158):0,chr(159):0,chr(160):0,chr(161):732,chr(162):544,chr(163):544,chr(164):910,chr(165):667,chr(166):760,chr(167):760,chr(168):776,chr(169):595,chr(170):694,chr(171):626,chr(172):788,chr(173):788,chr(174):788,chr(175):788,
    chr(176):788,chr(177):788,chr(178):788,chr(179):788,chr(180):788,chr(181):788,chr(182):788,chr(183):788,chr(184):788,chr(185):788,chr(186):788,chr(187):788,chr(188):788,chr(189):788,chr(190):788,chr(191):788,chr(192):788,chr(193):788,chr(194):788,chr(195):788,chr(196):788,chr(197):788,
    chr(198):788,chr(199):788,chr(200):788,chr(201):788,chr(202):788,chr(203):788,chr(204):788,chr(205):788,chr(206):788,chr(207):788,chr(208):788,chr(209):788,chr(210):788,chr(211):788,chr(212):894,chr(213):838,chr(214):1016,chr(215):458,chr(216):748,chr(217):924,chr(218):748,chr(219):918,
    chr(220):927,chr(221):928,chr(222):928,chr(223):834,chr(224):873,chr(225):828,chr(226):924,chr(227):924,chr(228):917,chr(229):930,chr(230):931,chr(231):463,chr(232):883,chr(233):836,chr(234):836,chr(235):867,chr(236):867,chr(237):696,chr(238):696,chr(239):874,chr(240):0,chr(241):874,
    chr(242):760,chr(243):946,chr(244):771,chr(245):865,chr(246):771,chr(247):888,chr(248):967,chr(249):888,chr(250):831,chr(251):873,chr(252):927,chr(253):970,chr(254):918,chr(255):0}


# -*- coding: utf-8 -*-
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
# *******************************************************************************/

from PHPutils import *
from datetime import datetime
import math
import os, sys, zlib, struct

try:
    # Check if PIL is available, necessary for JPEG support.
    import Image
except ImportError:
    Image = None

# Global variables
FPDF_VERSION='1.54'
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
        # Extract info from a JPEG file
        if Image is None:
            this.Error('PIL not installed')
        try:
            f = open(filename, 'rb')
            im = Image.open(f)
        except Exception, e:
            this.Error('Missing or incorrect image file: %s. Error: %s' % (filename, str(e)))
        else:
            a = im.size
        # We shouldn't get into here, as Jpeg is RGB=8bpp right(?), but, just in case...
        bpc=8
        if im.mode == 'RGB':
            colspace='DeviceRGB'
        elif im.mode == 'CMYK':
            colspace='DeviceCMYK'
        else:
            colspace='DeviceGray'

        # Read whole file from the start
        f.seek(0)
        data = f.read()
        f.close()
        return {'w':a[0],'h':a[1],'cs':colspace,'bpc':bpc,'f':'DCTDecode','data':data}

    def _parsepng(this, name):
        #Extract info from a PNG file
        f=file(name,'rb')
        if(not f):
            this.Error("Can't open image file: "+name)
        #Check signature
        if(f.read(8)!='\x89'+'PNG'+'\r'+'\n'+'\x1a'+'\n'):
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
                    pos=strpos(t,'\x00')
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


    def code39(self, txt, x, y, w=1.5, h=5.0):
        wide = w
        narrow = w /3.0
        gap = narrow

        barChar={}
        barChar['0'] = 'nnnwwnwnn'
        barChar['1'] = 'wnnwnnnnw'
        barChar['2'] = 'nnwwnnnnw'
        barChar['3'] = 'wnwwnnnnn'
        barChar['4'] = 'nnnwwnnnw'
        barChar['5'] = 'wnnwwnnnn'
        barChar['6'] = 'nnwwwnnnn'
        barChar['7'] = 'nnnwnnwnw'
        barChar['8'] = 'wnnwnnwnn'
        barChar['9'] = 'nnwwnnwnn'
        barChar['A'] = 'wnnnnwnnw'
        barChar['B'] = 'nnwnnwnnw'
        barChar['C'] = 'wnwnnwnnn'
        barChar['D'] = 'nnnnwwnnw'
        barChar['E'] = 'wnnnwwnnn'
        barChar['F'] = 'nnwnwwnnn'
        barChar['G'] = 'nnnnnwwnw'
        barChar['H'] = 'wnnnnwwnn'
        barChar['I'] = 'nnwnnwwnn'
        barChar['J'] = 'nnnnwwwnn'
        barChar['K'] = 'wnnnnnnww'
        barChar['L'] = 'nnwnnnnww'
        barChar['M'] = 'wnwnnnnwn'
        barChar['N'] = 'nnnnwnnww'
        barChar['O'] = 'wnnnwnnwn'
        barChar['P'] = 'nnwnwnnwn'
        barChar['Q'] = 'nnnnnnwww'
        barChar['R'] = 'wnnnnnwwn'
        barChar['S'] = 'nnwnnnwwn'
        barChar['T'] = 'nnnnwnwwn'
        barChar['U'] = 'wwnnnnnnw'
        barChar['V'] = 'nwwnnnnnw'
        barChar['W'] = 'wwwnnnnnn'
        barChar['X'] = 'nwnnwnnnw'
        barChar['Y'] = 'wwnnwnnnn'
        barChar['Z'] = 'nwwnwnnnn'
        barChar['-'] = 'nwnnnnwnw'
        barChar['.'] = 'wwnnnnwnn'
        barChar[' '] = 'nwwnnnwnn'
        barChar['*'] = 'nwnnwnwnn'
        barChar['$'] = 'nwnwnwnnn'
        barChar['/'] = 'nwnwnnnwn'
        barChar['+'] = 'nwnnnwnwn'
        barChar['%'] = 'nnnwnwnwn'

        self.SetFillColor(0)
        code = txt	
            
        code = code.upper()
        for i in xrange (0, len(code), 2):
            charBar = code[i];

            if not charBar in barChar.keys():
                raise RuntimeError ('Caracter "%s" inválido para el código de barras' % charBar)

            seq= ''
            for s in xrange(0, len(barChar[charBar])):
                seq += barChar[charBar][s] 

            for bar in xrange(0, len(seq)):
                if seq[bar] == 'n':
                    lineWidth = narrow
                else:
                    lineWidth = wide

                if bar % 2 == 0:
                    self.Rect(x,y,lineWidth,h,'F')
                x += lineWidth
        x += gap

#End of class

# Fonts:
    
fpdf_charwidths['courier']={}

for i in xrange(0,256):
    fpdf_charwidths['courier'][chr(i)]=600
    fpdf_charwidths['courierB']=fpdf_charwidths['courier']
    fpdf_charwidths['courierI']=fpdf_charwidths['courier']
    fpdf_charwidths['courierBI']=fpdf_charwidths['courier']

fpdf_charwidths['helvetica']={
    '\x00':278,'\x01':278,'\x02':278,'\x03':278,'\x04':278,'\x05':278,'\x06':278,'\x07':278,'\x08':278,'\t':278,'\n':278,'\x0b':278,'\x0c':278,'\r':278,'\x0e':278,'\x0f':278,'\x10':278,'\x11':278,'\x12':278,'\x13':278,'\x14':278,'\x15':278,
    '\x16':278,'\x17':278,'\x18':278,'\x19':278,'\x1a':278,'\x1b':278,'\x1c':278,'\x1d':278,'\x1e':278,'\x1f':278,' ':278,'!':278,'"':355,'#':556,'$':556,'%':889,'&':667,'\'':191,'(':333,')':333,'*':389,'+':584,
    ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':278,';':278,'<':584,'=':584,'>':584,'?':556,'@':1015,'A':667,
    'B':667,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':500,'K':667,'L':556,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
    'X':667,'Y':667,'Z':611,'[':278,'\\':278,']':278,'^':469,'_':556,'`':333,'a':556,'b':556,'c':500,'d':556,'e':556,'f':278,'g':556,'h':556,'i':222,'j':222,'k':500,'l':222,'m':833,
    'n':556,'o':556,'p':556,'q':556,'r':333,'s':500,'t':278,'u':556,'v':500,'w':722,'x':500,'y':500,'z':500,'{':334,'|':260,'}':334,'~':584,'\x7f':350,'\x80':556,'\x81':350,'\x82':222,'\x83':556,
    '\x84':333,'\x85':1000,'\x86':556,'\x87':556,'\x88':333,'\x89':1000,'\x8a':667,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':222,'\x92':222,'\x93':333,'\x94':333,'\x95':350,'\x96':556,'\x97':1000,'\x98':333,'\x99':1000,
    '\x9a':500,'\x9b':333,'\x9c':944,'\x9d':350,'\x9e':500,'\x9f':667,'\xa0':278,'\xa1':333,'\xa2':556,'\xa3':556,'\xa4':556,'\xa5':556,'\xa6':260,'\xa7':556,'\xa8':333,'\xa9':737,'\xaa':370,'\xab':556,'\xac':584,'\xad':333,'\xae':737,'\xaf':333,
    '\xb0':400,'\xb1':584,'\xb2':333,'\xb3':333,'\xb4':333,'\xb5':556,'\xb6':537,'\xb7':278,'\xb8':333,'\xb9':333,'\xba':365,'\xbb':556,'\xbc':834,'\xbd':834,'\xbe':834,'\xbf':611,'\xc0':667,'\xc1':667,'\xc2':667,'\xc3':667,'\xc4':667,'\xc5':667,
    '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':278,'\xcd':278,'\xce':278,'\xcf':278,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':584,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
    '\xdc':722,'\xdd':667,'\xde':667,'\xdf':611,'\xe0':556,'\xe1':556,'\xe2':556,'\xe3':556,'\xe4':556,'\xe5':556,'\xe6':889,'\xe7':500,'\xe8':556,'\xe9':556,'\xea':556,'\xeb':556,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':556,'\xf1':556,
    '\xf2':556,'\xf3':556,'\xf4':556,'\xf5':556,'\xf6':556,'\xf7':584,'\xf8':611,'\xf9':556,'\xfa':556,'\xfb':556,'\xfc':556,'\xfd':500,'\xfe':556,'\xff':500}

fpdf_charwidths['helveticaB']={
    '\x00':278,'\x01':278,'\x02':278,'\x03':278,'\x04':278,'\x05':278,'\x06':278,'\x07':278,'\x08':278,'\t':278,'\n':278,'\x0b':278,'\x0c':278,'\r':278,'\x0e':278,'\x0f':278,'\x10':278,'\x11':278,'\x12':278,'\x13':278,'\x14':278,'\x15':278,
    '\x16':278,'\x17':278,'\x18':278,'\x19':278,'\x1a':278,'\x1b':278,'\x1c':278,'\x1d':278,'\x1e':278,'\x1f':278,' ':278,'!':333,'"':474,'#':556,'$':556,'%':889,'&':722,'\'':238,'(':333,')':333,'*':389,'+':584,
    ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':333,';':333,'<':584,'=':584,'>':584,'?':611,'@':975,'A':722,
    'B':722,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':556,'K':722,'L':611,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
    'X':667,'Y':667,'Z':611,'[':333,'\\':278,']':333,'^':584,'_':556,'`':333,'a':556,'b':611,'c':556,'d':611,'e':556,'f':333,'g':611,'h':611,'i':278,'j':278,'k':556,'l':278,'m':889,
    'n':611,'o':611,'p':611,'q':611,'r':389,'s':556,'t':333,'u':611,'v':556,'w':778,'x':556,'y':556,'z':500,'{':389,'|':280,'}':389,'~':584,'\x7f':350,'\x80':556,'\x81':350,'\x82':278,'\x83':556,
    '\x84':500,'\x85':1000,'\x86':556,'\x87':556,'\x88':333,'\x89':1000,'\x8a':667,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':278,'\x92':278,'\x93':500,'\x94':500,'\x95':350,'\x96':556,'\x97':1000,'\x98':333,'\x99':1000,
    '\x9a':556,'\x9b':333,'\x9c':944,'\x9d':350,'\x9e':500,'\x9f':667,'\xa0':278,'\xa1':333,'\xa2':556,'\xa3':556,'\xa4':556,'\xa5':556,'\xa6':280,'\xa7':556,'\xa8':333,'\xa9':737,'\xaa':370,'\xab':556,'\xac':584,'\xad':333,'\xae':737,'\xaf':333,
    '\xb0':400,'\xb1':584,'\xb2':333,'\xb3':333,'\xb4':333,'\xb5':611,'\xb6':556,'\xb7':278,'\xb8':333,'\xb9':333,'\xba':365,'\xbb':556,'\xbc':834,'\xbd':834,'\xbe':834,'\xbf':611,'\xc0':722,'\xc1':722,'\xc2':722,'\xc3':722,'\xc4':722,'\xc5':722,
    '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':278,'\xcd':278,'\xce':278,'\xcf':278,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':584,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
    '\xdc':722,'\xdd':667,'\xde':667,'\xdf':611,'\xe0':556,'\xe1':556,'\xe2':556,'\xe3':556,'\xe4':556,'\xe5':556,'\xe6':889,'\xe7':556,'\xe8':556,'\xe9':556,'\xea':556,'\xeb':556,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':611,'\xf1':611,
    '\xf2':611,'\xf3':611,'\xf4':611,'\xf5':611,'\xf6':611,'\xf7':584,'\xf8':611,'\xf9':611,'\xfa':611,'\xfb':611,'\xfc':611,'\xfd':556,'\xfe':611,'\xff':556
}

fpdf_charwidths['helveticaBI']={
    '\x00':278,'\x01':278,'\x02':278,'\x03':278,'\x04':278,'\x05':278,'\x06':278,'\x07':278,'\x08':278,'\t':278,'\n':278,'\x0b':278,'\x0c':278,'\r':278,'\x0e':278,'\x0f':278,'\x10':278,'\x11':278,'\x12':278,'\x13':278,'\x14':278,'\x15':278,
    '\x16':278,'\x17':278,'\x18':278,'\x19':278,'\x1a':278,'\x1b':278,'\x1c':278,'\x1d':278,'\x1e':278,'\x1f':278,' ':278,'!':333,'"':474,'#':556,'$':556,'%':889,'&':722,'\'':238,'(':333,')':333,'*':389,'+':584,
    ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':333,';':333,'<':584,'=':584,'>':584,'?':611,'@':975,'A':722,
    'B':722,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':556,'K':722,'L':611,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
    'X':667,'Y':667,'Z':611,'[':333,'\\':278,']':333,'^':584,'_':556,'`':333,'a':556,'b':611,'c':556,'d':611,'e':556,'f':333,'g':611,'h':611,'i':278,'j':278,'k':556,'l':278,'m':889,
    'n':611,'o':611,'p':611,'q':611,'r':389,'s':556,'t':333,'u':611,'v':556,'w':778,'x':556,'y':556,'z':500,'{':389,'|':280,'}':389,'~':584,'\x7f':350,'\x80':556,'\x81':350,'\x82':278,'\x83':556,
    '\x84':500,'\x85':1000,'\x86':556,'\x87':556,'\x88':333,'\x89':1000,'\x8a':667,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':278,'\x92':278,'\x93':500,'\x94':500,'\x95':350,'\x96':556,'\x97':1000,'\x98':333,'\x99':1000,
    '\x9a':556,'\x9b':333,'\x9c':944,'\x9d':350,'\x9e':500,'\x9f':667,'\xa0':278,'\xa1':333,'\xa2':556,'\xa3':556,'\xa4':556,'\xa5':556,'\xa6':280,'\xa7':556,'\xa8':333,'\xa9':737,'\xaa':370,'\xab':556,'\xac':584,'\xad':333,'\xae':737,'\xaf':333,
    '\xb0':400,'\xb1':584,'\xb2':333,'\xb3':333,'\xb4':333,'\xb5':611,'\xb6':556,'\xb7':278,'\xb8':333,'\xb9':333,'\xba':365,'\xbb':556,'\xbc':834,'\xbd':834,'\xbe':834,'\xbf':611,'\xc0':722,'\xc1':722,'\xc2':722,'\xc3':722,'\xc4':722,'\xc5':722,
    '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':278,'\xcd':278,'\xce':278,'\xcf':278,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':584,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
    '\xdc':722,'\xdd':667,'\xde':667,'\xdf':611,'\xe0':556,'\xe1':556,'\xe2':556,'\xe3':556,'\xe4':556,'\xe5':556,'\xe6':889,'\xe7':556,'\xe8':556,'\xe9':556,'\xea':556,'\xeb':556,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':611,'\xf1':611,
    '\xf2':611,'\xf3':611,'\xf4':611,'\xf5':611,'\xf6':611,'\xf7':584,'\xf8':611,'\xf9':611,'\xfa':611,'\xfb':611,'\xfc':611,'\xfd':556,'\xfe':611,'\xff':556}

fpdf_charwidths['helveticaI']={
    '\x00':278,'\x01':278,'\x02':278,'\x03':278,'\x04':278,'\x05':278,'\x06':278,'\x07':278,'\x08':278,'\t':278,'\n':278,'\x0b':278,'\x0c':278,'\r':278,'\x0e':278,'\x0f':278,'\x10':278,'\x11':278,'\x12':278,'\x13':278,'\x14':278,'\x15':278,
    '\x16':278,'\x17':278,'\x18':278,'\x19':278,'\x1a':278,'\x1b':278,'\x1c':278,'\x1d':278,'\x1e':278,'\x1f':278,' ':278,'!':278,'"':355,'#':556,'$':556,'%':889,'&':667,'\'':191,'(':333,')':333,'*':389,'+':584,
    ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':278,';':278,'<':584,'=':584,'>':584,'?':556,'@':1015,'A':667,
    'B':667,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':500,'K':667,'L':556,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
    'X':667,'Y':667,'Z':611,'[':278,'\\':278,']':278,'^':469,'_':556,'`':333,'a':556,'b':556,'c':500,'d':556,'e':556,'f':278,'g':556,'h':556,'i':222,'j':222,'k':500,'l':222,'m':833,
    'n':556,'o':556,'p':556,'q':556,'r':333,'s':500,'t':278,'u':556,'v':500,'w':722,'x':500,'y':500,'z':500,'{':334,'|':260,'}':334,'~':584,'\x7f':350,'\x80':556,'\x81':350,'\x82':222,'\x83':556,
    '\x84':333,'\x85':1000,'\x86':556,'\x87':556,'\x88':333,'\x89':1000,'\x8a':667,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':222,'\x92':222,'\x93':333,'\x94':333,'\x95':350,'\x96':556,'\x97':1000,'\x98':333,'\x99':1000,
    '\x9a':500,'\x9b':333,'\x9c':944,'\x9d':350,'\x9e':500,'\x9f':667,'\xa0':278,'\xa1':333,'\xa2':556,'\xa3':556,'\xa4':556,'\xa5':556,'\xa6':260,'\xa7':556,'\xa8':333,'\xa9':737,'\xaa':370,'\xab':556,'\xac':584,'\xad':333,'\xae':737,'\xaf':333,
    '\xb0':400,'\xb1':584,'\xb2':333,'\xb3':333,'\xb4':333,'\xb5':556,'\xb6':537,'\xb7':278,'\xb8':333,'\xb9':333,'\xba':365,'\xbb':556,'\xbc':834,'\xbd':834,'\xbe':834,'\xbf':611,'\xc0':667,'\xc1':667,'\xc2':667,'\xc3':667,'\xc4':667,'\xc5':667,
    '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':278,'\xcd':278,'\xce':278,'\xcf':278,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':584,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
    '\xdc':722,'\xdd':667,'\xde':667,'\xdf':611,'\xe0':556,'\xe1':556,'\xe2':556,'\xe3':556,'\xe4':556,'\xe5':556,'\xe6':889,'\xe7':500,'\xe8':556,'\xe9':556,'\xea':556,'\xeb':556,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':556,'\xf1':556,
    '\xf2':556,'\xf3':556,'\xf4':556,'\xf5':556,'\xf6':556,'\xf7':584,'\xf8':611,'\xf9':556,'\xfa':556,'\xfb':556,'\xfc':556,'\xfd':500,'\xfe':556,'\xff':500}

fpdf_charwidths['symbol']={
    '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
    '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':333,'"':713,'#':500,'$':549,'%':833,'&':778,'\'':439,'(':333,')':333,'*':500,'+':549,
    ',':250,'-':549,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':278,';':278,'<':549,'=':549,'>':549,'?':444,'@':549,'A':722,
    'B':667,'C':722,'D':612,'E':611,'F':763,'G':603,'H':722,'I':333,'J':631,'K':722,'L':686,'M':889,'N':722,'O':722,'P':768,'Q':741,'R':556,'S':592,'T':611,'U':690,'V':439,'W':768,
    'X':645,'Y':795,'Z':611,'[':333,'\\':863,']':333,'^':658,'_':500,'`':500,'a':631,'b':549,'c':549,'d':494,'e':439,'f':521,'g':411,'h':603,'i':329,'j':603,'k':549,'l':549,'m':576,
    'n':521,'o':549,'p':549,'q':521,'r':549,'s':603,'t':439,'u':576,'v':713,'w':686,'x':493,'y':686,'z':494,'{':480,'|':200,'}':480,'~':549,'\x7f':0,'\x80':0,'\x81':0,'\x82':0,'\x83':0,
    '\x84':0,'\x85':0,'\x86':0,'\x87':0,'\x88':0,'\x89':0,'\x8a':0,'\x8b':0,'\x8c':0,'\x8d':0,'\x8e':0,'\x8f':0,'\x90':0,'\x91':0,'\x92':0,'\x93':0,'\x94':0,'\x95':0,'\x96':0,'\x97':0,'\x98':0,'\x99':0,
    '\x9a':0,'\x9b':0,'\x9c':0,'\x9d':0,'\x9e':0,'\x9f':0,'\xa0':750,'\xa1':620,'\xa2':247,'\xa3':549,'\xa4':167,'\xa5':713,'\xa6':500,'\xa7':753,'\xa8':753,'\xa9':753,'\xaa':753,'\xab':1042,'\xac':987,'\xad':603,'\xae':987,'\xaf':603,
    '\xb0':400,'\xb1':549,'\xb2':411,'\xb3':549,'\xb4':549,'\xb5':713,'\xb6':494,'\xb7':460,'\xb8':549,'\xb9':549,'\xba':549,'\xbb':549,'\xbc':1000,'\xbd':603,'\xbe':1000,'\xbf':658,'\xc0':823,'\xc1':686,'\xc2':795,'\xc3':987,'\xc4':768,'\xc5':768,
    '\xc6':823,'\xc7':768,'\xc8':768,'\xc9':713,'\xca':713,'\xcb':713,'\xcc':713,'\xcd':713,'\xce':713,'\xcf':713,'\xd0':768,'\xd1':713,'\xd2':790,'\xd3':790,'\xd4':890,'\xd5':823,'\xd6':549,'\xd7':250,'\xd8':713,'\xd9':603,'\xda':603,'\xdb':1042,
    '\xdc':987,'\xdd':603,'\xde':987,'\xdf':603,'\xe0':494,'\xe1':329,'\xe2':790,'\xe3':790,'\xe4':786,'\xe5':713,'\xe6':384,'\xe7':384,'\xe8':384,'\xe9':384,'\xea':384,'\xeb':384,'\xec':494,'\xed':494,'\xee':494,'\xef':494,'\xf0':0,'\xf1':329,
    '\xf2':274,'\xf3':686,'\xf4':686,'\xf5':686,'\xf6':384,'\xf7':384,'\xf8':384,'\xf9':384,'\xfa':384,'\xfb':384,'\xfc':494,'\xfd':494,'\xfe':494,'\xff':0}
    
fpdf_charwidths['times']={
    '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
    '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':333,'"':408,'#':500,'$':500,'%':833,'&':778,'\'':180,'(':333,')':333,'*':500,'+':564,
    ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':278,';':278,'<':564,'=':564,'>':564,'?':444,'@':921,'A':722,
    'B':667,'C':667,'D':722,'E':611,'F':556,'G':722,'H':722,'I':333,'J':389,'K':722,'L':611,'M':889,'N':722,'O':722,'P':556,'Q':722,'R':667,'S':556,'T':611,'U':722,'V':722,'W':944,
    'X':722,'Y':722,'Z':611,'[':333,'\\':278,']':333,'^':469,'_':500,'`':333,'a':444,'b':500,'c':444,'d':500,'e':444,'f':333,'g':500,'h':500,'i':278,'j':278,'k':500,'l':278,'m':778,
    'n':500,'o':500,'p':500,'q':500,'r':333,'s':389,'t':278,'u':500,'v':500,'w':722,'x':500,'y':500,'z':444,'{':480,'|':200,'}':480,'~':541,'\x7f':350,'\x80':500,'\x81':350,'\x82':333,'\x83':500,
    '\x84':444,'\x85':1000,'\x86':500,'\x87':500,'\x88':333,'\x89':1000,'\x8a':556,'\x8b':333,'\x8c':889,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':333,'\x92':333,'\x93':444,'\x94':444,'\x95':350,'\x96':500,'\x97':1000,'\x98':333,'\x99':980,
    '\x9a':389,'\x9b':333,'\x9c':722,'\x9d':350,'\x9e':444,'\x9f':722,'\xa0':250,'\xa1':333,'\xa2':500,'\xa3':500,'\xa4':500,'\xa5':500,'\xa6':200,'\xa7':500,'\xa8':333,'\xa9':760,'\xaa':276,'\xab':500,'\xac':564,'\xad':333,'\xae':760,'\xaf':333,
    '\xb0':400,'\xb1':564,'\xb2':300,'\xb3':300,'\xb4':333,'\xb5':500,'\xb6':453,'\xb7':250,'\xb8':333,'\xb9':300,'\xba':310,'\xbb':500,'\xbc':750,'\xbd':750,'\xbe':750,'\xbf':444,'\xc0':722,'\xc1':722,'\xc2':722,'\xc3':722,'\xc4':722,'\xc5':722,
    '\xc6':889,'\xc7':667,'\xc8':611,'\xc9':611,'\xca':611,'\xcb':611,'\xcc':333,'\xcd':333,'\xce':333,'\xcf':333,'\xd0':722,'\xd1':722,'\xd2':722,'\xd3':722,'\xd4':722,'\xd5':722,'\xd6':722,'\xd7':564,'\xd8':722,'\xd9':722,'\xda':722,'\xdb':722,
    '\xdc':722,'\xdd':722,'\xde':556,'\xdf':500,'\xe0':444,'\xe1':444,'\xe2':444,'\xe3':444,'\xe4':444,'\xe5':444,'\xe6':667,'\xe7':444,'\xe8':444,'\xe9':444,'\xea':444,'\xeb':444,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':500,'\xf1':500,
    '\xf2':500,'\xf3':500,'\xf4':500,'\xf5':500,'\xf6':500,'\xf7':564,'\xf8':500,'\xf9':500,'\xfa':500,'\xfb':500,'\xfc':500,'\xfd':500,'\xfe':500,'\xff':500}

fpdf_charwidths['timesB']={
    '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
    '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':333,'"':555,'#':500,'$':500,'%':1000,'&':833,'\'':278,'(':333,')':333,'*':500,'+':570,
    ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':333,';':333,'<':570,'=':570,'>':570,'?':500,'@':930,'A':722,
    'B':667,'C':722,'D':722,'E':667,'F':611,'G':778,'H':778,'I':389,'J':500,'K':778,'L':667,'M':944,'N':722,'O':778,'P':611,'Q':778,'R':722,'S':556,'T':667,'U':722,'V':722,'W':1000,
    'X':722,'Y':722,'Z':667,'[':333,'\\':278,']':333,'^':581,'_':500,'`':333,'a':500,'b':556,'c':444,'d':556,'e':444,'f':333,'g':500,'h':556,'i':278,'j':333,'k':556,'l':278,'m':833,
    'n':556,'o':500,'p':556,'q':556,'r':444,'s':389,'t':333,'u':556,'v':500,'w':722,'x':500,'y':500,'z':444,'{':394,'|':220,'}':394,'~':520,'\x7f':350,'\x80':500,'\x81':350,'\x82':333,'\x83':500,
    '\x84':500,'\x85':1000,'\x86':500,'\x87':500,'\x88':333,'\x89':1000,'\x8a':556,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':667,'\x8f':350,'\x90':350,'\x91':333,'\x92':333,'\x93':500,'\x94':500,'\x95':350,'\x96':500,'\x97':1000,'\x98':333,'\x99':1000,
    '\x9a':389,'\x9b':333,'\x9c':722,'\x9d':350,'\x9e':444,'\x9f':722,'\xa0':250,'\xa1':333,'\xa2':500,'\xa3':500,'\xa4':500,'\xa5':500,'\xa6':220,'\xa7':500,'\xa8':333,'\xa9':747,'\xaa':300,'\xab':500,'\xac':570,'\xad':333,'\xae':747,'\xaf':333,
    '\xb0':400,'\xb1':570,'\xb2':300,'\xb3':300,'\xb4':333,'\xb5':556,'\xb6':540,'\xb7':250,'\xb8':333,'\xb9':300,'\xba':330,'\xbb':500,'\xbc':750,'\xbd':750,'\xbe':750,'\xbf':500,'\xc0':722,'\xc1':722,'\xc2':722,'\xc3':722,'\xc4':722,'\xc5':722,
    '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':389,'\xcd':389,'\xce':389,'\xcf':389,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':570,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
    '\xdc':722,'\xdd':722,'\xde':611,'\xdf':556,'\xe0':500,'\xe1':500,'\xe2':500,'\xe3':500,'\xe4':500,'\xe5':500,'\xe6':722,'\xe7':444,'\xe8':444,'\xe9':444,'\xea':444,'\xeb':444,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':500,'\xf1':556,
    '\xf2':500,'\xf3':500,'\xf4':500,'\xf5':500,'\xf6':500,'\xf7':570,'\xf8':500,'\xf9':556,'\xfa':556,'\xfb':556,'\xfc':556,'\xfd':500,'\xfe':556,'\xff':500}
    
fpdf_charwidths['timesBI']={
    '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
    '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':389,'"':555,'#':500,'$':500,'%':833,'&':778,'\'':278,'(':333,')':333,'*':500,'+':570,
    ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':333,';':333,'<':570,'=':570,'>':570,'?':500,'@':832,'A':667,
    'B':667,'C':667,'D':722,'E':667,'F':667,'G':722,'H':778,'I':389,'J':500,'K':667,'L':611,'M':889,'N':722,'O':722,'P':611,'Q':722,'R':667,'S':556,'T':611,'U':722,'V':667,'W':889,
    'X':667,'Y':611,'Z':611,'[':333,'\\':278,']':333,'^':570,'_':500,'`':333,'a':500,'b':500,'c':444,'d':500,'e':444,'f':333,'g':500,'h':556,'i':278,'j':278,'k':500,'l':278,'m':778,
    'n':556,'o':500,'p':500,'q':500,'r':389,'s':389,'t':278,'u':556,'v':444,'w':667,'x':500,'y':444,'z':389,'{':348,'|':220,'}':348,'~':570,'\x7f':350,'\x80':500,'\x81':350,'\x82':333,'\x83':500,
    '\x84':500,'\x85':1000,'\x86':500,'\x87':500,'\x88':333,'\x89':1000,'\x8a':556,'\x8b':333,'\x8c':944,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':333,'\x92':333,'\x93':500,'\x94':500,'\x95':350,'\x96':500,'\x97':1000,'\x98':333,'\x99':1000,
    '\x9a':389,'\x9b':333,'\x9c':722,'\x9d':350,'\x9e':389,'\x9f':611,'\xa0':250,'\xa1':389,'\xa2':500,'\xa3':500,'\xa4':500,'\xa5':500,'\xa6':220,'\xa7':500,'\xa8':333,'\xa9':747,'\xaa':266,'\xab':500,'\xac':606,'\xad':333,'\xae':747,'\xaf':333,
    '\xb0':400,'\xb1':570,'\xb2':300,'\xb3':300,'\xb4':333,'\xb5':576,'\xb6':500,'\xb7':250,'\xb8':333,'\xb9':300,'\xba':300,'\xbb':500,'\xbc':750,'\xbd':750,'\xbe':750,'\xbf':500,'\xc0':667,'\xc1':667,'\xc2':667,'\xc3':667,'\xc4':667,'\xc5':667,
    '\xc6':944,'\xc7':667,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':389,'\xcd':389,'\xce':389,'\xcf':389,'\xd0':722,'\xd1':722,'\xd2':722,'\xd3':722,'\xd4':722,'\xd5':722,'\xd6':722,'\xd7':570,'\xd8':722,'\xd9':722,'\xda':722,'\xdb':722,
    '\xdc':722,'\xdd':611,'\xde':611,'\xdf':500,'\xe0':500,'\xe1':500,'\xe2':500,'\xe3':500,'\xe4':500,'\xe5':500,'\xe6':722,'\xe7':444,'\xe8':444,'\xe9':444,'\xea':444,'\xeb':444,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':500,'\xf1':556,
    '\xf2':500,'\xf3':500,'\xf4':500,'\xf5':500,'\xf6':500,'\xf7':570,'\xf8':500,'\xf9':556,'\xfa':556,'\xfb':556,'\xfc':556,'\xfd':444,'\xfe':500,'\xff':444}

fpdf_charwidths['timesI']={
    '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
    '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':333,'"':420,'#':500,'$':500,'%':833,'&':778,'\'':214,'(':333,')':333,'*':500,'+':675,
    ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':333,';':333,'<':675,'=':675,'>':675,'?':500,'@':920,'A':611,
    'B':611,'C':667,'D':722,'E':611,'F':611,'G':722,'H':722,'I':333,'J':444,'K':667,'L':556,'M':833,'N':667,'O':722,'P':611,'Q':722,'R':611,'S':500,'T':556,'U':722,'V':611,'W':833,
    'X':611,'Y':556,'Z':556,'[':389,'\\':278,']':389,'^':422,'_':500,'`':333,'a':500,'b':500,'c':444,'d':500,'e':444,'f':278,'g':500,'h':500,'i':278,'j':278,'k':444,'l':278,'m':722,
    'n':500,'o':500,'p':500,'q':500,'r':389,'s':389,'t':278,'u':500,'v':444,'w':667,'x':444,'y':444,'z':389,'{':400,'|':275,'}':400,'~':541,'\x7f':350,'\x80':500,'\x81':350,'\x82':333,'\x83':500,
    '\x84':556,'\x85':889,'\x86':500,'\x87':500,'\x88':333,'\x89':1000,'\x8a':500,'\x8b':333,'\x8c':944,'\x8d':350,'\x8e':556,'\x8f':350,'\x90':350,'\x91':333,'\x92':333,'\x93':556,'\x94':556,'\x95':350,'\x96':500,'\x97':889,'\x98':333,'\x99':980,
    '\x9a':389,'\x9b':333,'\x9c':667,'\x9d':350,'\x9e':389,'\x9f':556,'\xa0':250,'\xa1':389,'\xa2':500,'\xa3':500,'\xa4':500,'\xa5':500,'\xa6':275,'\xa7':500,'\xa8':333,'\xa9':760,'\xaa':276,'\xab':500,'\xac':675,'\xad':333,'\xae':760,'\xaf':333,
    '\xb0':400,'\xb1':675,'\xb2':300,'\xb3':300,'\xb4':333,'\xb5':500,'\xb6':523,'\xb7':250,'\xb8':333,'\xb9':300,'\xba':310,'\xbb':500,'\xbc':750,'\xbd':750,'\xbe':750,'\xbf':500,'\xc0':611,'\xc1':611,'\xc2':611,'\xc3':611,'\xc4':611,'\xc5':611,
    '\xc6':889,'\xc7':667,'\xc8':611,'\xc9':611,'\xca':611,'\xcb':611,'\xcc':333,'\xcd':333,'\xce':333,'\xcf':333,'\xd0':722,'\xd1':667,'\xd2':722,'\xd3':722,'\xd4':722,'\xd5':722,'\xd6':722,'\xd7':675,'\xd8':722,'\xd9':722,'\xda':722,'\xdb':722,
    '\xdc':722,'\xdd':556,'\xde':611,'\xdf':500,'\xe0':500,'\xe1':500,'\xe2':500,'\xe3':500,'\xe4':500,'\xe5':500,'\xe6':667,'\xe7':444,'\xe8':444,'\xe9':444,'\xea':444,'\xeb':444,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':500,'\xf1':500,
    '\xf2':500,'\xf3':500,'\xf4':500,'\xf5':500,'\xf6':500,'\xf7':675,'\xf8':500,'\xf9':500,'\xfa':500,'\xfb':500,'\xfc':500,'\xfd':444,'\xfe':500,'\xff':444}

fpdf_charwidths['zapfdingbats']={
    '\x00':0,'\x01':0,'\x02':0,'\x03':0,'\x04':0,'\x05':0,'\x06':0,'\x07':0,'\x08':0,'\t':0,'\n':0,'\x0b':0,'\x0c':0,'\r':0,'\x0e':0,'\x0f':0,'\x10':0,'\x11':0,'\x12':0,'\x13':0,'\x14':0,'\x15':0,
    '\x16':0,'\x17':0,'\x18':0,'\x19':0,'\x1a':0,'\x1b':0,'\x1c':0,'\x1d':0,'\x1e':0,'\x1f':0,' ':278,'!':974,'"':961,'#':974,'$':980,'%':719,'&':789,'\'':790,'(':791,')':690,'*':960,'+':939,
    ',':549,'-':855,'.':911,'/':933,'0':911,'1':945,'2':974,'3':755,'4':846,'5':762,'6':761,'7':571,'8':677,'9':763,':':760,';':759,'<':754,'=':494,'>':552,'?':537,'@':577,'A':692,
    'B':786,'C':788,'D':788,'E':790,'F':793,'G':794,'H':816,'I':823,'J':789,'K':841,'L':823,'M':833,'N':816,'O':831,'P':923,'Q':744,'R':723,'S':749,'T':790,'U':792,'V':695,'W':776,
    'X':768,'Y':792,'Z':759,'[':707,'\\':708,']':682,'^':701,'_':826,'`':815,'a':789,'b':789,'c':707,'d':687,'e':696,'f':689,'g':786,'h':787,'i':713,'j':791,'k':785,'l':791,'m':873,
    'n':761,'o':762,'p':762,'q':759,'r':759,'s':892,'t':892,'u':788,'v':784,'w':438,'x':138,'y':277,'z':415,'{':392,'|':392,'}':668,'~':668,'\x7f':0,'\x80':390,'\x81':390,'\x82':317,'\x83':317,
    '\x84':276,'\x85':276,'\x86':509,'\x87':509,'\x88':410,'\x89':410,'\x8a':234,'\x8b':234,'\x8c':334,'\x8d':334,'\x8e':0,'\x8f':0,'\x90':0,'\x91':0,'\x92':0,'\x93':0,'\x94':0,'\x95':0,'\x96':0,'\x97':0,'\x98':0,'\x99':0,
    '\x9a':0,'\x9b':0,'\x9c':0,'\x9d':0,'\x9e':0,'\x9f':0,'\xa0':0,'\xa1':732,'\xa2':544,'\xa3':544,'\xa4':910,'\xa5':667,'\xa6':760,'\xa7':760,'\xa8':776,'\xa9':595,'\xaa':694,'\xab':626,'\xac':788,'\xad':788,'\xae':788,'\xaf':788,
    '\xb0':788,'\xb1':788,'\xb2':788,'\xb3':788,'\xb4':788,'\xb5':788,'\xb6':788,'\xb7':788,'\xb8':788,'\xb9':788,'\xba':788,'\xbb':788,'\xbc':788,'\xbd':788,'\xbe':788,'\xbf':788,'\xc0':788,'\xc1':788,'\xc2':788,'\xc3':788,'\xc4':788,'\xc5':788,
    '\xc6':788,'\xc7':788,'\xc8':788,'\xc9':788,'\xca':788,'\xcb':788,'\xcc':788,'\xcd':788,'\xce':788,'\xcf':788,'\xd0':788,'\xd1':788,'\xd2':788,'\xd3':788,'\xd4':894,'\xd5':838,'\xd6':1016,'\xd7':458,'\xd8':748,'\xd9':924,'\xda':748,'\xdb':918,
    '\xdc':927,'\xdd':928,'\xde':928,'\xdf':834,'\xe0':873,'\xe1':828,'\xe2':924,'\xe3':924,'\xe4':917,'\xe5':930,'\xe6':931,'\xe7':463,'\xe8':883,'\xe9':836,'\xea':836,'\xeb':867,'\xec':867,'\xed':696,'\xee':696,'\xef':874,'\xf0':0,'\xf1':874,
    '\xf2':760,'\xf3':946,'\xf4':771,'\xf5':865,'\xf6':771,'\xf7':888,'\xf8':967,'\xf9':888,'\xfa':831,'\xfb':873,'\xfc':927,'\xfd':970,'\xfe':918,'\xff':0}


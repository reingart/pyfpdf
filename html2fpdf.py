# -*- coding: latin-1 -*-
from fpdf import FPDF
from HTMLParser import HTMLParser

def px2mm(px):
    return int(px)*25.4/72.0

def hex2dec(color = "#000000"):
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    return r, g, b

class HTML2FPDF(HTMLParser):
    "Render basic HTML to FPDF"

    def __init__(self, pdf):
        HTMLParser.__init__(self)
        self.style = {}
        self.pre = False
        self.href = ''
        self.align = ''
        self.page_links = {}
        self.font_list = ("times","courier", "helvetica")
        self.pdf = pdf
        self.r = self.g = self.b = 0
        self.indent = 0
        self.bullet = []
        self.set_font("times", 12)

    def handle_data(self, data):
        if(self.href):
            self.put_link(self.href,data)
        elif self.align:
            print "cell", data, "*"
            self.pdf.cell(0,self.h,data,0,1,self.aling[0].upper())
        else:
            data = data.replace("\n"," ")
            print "write", data, "*"
            self.pdf.write(self.h,data)

    def handle_starttag(self, tag, attrs):
        if attrs:
            attrs = dict(attrs)
        print "STARTTAG", tag, attrs
        if tag=='b' or tag=='i' or tag=='u':
            self.set_style(tag,1)
        if tag=='a':
            self.href=attrs['href']
        if tag=='br':
            self.pdf.ln(5)
        if tag=='p':
            self.pdf.ln(5)
            if attrs:
                self.align=attrs['align'].lower()
        if tag=='h1':
            self.pdf.ln(5)
            self.pdf.set_text_color(150,0,0)
            self.pdf.set_font_size(22)
        if tag=='h2':
            self.pdf.ln(5)
            self.pdf.set_font_size(18)
            self.set_style('U',True)
        if tag=='h3':
            self.pdf.ln(5)
            self.pdf.set_font_size(16)
            self.set_style('U',True)
        if tag=='h4':
            self.pdf.ln(5)
            self.pdf.set_text_color(102,0,0)
            self.pdf.set_font_size(14)
        if tag=='hr':
            self.put_line()
        if tag=='pre':
            self.pdf.set_font('Courier','',11)
            self.pdf.set_font_size(11)
            self.set_style('B',False)
            self.set_style('I',False)
            self.pre = True
        if tag=='blockquote':
            self.set_text_color(100,0,45)
            self.pdf.ln(3)
        if tag=='ul':
            self.indent+=1
            self.bullet.append('\x95')
        if tag=='ol':
            self.indent+=1
            self.bullet.append(0)
        if tag=='li':
            self.pdf.ln(self.h+2)
            self.pdf.set_text_color(190,0,0)
            bullet = self.bullet[self.indent-1]
            if not isinstance(bullet, basestring):
                bullet += 1
                self.bullet[self.indent-1] = bullet
                bullet = "%s. " % bullet
            self.pdf.write(self.h,'%s%s ' % (' '*5*self.indent, bullet))
            self.set_text_color()
        if tag=='font':
            if 'color' in attrs:
                self.color = hex2dec(attrs['color'])
                self.set_text_color(*color)
                self.color = color
            if 'face' in attrs and attrs['face'].lower() in self.font_list:
                face = attrs.get('face').lower()
                self.pdf.set_font(face)
                self.font_face = face
            if 'size' in attrs:
                face = attrs.get('size')
                self.pdf.set_font('', size)
                self.font_size = size
        if tag=='img':
            if 'src' in attrs:
                x = self.pdf.get_x()
                y = self.pdf.get_y()
                w = px2mm(attrs.get('width', 0))
                h = px2mm(attrs.get('height',0))
                self.pdf.image(attrs['src'], x, y, w, h, link=self.href)
                self.pdf.set_x(x+w)
                self.pdf.set_y(y+h)
        if tag=='b' or tag=='i' or tag=='u':
            self.set_style(tag, True)

    def handle_endtag(self, tag):
        #Closing tag
        print "ENDTAG", tag
        if tag=='h1' or tag=='h2' or tag=='h3' or tag=='h4':
            self.pdf.ln(6)
            self.set_font()
            self.set_style()
        if tag=='pre':
            self.pdf.set_font(self.font or 'Times','',12)
            self.pdf.set_font_size(12)
            self.pre=False
        if tag=='blockquote':
            self.set_text_color(0,0,0)
            self.pdf.ln(3)
        if tag=='strong':
            tag='b'
        if tag=='em':
            tag='i'
        if tag=='b' or tag=='i' or tag=='u':
            self.set_style(tag, False)
        if tag=='a':
            self.href=''
        if tag=='p':
            self.align=''
        if tag in ('ul', 'ol'):
            self.indent-=1
            self.bullet.pop()
        if tag=='font':
            if self.color:
                self.pdf.set_text_color(0,0,0)
                self.color = None
            if self.font:
                self.SetFont('Times','',12)
                self.font = None

    def set_font(self, face=None, size=None):
        if face:
            self.font_face = face
        if size:
            self.font_size = size
            self.h = size / 72.0*25.4
            print "H", self.h
        self.pdf.set_font(self.font_face or 'times','',12)
        self.pdf.set_font_size(self.font_size or 12)
        self.set_style('u', False)
        self.set_style('b', False)
        self.set_style('b', False)
        self.set_text_color()        

    def set_style(self, tag=None, enable=None):
        #Modify style and select corresponding font
        if tag:
            t = self.style.get(tag.lower())
            self.style[tag.lower()] = enable
        style=''
        for s in ('b','i','u'):
            if self.style.get(s):
                style+=s
        print "SET_FONT_STYLE", style
        self.pdf.set_font('',style)

    def set_text_color(self, r=None, g=0, b=0):
        if r is None:
            self.pdf.set_text_color(self.r,self.g,self.b)
        else:
            self.pdf.set_text_color(r, g, b)
            self.r = r
            self.g = g
            self.b = b
    
    def put_link(self, url, txt):
        #Put a hyperlink
        self.set_text_color(0,0,255)
        self.set_style('u', True)
        self.pdf.write(5,txt,url)
        self.set_style('u', False)
        self.set_text_color(0)

    def put_line(self):
        self.pdf.ln(2)
        self.pdf.line(self.pdf.get_x(),self.pdf.get_y(),self.pdf.get_x()+187,self.pdf.get_y())
        self.pdf.ln(3)


html="""
<H1>html2fpdf</H1>
<h2>Basic usage</h2>
<p>You can now easily print text mixing different
styles : <B>bold</B>, <I>italic</I>, <U>underlined</U>, or
<B><I><U>all at once</U></I></B>!<BR>You can also insert links
on text, such as <A HREF="http://www.fpdf.org">www.fpdf.org</A>,
or on an image: click on the logo.<br>
<A HREF="http://www.fpdf.org">
    <img src="tutorial/logo.png" width="104" height="71"></A>
<h3>Sample List</h3>
<ul>
<li>option 1</li>
<ol>
<li>option 2</li>
</ol>
<li>option 3</li>
</ul>"""

pdf=FPDF()
#First page
pdf.add_page()
h2p = HTML2FPDF(pdf)
h2p.feed(html)
pdf.output('html.pdf','F')


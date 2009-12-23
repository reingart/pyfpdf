# -*- coding: iso-8859-1 -*-
import sys,os
from PyFPDF import FPDF

class Form:
    def __init__(self, infile):
        keys = ('name','type','x1','y1','x2','y2','font','size',
                'bold','italic','underline','foreground','background',
                'align','text','priority')
        # parse form format file and create fields dict
        self.fields = {}
        for linea in open(infile).readlines():
            kargs = {}
            for i,v in enumerate(linea.split(";")):
                if not v.startswith("'"): 
                    v = v.replace(",",".")
                else:
                    v = v#.decode('latin1')
                if v=='':
                    v = None
                else:
                    v = eval(v.strip())
                kargs[keys[i]] = v
            self.fields[kargs['name'].lower()] = kargs
        self.handlers = {'T': self.text, 'L': self.line, 'I': self.image, 
                         'B': self.rect, 'BC': self.barcode}

    def set(self, name, value):
        if name.lower() in self.fields:
            self.fields[name.lower()]['text'] = value

    def render(self, outfile):
        pdf = FPDF()
        pdf.AddPage();
        pdf.SetFont('Arial','B',16);

        for field in self.fields.values():
            self.handlers[field['type'].upper()](pdf, **field)

        pdf.Output(outfile,"F")
        
    def text(self, pdf, x1=0, y1=0, x2=0, y2=0, text='', font="arial", size=10, 
             bold=False, italic=False, underline=False, align="", *args, **kwargs):
        if text:
            font = font.strip().lower()
            if font == 'arial black':
                font = 'arial'
            style = ""
            if bold: style += "B"
            if italic: style += "I"
            if underline: style += "U"
            align = {'I':'L','D':'R','C':'C','':'',None:None}[align]
            pdf.SetFont(font,style,size)
            ##m_k = 72 / 2.54
            ##h = (size/m_k)
            pdf.SetXY(x1,y1)
            pdf.Cell(w=x2-x1,h=y2-y1,txt=text,border=0,ln=0,align=align)
            #pdf.Text(x=x1,y=y1,txt=text)

    def line(self, pdf, x1=0, y1=0, x2=0, y2=0, size=0, *args, **kwargs):
        pdf.SetLineWidth(size)
        pdf.Line(x1, y1, x2, y2)

    def rect(self, pdf, x1=0, y1=0, x2=0, y2=0, size=0, *args, **kwargs):
        pdf.SetLineWidth(size)
        pdf.Rect(x1, y1, x2-x1, y2-y1)

    def image(self, pdf, x1=0, y1=0, x2=0, y2=0, text='', *args,**kwargs):
        pdf.Image(text,x1,y1,w=x2-x1,h=y2-y1,type='',link='')

    def barcode(self, pdf, x1=0, y1=0, x2=0, y2=0, text='', font="arial", size=1,
             *args, **kwargs):
        font = font.lower().strip()
        if font == 'interleaved 2of5 nt':
            pdf.Interleaved2of5(text,x1,y1,w=size)

if __name__ == "__main__":
    f = Form("factura.csv")
    f.set("EMPRESA","Saraza")
    f.set("logo","logo.png")
    f.render("./factura.pdf")
    if sys.platform.startswith("linux"):
        os.system("evince ./factura.pdf")
    else:
        os.system("./factura.pdf")

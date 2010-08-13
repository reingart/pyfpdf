# -*- coding: iso-8859-1 -*-
import sys,os
sys.path.append("..")
import pyfpdf

cliente = {'nombre':'juan perez','cuit':'00-0000000-0','inscripto':True}
items = [
    {'cantidad':12,'descripcion':'Eggs','precio':1.00},
    {'cantidad':20,'descripcion':'Spam','precio':3.00},
    {'cantidad':1,'descripcion':'Varios','precio':0.50},
]

pdf = pyfpdf.FPDF()
pdf.add_page();
pdf.set_font('Arial','B',16);
for linea in open("simple-csv-invoice.txt").readlines():
   args = eval(linea)
   print linea
   pdf.text(x=args[0],y=args[1],txt=str(args[2]).decode('latin1'));

pdf.output(r"c:\factura.pdf","F")
os.system(r"c:\factura.pdf")

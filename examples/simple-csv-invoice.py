# -*- coding: iso-8859-1 -*-
import sys,os
sys.path.append("..")
import pyfpdf

customer = {'name':'John Doe','tax_id':'00-0000000-0','vat':True}
items = [
    {'qty':12,'description':'Eggs','price':1.00},
    {'qty':20,'description':'Spam','price':3.00},
    {'qty':1,'description':'Varios','price':0.50},
]

pdf = pyfpdf.FPDF()
pdf.add_page();
pdf.set_font('Arial','B',16);
for line in open("simple-csv-invoice.txt").readlines():
   print line
   args = eval(line.strip())
   pdf.text(x=args[0],y=args[1],txt=str(args[2]).decode('latin1'));

pdf.output(r"./invoice.pdf","F")
import sys
if sys.platform.startswith("linux"):
    os.system("evince ./invoice.pdf")
else:
    os.system("./invoice.pdf")

# -*- coding: iso-8859-1 -*-
from __future__ import with_statement

import sys, os
sys.path.append("..")
import fpdf

customer = {'name':'John Doe','tax_id':'00-0000000-0','vat':True}
items = [
    {'qty':12,'description':'Eggs','price':1.00},
    {'qty':20,'description':'Spam','price':3.00},
    {'qty':1,'description':'Varios','price':0.50},
]

pdf = fpdf.FPDF()
pdf.add_page();
pdf.set_font('Arial','B',16);
with open("simple-csv-invoice.txt") as file:
   for line in file.readlines():
      sys.stdout.write(line)
      args = eval(line.strip())
      pdf.text(x=args[0],y=args[1],txt=str(args[2]));

pdf.output(r"./invoice.pdf","F")
import sys
if sys.platform.startswith("linux"):
    os.system("xdg-open ./invoice.pdf")
else:
    os.system("./invoice.pdf")

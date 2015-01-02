# -*- coding: utf-8 -*-

"PDF Template Helper for FPDF.py"

__author__ = "Mariano Reingart <reingart@gmail.com>"
__copyright__ = "Copyright (C) 2010 Mariano Reingart"
__license__ = "LGPL 3.0"

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=invoice.pdf
#PyFPDF-cover-test:hash=5844bbebe3e33b0ac9cc15ac39327a81
#PyFPDF-cover-test:res=invoice.csv

import common
from fpdf import Template

import os

class randomfake:
    RINT1_10 = [8, 5, 7, 9, 10, 8, 1, 9, 1, 7, 6, 2, 3, 7, 8, 4, 6, 5, 7, 2, \
        5, 8, 6, 5, 5, 8, 7, 7, 6]
    RINT65_90 = [67, 67, 87, 78, 84, 67, 86, 75, 86, 89, 81, 69, 72, 71, 84, \
        80, 71 , 86 , 82 , 70 , 84 , 69 , 70]
    RFLT = [0.820710198665, 0.342854771472, 0.0238515965298, 0.177658111957, \
        0.422301628067, 0.701867781693, 0.168650983171, 0.329723498664, \
        0.490481106182, 0.892634029991, 0.994758791625, 0.998243714035, \
        0.596244312914 ,0.318601111178 ,0.321593673214 ,0.203486335469]
    def __init__(self):
        self.icnt1_10 = 0
        self.icnt65_90 = 0
        self.fcnt = 0

    def randint(self, beg, end):
        if beg == 1 and end == 10:
            self.icnt1_10 += 1
            if self.icnt1_10 > len(self.RINT1_10):
                self.icnt1_10 = 1
            return self.RINT1_10[self.icnt1_10 - 1]
        if beg == 65 and end == 90:
            self.icnt65_90 += 1
            if self.icnt65_90 > len(self.RINT65_90):
                self.icnt65_90 = 1
            return self.RINT65_90[self.icnt65_90 - 1]
        raise Exception("Not implemented")

    def random(self):
        self.fcnt += 1
        if self.fcnt > len(self.RFLT):
            self.fcnt = 1
        return self.RFLT[self.fcnt - 1]

@common.add_unittest
def dotest(outputname, nostamp):

    # generate sample invoice (according Argentina's regulations)   
    from decimal import Decimal

    f = Template(format="A4",
             title="Sample Invoice", author="Sample Company",
             subject="Sample Customer", keywords="Electronic TAX Invoice")
    if nostamp:
        f.pdf._putinfo = lambda: common.test_putinfo(f.pdf)
        random = randomfake()
    else:
        import random

    csvpath = os.path.join(common.basepath, "invoice.csv")
    f.parse_csv(infile=csvpath, delimiter=";", decimal_sep=",")
    
    detail = "Lorem ipsum dolor sit amet, consectetur. " * 30
    items = []
    for i in range(1, 30):
        ds = "Sample product %s" % i
        qty = random.randint(1,10)
        price = round(random.random()*100,3)
        code = "%s%s%02d" % (chr(random.randint(65,90)), chr(random.randint(65,90)),i)
        items.append(dict(code=code, unit='u',
                          qty=qty, price=price, 
                          amount=qty*price,
                          ds="%s: %s" % (i,ds)))

    # divide and count lines
    lines = 0
    li_items = []
    for it in items:
        qty = it['qty']
        code = it['code']
        unit = it['unit']
        for ds in f.split_multicell(it['ds'], 'item_description01'):
            # add item description line (without price nor amount)
            li_items.append(dict(code=code, ds=ds, qty=qty, unit=unit, price=None, amount=None))
            # clean qty and code (show only at first)
            unit = qty = code = None
        # set last item line price and amount
        li_items[-1].update(amount = it['amount'],
                            price = it['price'])

    obs="\n<U>Detail:</U>\n\n" + detail
    for ds in f.split_multicell(obs, 'item_description01'):
        li_items.append(dict(code=code, ds=ds, qty=qty, unit=unit, price=None, amount=None))

    # calculate pages:
    lines = len(li_items)
    max_lines_per_page = 24
    pages = lines // (max_lines_per_page - 1)
    if lines % (max_lines_per_page - 1): pages = pages + 1

    # completo campos y hojas
    for page in range(1, int(pages)+1):
        f.add_page()
        f['page'] = 'Page %s of %s' % (page, pages)
        if pages>1 and page<pages:
            s = 'Continues on page %s' % (page+1)
        else:
            s = ''
        f['item_description%02d' % (max_lines_per_page+1)] = s

        f["company_name"] = "Sample Company"
        f["company_logo"] = os.path.join(common.basepath, "../tutorial/logo.png")
        f["company_header1"] = "Some Address - somewhere -"
        f["company_header2"] = "http://www.example.com"        
        f["company_footer1"] = "Tax Code ..."
        f["company_footer2"] = "Tax/VAT ID ..."
        f['number'] = '0001-00001234'
        f['issue_date'] = '2010-09-10'
        f['due_date'] = '2099-09-10'
        f['customer_name'] = "Sample Client"
        f['customer_address'] = "Siempreviva 1234"
       
        # print line item...
        li = 0 
        k = 0
        total = Decimal("0.00")
        for it in li_items:
            k = k + 1
            if k > page * (max_lines_per_page - 1):
                break
            if it['amount']:
                total += Decimal("%.6f" % it['amount'])
            if k > (page - 1) * (max_lines_per_page - 1):
                li += 1
                if it['qty'] is not None:
                    f['item_quantity%02d' % li] = it['qty']
                if it['code'] is not None:
                    f['item_code%02d' % li] = it['code']
                if it['unit'] is not None:
                    f['item_unit%02d' % li] = it['unit']
                f['item_description%02d' % li] = it['ds']
                if it['price'] is not None:
                    f['item_price%02d' % li] = "%0.3f" % it['price']
                if it['amount'] is not None:
                    f['item_amount%02d' % li] = "%0.2f" % it['amount']

        if pages == page:
            f['net'] = "%0.2f" % (total/Decimal("1.21"))
            f['vat'] = "%0.2f" % (total*(1-1/Decimal("1.21")))
            f['total_label'] = 'Total:'
        else:
            f['total_label'] = 'SubTotal:'
        f['total'] = "%0.2f" % total
            
    f.render(outputname)

if __name__ == "__main__":
    common.testmain(__file__, dotest)


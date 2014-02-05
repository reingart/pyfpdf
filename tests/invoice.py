# -*- coding: iso-8859-1 -*-

"PDF Template Helper for FPDF.py"

__author__ = "Mariano Reingart <reingart@gmail.com>"
__copyright__ = "Copyright (C) 2010 Mariano Reingart"
__license__ = "LGPL 3.0"

import sys, os
from fpdf import Template

if __name__ == "__main__":

    # generate sample invoice (according Argentina's regulations)

    import random
    from decimal import Decimal

    f = Template(format="A4",
             title="Sample Invoice", author="Sample Company",
             subject="Sample Customer", keywords="Electronic TAX Invoice")
    f.parse_csv(infile="invoice.csv", delimiter=";", decimal_sep=",")
    
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
    pages = int(lines / (max_lines_per_page - 1))
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
        f["company_logo"] = "../tutorial/logo.png"
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
            
    f.render("./invoice.pdf")
    if sys.platform.startswith("linux"):
        os.system("evince ./invoice.pdf")
    else:
        os.startfile("./invoice.pdf")

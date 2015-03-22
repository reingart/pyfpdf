

Apologies in advance: Spanish is our main language, so there may be errors or inaccuracies with our written English.

See [Project Home](http://code.google.com/p/pyfpdf/) for an overall introduction.

# What is FPDF? #

[FPDF](http://www.fpdf.org) (and PyFPDF) is a library with low level primitives to easily generate PDF document. This is similar to ReportLab's graphics canvas, but with some methods to output "fluid" cells ("flowables" that can span multiple rows, pages, tables, columns, etc.), it has several methods ("hooks") that can be redefined, to fine-control headers, footers, etc.

Originally developed in PHP several years ago (as a free alternative to propietary C libraries), it has been ported to many programming languages, including ASP, C++, Java, Pl/SQL, Ruby, Visual Basic, and of course, Python.

For more information see: http://www.fpdf.org/en/links.php

# What this library **is not**? #

This library is not a:
  * charts or widgets library (you can import PNG or JPG images, use PIL or any other library, or draw the figures yourself, see examples)
  * "flexible page layout engine" like [Reportlab](http://www.reportlab.com/software/opensource/) PLATYPUS (but can do columns, chapters, etc., see [Tutorial](Tutorial.md))
  * XML /object definition language like [Geraldo Reports](http://www.geraldoreports.org/), Jasper Reports or similar (look at [WriteHTML](WriteHTML.md) for simple HTML reports and [Templates](Templates.md) for fill-in-the-blank documents)
  * PDF text extractor/conversor, spltiter or similar. Look at [pyPdf](http://pybrary.net/pyPdf/)

# How does this library compares to ...? #

Compared to other solutions, this library should be easier to use and adapt for
most common documents (no need to use a page layout engine, style-sheets templates, or stories...), with a full control over the generated PDF document (including advanced features and extensions)

It is smaller (a single .py file <77K) and compilation or external libraries are not required.

It includes cell and multi\_cell primitives to draw fluid document like invoices, listings/reports, and basic support for HTML rendering.

# How does the code looks like? #

Following is a example similar to the reportlab one at the book of web2py, note
the simplified import and usage:
(http://www.web2py.com/book/default/chapter/09?search=pdf#ReportLab-and-PDF)

PyFPDF:
```
from pyfpdf import FPDF

def get_me_a_pyfpdf():
    title = "This The Doc Title"
    heading = "First Paragraph"
    text = 'bla '* 10000

    pdf=FPDF()
    pdf.add_page()
    pdf.set_font('Times','B',15)
    pdf.cell(w=210,h=9,txt=title,border=0,ln=1,align='C',fill=0)
    pdf.set_font('Times','B',15)
    pdf.cell(w=0,h=6,txt=heading,border=0,ln=1,align='L',fill=0)
    pdf.set_font('Times','',12)
    pdf.multi_cell(w=0,h=5,txt=text)
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')
```

Reportlab:
```
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from uuid import uuid4
from cgi import escape
import os

def get_me_a_pdf():
    title = "This The Doc Title"
    heading = "First Paragraph"
    text = 'bla '* 10000

    styles = getSampleStyleSheet()
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    doc = SimpleDocTemplate(tmpfilename)
    story = []
    story.append(Paragraph(escape(title),styles["Title"]))
    story.append(Paragraph(escape(heading),styles["Heading2"]))
    story.append(Paragraph(escape(text),styles["Normal"]))
    story.append(Spacer(1,2*inch))
    doc.build(story)
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data
```

# Has this library any framework integration? #

Yes, if you use web2py, you can make simple HTML reports that can be viewed in a browser, or donwloaded as PDF.

Also, using web2py DAL, you can easily set up a templating engine for PDF documents.

Look at Web2Py for examples

# What is the development status of this library? #

This library has more than 4 years since the initial port from PHP. Some code is in early development stages (mainly UTF-8 support and some advanced features). The good news are than PHP versions and examples are available since long time ago, so migration and some bug-fixes are easy.

Said that, a former version is working successfully and is commercially supported since late 2008 for electronic invoices templates compliant with AFIP (Argentina IRS) normative, in several environments (linux, windows, etc.). It was originally included in [PyRece](http://code.google.com/p/pyafipws/wiki/ProjectSummary), with thousands downloads to date.

For further information see:
  * http://www.pyafipws.com.ar/
  * http://code.google.com/p/pyafipws/
  * http://groups.google.com/group/pyafipws

In contrast, WriteHTML support is not complete, so it must be considered in alpha state. Further enhancements using web2py helpers and xml parser will enable to parse more complex HTML files.

# What is the license of this library (pyfpdf)? #

Original FPDF uses a permissive license:
http://www.fpdf.org/en/FAQ.php#q1

> "FPDF is released under a permissive license: there is no usage
> restriction. You may embed it freely in your application (commercial
> or not), with or without modifications."

FPDF Version 1.6 license.txt says:
http://www.fpdf.org/es/dl.php?v=16&f=zip

> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software to use, copy, modify, distribute, sublicense, and/or sell
> copies of the software, and to permit persons to whom the software is furnished
> to do so.

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

fpdf.py is a revision of a port by Max Pat, in the original source uses the same licence:
http://www.fpdf.org/dl.php?id=94

```
# * Software: FPDF
# * Version:  1.53
# * Date:     2004-12-31
# * Author:   Olivier PLATHEY
# * License:  Freeware
# *
# * You may use and modify this software as you wish.
# * Ported to Python 2.4 by Max (maxpat78@yahoo.it) on 2006-05
```

To avoid ambiguity (and to be compatible with other free software, open source licenses), LGPL was chosen for this googlecode project (as Freeware isn't listed).
Other FPDF ports had chosen similar licences (wxWindows Licence for C++ port, MIT licence for java port, etc.):
http://www.fpdf.org/en/links.php
Other FPDF derivatives also choose LGPL, as [sFPDF](http://www.fpdf.org/en/script/script91.php) by [Ian Back](mailto:ian@bpm1.com?subject=sFPDF)
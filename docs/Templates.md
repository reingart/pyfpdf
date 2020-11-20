# Introduction #

Templates are predefined documents (like invoices, tax forms, etc.), where each element (text, lines, barcodes, etc.) has a fixed position (x1, y1, x2, y2), style (font, size, etc.) and a default text.

This elements can act as placeholders, so the program can change the default text "filling" the document.

Also, the elements can be defined in a CSV file or in a database, so the user can easily adapt the form to his printing needs.

A template is used like a dict, setting its items' values.

# Details - Template definition #

A template is composed of a header and a list of elements.

The header contains the page format, title of the document and other metadata.

Elements have the following properties (columns in a CSV, fields in a database):

  * name: placeholder identification
  * type: 'T': texts, 'L': lines, 'I': images, 'B': boxes, 'BC': barcodes (Interleaved
    2 of 5) - alias for BCI25, 'BCI25': barcodes (Interleaved 2 of 5), 'BCC39': barcodes
    (C39),
  * x1, y1, x2, y2: top-left, bottom-right coordinates (in mm)
  * font: e.g. "Arial"
  * size: text size in points, e.g. 10
  * bold, italic, underline: text style (non-empty to enable)
  * foreground, background: text and fill colors, e.g. 0xFFFFFF
  * align: text alignment, 'L': left, 'R': right, 'C': center
  * text: default string, can be replaced at runtime
  * priority: Z-order
  * multiline: None for single line (default), True to for multicells (multiple lines), False trims to exactly fit the space defined

# How to create a template #

A template can be created in 3 ways:

  * By defining everything manually in a hardcoded way
  * By using a template definition in a CSV document and parsing the CSV with Template.parse\_dict()
  * By defining the template in a database (this applies to [Web2Py](Web2Py.md) integration)


Note the following, the definition of a template will contain the elements. The header will be given during instantiation (except for the database method).

# Example - Hardcoded #

```python

from fpdf import Template

#this will define the ELEMENTS that will compose the template.
elements = [
    { 'name': 'company_logo', 'type': 'I', 'x1': 20.0, 'y1': 17.0, 'x2': 78.0, 'y2': 30.0, 'font': None, 'size': 0.0, 'bold': 0, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': 'logo', 'priority': 2, },
    { 'name': 'company_name', 'type': 'T', 'x1': 17.0, 'y1': 32.5, 'x2': 115.0, 'y2': 37.5, 'font': 'Arial', 'size': 12.0, 'bold': 1, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': '', 'priority': 2, },
    { 'name': 'box', 'type': 'B', 'x1': 15.0, 'y1': 15.0, 'x2': 185.0, 'y2': 260.0, 'font': 'Arial', 'size': 0.0, 'bold': 0, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': None, 'priority': 0, },
    { 'name': 'box_x', 'type': 'B', 'x1': 95.0, 'y1': 15.0, 'x2': 105.0, 'y2': 25.0, 'font': 'Arial', 'size': 0.0, 'bold': 1, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': None, 'priority': 2, },
    { 'name': 'line1', 'type': 'L', 'x1': 100.0, 'y1': 25.0, 'x2': 100.0, 'y2': 57.0, 'font': 'Arial', 'size': 0, 'bold': 0, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': None, 'priority': 3, },
    { 'name': 'barcode', 'type': 'BC', 'x1': 20.0, 'y1': 246.5, 'x2': 140.0, 'y2': 254.0, 'font': 'Interleaved 2of5 NT', 'size': 0.75, 'bold': 0, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': '200000000001000159053338016581200810081', 'priority': 3, },
]

#here we instantiate the template and define the HEADER
f = Template(format="A4", elements=elements,
             title="Sample Invoice")
f.add_page()

#we FILL some of the fields of the template with the information we want
#note we access the elements treating the template instance as a "dict"
f["company_name"] = "Sample Company"
f["company_logo"] = "pyfpdf/tutorial/logo.png"

#and now we render the page
f.render("./template.pdf")

```

See template.py or [Web2Py](Web2Py.md) for a complete example.

# Example - Elements defined in CSV file #
You define your elements in a CSV file "mycsvfile.csv"
that will look like:
```
line0;T;20.0;13.0;190.0;13.0;times;10.0;0;0;0;0;65535;C;;0
line1;T;20.0;67.0;190.0;67.0;times;10.0;0;0;0;0;65535;C;;0
name0;T;21;14;104;25;times;16.0;0;0;0;0;0;C;;2
title0;T;64;26;104;30;times;10.0;0;0;0;0;0;C;;2
```

Remember that each line represents an element and each field represents one of the properties of the element in the following order:
('name','type','x1','y1','x2','y2','font','size','bold','italic','underline','foreground','background','align','text','priority', 'multiline')

Then you can use the file like this:

```python
def test_template():
    f = Template(format="A4",
                 title="Sample Invoice")
    f.parse_csv("mycsvfile.csv")
    f.add_page()
    f["company_name"] = "Sample Company"
    response.headers['Content-Type'] = 'application/pdf'
    return f.render("./template.pdf", dest='S')

```

# Designer - GUI tool to design templates #

This library includes a program `designer.py` to visually modify the designs of a template (e.g., an invoice, report, etc.).

Input files are CSV spreadsheets describing the design (see above).
Once opened, the designer displays the template with the elements as how they will be located.

The toolbar has buttons for:

  * Open, save and print (preview) template
  * Add, delete and duplicate
  * Find items by name or by text
  * Find and replace (modify selected elements, mainly move x/y)

Over an element, double left click opens a dialog to edit its text and right click opens a dialog with the properties window.
You can select multiple items by holding down shift and left clicking them.
To move the elements you can use the arrow keys or drag the elements.

To run it, just go to the directory and run:
```
python designer.py
```
(you need to have wx installed).

If you are having problems making it work, change the imports on designer.py file to the following (it should be fixed in the next version):

```python
import os, sys
import wx
import wx.lib
import wx.lib.ogl as ogl
try:
    from wx.lib.wordwrap import wordwrap
except ImportError:
    wordwrap = lambda text, width, dc: text

try:
    from template import Template
except ImportError:
    # we are frozen?
    from fpdf.template import Template
```

As an example, the following screenshot shows the Visual Designer, with the sample invoice.csv file open and 'logo' element selected, editing its properties:

![http://pyfpdf.googlecode.com/files/designer.png](http://pyfpdf.googlecode.com/files/designer.png)

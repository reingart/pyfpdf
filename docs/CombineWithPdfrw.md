# Combine with pdfrw

`fpdf2` cannot **parse** existing PDF files.

However, other Python libraries can be combined with `fpdf2`
in order to add new content to existing PDF files.

This page provides several examples of using `fpdf2` with [`pdfrw`](https://github.com/pmaupin/pdfrw),
a great zero-dependency pure Python library dedicated to reading & writing PDFs,
with numerous examples and a very clean set of classes modelling the PDF internal syntax.

## Adding content onto an existing PDF page

```python
import sys
from fpdf import FPDF
from pdfrw import PageMerge, PdfReader, PdfWriter
from pdfrw.pagemerge import RectXObj

IN_FILEPATH = sys.argv[1]
OUT_FILEPATH = sys.argv[2]
ON_PAGE_INDEX = 1
UNDERNEATH = False  # if True, new content will be placed underneath page (painted first)

reader = PdfReader(IN_FILEPATH)
area = RectXObj(reader.pages[0])

def new_content():
    fpdf = FPDF(format=(area.w, area.h), unit="pt")
    fpdf.add_page()
    fpdf.set_font("helvetica", size=36)
    fpdf.text(50, 50, "Hello!")
    reader = PdfReader(fdata=bytes(fpdf.output()))
    return reader.pages[0]

writer = PdfWriter()
writer.pagearray = reader.Root.Pages.Kids
PageMerge(writer.pagearray[ON_PAGE_INDEX]).add(new_content(), prepend=UNDERNEATH).render()
writer.write(OUT_FILEPATH)
```

## Adding a page to an existing PDF

```python
import sys
from fpdf import FPDF
from pdfrw import PdfReader, PdfWriter
from pdfrw.pagemerge import RectXObj

IN_FILEPATH = sys.argv[1]
OUT_FILEPATH = sys.argv[2]
NEW_PAGE_INDEX = 1  # set to None to append at the end

reader = PdfReader(IN_FILEPATH)
area = RectXObj(reader.pages[0])

def new_page():
    fpdf = FPDF(format=(area.w, area.h), unit="pt")
    fpdf.add_page()
    fpdf.set_font("helvetica", size=36)
    fpdf.text(50, 50, "Hello!")
    reader = PdfReader(fdata=bytes(fpdf.output()))
    return reader.pages[0]

writer = PdfWriter(trailer=PdfReader(IN_FILEPATH))
writer.addpage(new_page(), at_index=NEW_PAGE_INDEX)
writer.write(OUT_FILEPATH)
```

This example relies on [pdfrw _Pull Request_ #216](https://github.com/pmaupin/pdfrw/pull/216).
Until it is merged, you can install a forked version of `pdfrw` including the required patch:

    pip install git+https://github.com/PyFPDF/pdfrw.git@addpage_at_index

## Altering with pdfrw a document generated with fpdf2
A document created with `fpdf2` can the be edited with `pdfrw`
by passing its `.output()` to a `pdfrw.PdfReader`:
```python
import io
from fpdf import FPDF
from pdfrw import PdfReader

pdf = FPDF()
pdf.add_page()
pdf.set_font('times', 'B', 19)
pdf.text(50, 10, 'Hello World!')

reader = PdfReader(io.BytesIO(pdf.output()))
```

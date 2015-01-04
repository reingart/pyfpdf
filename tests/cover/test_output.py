"Test the various PDF output modes"

from __future__ import with_statement

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=output.pdf
#PyFPDF-cover-test:hash=3996992652a230c26ffe8b5b7525aeb3

import common
from fpdf import FPDF

import sys

try:  # Python >= 2.6
    bytes
except NameError:  # Python 2.5
    bytes = str

@common.add_unittest
def dotest(outputname, nostamp=True):
    pdf = FPDF(unit="pt")
    pdf._putinfo = lambda: common.test_putinfo(pdf)
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.cell(0, 12, "Dummy content")
    
    # Get the PDF data the usual way via a real file
    pdf.output(outputname)
    with open(outputname, "rb") as file:
        data = file.read(1000)
        assert len(data) == 966, "Unexpected PDF file size"
    
    try:  # Python < 3 (Python 2.5 does not have the "io" module)
        from cStringIO import StringIO
        capture = StringIO()
        detach = lambda: capture
    except ImportError:  # Python >= 3.1
        from io import TextIOWrapper, BytesIO
        # Ensure that no text encoding is actually done
        capture = TextIOWrapper(BytesIO(), "undefined")
        detach = lambda: capture.detach()
    
    # Compare data when output() writes to stdout
    original_stdout = sys.stdout
    try:
        sys.stdout = capture
        pdf.output()
        capture = detach()
    finally:
        sys.stdout = original_stdout
    assert capture.getvalue() == data, "Unexpected stdout data"
    
    # Compare data when output() returns a byte string
    returned = pdf.output(dest="S")
    assert isinstance(returned, bytes), "output() should return bytes"
    assert returned == data, "Unexpected PDF data returned"

if __name__ == "__main__":
    common.testmain(__file__, dotest)

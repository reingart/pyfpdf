"""issue65_test.py"""

import unittest
import sys
import os
sys.path.insert(0,
  os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.path.join('..', '..')
  )
)

import fpdf
import test
from test.utilities import relative_path_to, \
                           set_doc_date_0, \
                           calculate_hash_of_file

def next_row(pdf):
  pdf.ln()
  pdf.set_y(pdf.get_y() + size + margin)

size = 50
margin = 10

class EllipseTest(unittest.TestCase):
  """ShapeWriterTest"""
  PDFClass = fpdf.FPDF
  def test_ellipse_style(self):
    pdf = self.PDFClass(unit = 'mm')
    set_doc_date_0(pdf)
    pdf.add_page()

    # Styles
    counter = 0
    for style in ['', 'F', 'FD', 'DF', None]:
      counter += 1
      pdf.ellipse(x=pdf.get_x(), y=pdf.get_y(), w=size, h=size, style = style)
      pdf.set_x(pdf.get_x() + size + margin)
      
      if counter % 3 == 0:
        next_row(pdf)

    outfile = relative_path_to("output1.pdf")
    pdf.output(outfile)
    
    known_good_hash = "2f08ed8338d7d421fe2a286ef6c00daf"
    self.assertEqual(known_good_hash, calculate_hash_of_file(outfile))
    os.unlink(outfile)

  def test_ellipse_line_width(self):
    pdf = self.PDFClass(unit = 'mm')
    set_doc_date_0(pdf)
    pdf.add_page()

    # Line Width
    for line_width in [1, 2, 3]:
      pdf.set_line_width(line_width)
      pdf.ellipse(x=pdf.get_x(), y=pdf.get_y(), w=size, h=size, style = None)
      pdf.set_x(pdf.get_x() + size + margin)
    next_row(pdf)
    for line_width in [4, 5, 6]:
      pdf.set_line_width(line_width)
      pdf.ellipse(x=pdf.get_x(), y=pdf.get_y(), w=size, h=size, style = None)
      pdf.set_x(pdf.get_x() + size + margin)
    pdf.set_line_width(.2)  # reset

    outfile = relative_path_to("output2.pdf")
    pdf.output(outfile)
    
    known_good_hash = "9151e507484e32ca1577c6002ccafada"
    self.assertEqual(known_good_hash, calculate_hash_of_file(outfile))
    os.unlink(outfile)

  def test_ellipse_draw_color(self):
    pdf = self.PDFClass(unit = 'mm')
    set_doc_date_0(pdf)
    pdf.add_page()

    # Colors
    pdf.set_line_width(.5)
    for gray in [70, 140, 210]:
      pdf.set_draw_color(gray)
      pdf.ellipse(x=pdf.get_x(), y=pdf.get_y(), w=size, h=size, style = None)
      pdf.set_x(pdf.get_x() + size + margin)

    outfile = relative_path_to("output3.pdf")
    pdf.output(outfile)
    
    known_good_hash = "ad08d121648ee2b6e38982cdcce01688"
    self.assertEqual(known_good_hash, calculate_hash_of_file(outfile))
    os.unlink(outfile)

  def test_ellipse_fill_color(self):
    pdf = self.PDFClass(unit = 'mm')
    set_doc_date_0(pdf)
    pdf.add_page()

    pdf.set_fill_color(240)
    for color in [[230, 30, 180], [30, 180, 30], [30, 30, 70]]:
      pdf.set_draw_color(*color)
      pdf.ellipse(x=pdf.get_x(), y=pdf.get_y(), w=size, h=size, style = 'FD')
      pdf.set_x(pdf.get_x() + size + margin)

    next_row(pdf)

    outfile = relative_path_to("output4.pdf")
    pdf.output(outfile)
    
    known_good_hash = "2719bf0278757bb684d5d8e6e9cea5f5"
    self.assertEqual(known_good_hash, calculate_hash_of_file(outfile))
    os.unlink(outfile)
    

if __name__ == '__main__':
  unittest.main()

## Development of demo mostly done as written above.

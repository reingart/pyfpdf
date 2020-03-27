import fpdf
import os
import unittest
from fpdf.html import px2mm
from test.utilities import calculate_hash_of_file, set_doc_date_0

class MyFPDF(fpdf.FPDF, fpdf.HTMLMixin):
  pass


class HTMLTest(unittest.TestCase):
  """This test executes some possible inputs to FPDF#HTMLMixin."""
  def test_html_images(self):
    pdf = MyFPDF()
    set_doc_date_0(pdf)
    pdf.add_page()
    rel = os.path.dirname(os.path.abspath(__file__))
    img_path = rel + "/image/png_images/c636287a4d7cb1a36362f7f236564cef.png"

    initial = 10
    mm_after_image = initial + px2mm(300)
    self.assertEqual(round(pdf.get_x()), 10, 'Initial x margin is not expected')
    self.assertEqual(round(pdf.get_y()), 10, 'Initial y margin is not expected')
    self.assertEqual(round(pdf.w), 210, 'Page width is not expected')
    pdf.write_html("<center><img src=\"%s\" height='300' width='300'></center>" % img_path)
    # Unable to text position of the image as write html moves to a new line after
    # adding the image but it can be seen in the produce test.pdf file.
    self.assertEqual(round(pdf.get_x()), 10, 'Have not moved to beginning of new line')
    self.assertAlmostEqual(pdf.get_y(), mm_after_image, places=2, msg='Image height has moved down the page')
    pdf.output('test/test.pdf', "F")

    # comment to see view output after test
    known_good_hash = "663ecbb2c23d55d4589629039d394911"
    self.assertEqual(calculate_hash_of_file('test/test.pdf'), known_good_hash)
    os.unlink('test/test.pdf')

if __name__ == '__main__':
  unittest.main()

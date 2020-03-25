import fpdf
import os
import unittest


class MyFPDF(fpdf.FPDF, fpdf.HTMLMixin):
  pass


class HTMLTest(unittest.TestCase):
  """This test executes some possible inputs to FPDF#HTMLMixin."""
  def test_html_images(self):
    pdf = MyFPDF()
    pdf.add_page()
    img_path = f"{os.path.dirname(os.path.abspath(__file__))}/image/png_images/c636287a4d7cb1a36362f7f236564cef.png"
    self.assertEqual(round(pdf.get_x()), 10, 'Initial x margin is not expected')
    self.assertEqual(round(pdf.get_y()), 10, 'Initial y margin is not expected')
    self.assertEqual(round(pdf.w), 210, 'Page width is not expected')
    pdf.write_html(f"<center><img src={img_path} height='300' width='300'></center>")
    # Unable to text position of the image as write html moves to a new line after
    # adding the image but it can be seen in the produce test.pdf file.
    self.assertEqual(round(pdf.get_x()), 10, 'Have not moved to beginning of new line')
    self.assertEqual(round(pdf.get_y()), 116, 'Image height has moved down the page')
    pdf.output('test/test.pdf', "F")


if __name__ == '__main__':
  unittest.main()

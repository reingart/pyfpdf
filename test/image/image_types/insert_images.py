"""insert_images.py"""

import unittest
import sys
import os
sys.path.insert(0,
  os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.path.join('..', '..', '..')
  )
)

import fpdf
import test
from test.utilities import relative_path_to, \
                           compare_files_ignoring_CreationDate

class InsertImagesTest(unittest.TestCase):
  def test_insert_jpg(self):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    imagename = relative_path_to('insert_images_insert_jpg.jpg')
    pdf.image(imagename, x = 15, y = 15, h = 140)

    good = relative_path_to('insert_images_jpg_good.pdf')
    test = relative_path_to('insert_images_jpg_test.pdf')

    pdf.output(test, 'F')

    compare_files_ignoring_CreationDate(test, good, self.assertEqual)
    os.unlink(test)

  def test_insert_png(self):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    imagename = relative_path_to('insert_images_insert_png.png')
    pdf.image(imagename, x = 15, y = 15, h = 140)

    good = relative_path_to('insert_images_png_good.pdf')
    test = relative_path_to('insert_images_png_test.pdf')

    pdf.output(test, 'F')

    compare_files_ignoring_CreationDate(test, good, self.assertEqual)
    os.unlink(test)

if __name__ == '__main__':
  unittest.main()

## Code used to create test:
# doc = fpdf.FPDF()
# doc.compress = False
# doc.add_page()
# imagename = 'insert_images_insert_jpg.jpg'
# doc.image(imagename, x = 15, y = 15, h = 140) #, w = 30, h = 25)
# doc.output('insert_images_jpg_good.pdf')

# doc = fpdf.FPDF()
# doc.compress = False
# doc.add_page()
# imagename = 'insert_images_insert_png.png'
# doc.image(imagename, x = 15, y = 15, h = 140) #, w = 30, h = 25)
# doc.output('insert_images_png_good.pdf')

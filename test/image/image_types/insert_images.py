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
                           set_doc_date_0, \
                           calculate_hash_of_file

class InsertImagesTest(unittest.TestCase):
  def test_insert_jpg(self):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    imagename = relative_path_to('insert_images_insert_jpg.jpg')
    pdf.image(imagename, x = 15, y = 15, h = 140)

    set_doc_date_0(pdf)
    test = relative_path_to('insert_images_jpg_test.pdf')
    pdf.output(test, 'F')

    test_hash = calculate_hash_of_file(test)
    self.assertEqual(test_hash, "c6997071c5e5f4191327603607d2a32c")
    os.unlink(test)

  def test_insert_png(self):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    imagename = relative_path_to('insert_images_insert_png.png')
    pdf.image(imagename, x = 15, y = 15, h = 140)

    set_doc_date_0(pdf)
    test = relative_path_to('insert_images_png_test.pdf')
    pdf.output(test, 'F')

    test_hash = calculate_hash_of_file(test)
    self.assertEqual(test_hash, "dd20cb8689d5512b31753b6ab6aa6341")
    os.unlink(test)

if __name__ == '__main__':
  unittest.main()

## Code used to create test:
# doc = fpdf.FPDF()
# doc.compress = False
# doc.add_page()
# imagename = relative_path_to('insert_images_insert_jpg.jpg')
# doc.image(imagename, x = 15, y = 15, h = 140) #, w = 30, h = 25)
# set_doc_date_0(doc)
# output_name = relative_path_to('insert_images_jpg_good.pdf')
# doc.output(output_name)
# print calculate_hash_of_file(output_name)

# doc = fpdf.FPDF()
# doc.compress = False
# doc.add_page()
# imagename = relative_path_to('insert_images_insert_png.png')
# doc.image(imagename, x = 15, y = 15, h = 140) #, w = 30, h = 25)
# set_doc_date_0(doc)
# output_name = relative_path_to('insert_images_png_good.pdf')
# doc.output(output_name)
# print calculate_hash_of_file(output_name)

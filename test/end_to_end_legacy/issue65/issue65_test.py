"""issue65_test.py"""

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


class Issue65Test(unittest.TestCase):
  def test_issue65(self):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    png = "https://g.twimg.com/Twitter_logo_blue.png"
    pdf.image(png, x = 15, y = 15, w = 30, h = 25)

    good = relative_path_to('issue65_good.pdf')
    test = relative_path_to('issue65_test.pdf')

    pdf.output(test, 'F')

    compare_files_ignoring_CreationDate(test, good, self.assertEqual)
    os.unlink(test)

if __name__ == '__main__':
  unittest.main()

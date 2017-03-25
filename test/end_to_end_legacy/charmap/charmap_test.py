"""Charmap Test Case

This module contains the test case for the Charmap Test. It prints the first
999 characters of the unicode character set with a unicode ttf font, and
verifies the result against a known good result.

This test will complain that some of the values in this font file are out of
the range of the C 'short' data type (2 bytes, 0 - 65535):
  fpdf/ttfonts.py:671: UserWarning: cmap value too big/small: 
and this seems to be okay.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                '..', '..', '..'))
import fpdf
from fpdf.ttfonts import TTFontFile

class MyTTFontFile(TTFontFile):
  """MyTTFontFile docstring

  I clearly have no idea what this does. It'd be great if this class were
  even a little bit better documented, so that it would be clearer what this
  test is testing, otherwise this test isn't clearly testing one class or the
  other.

  """
  def getCMAP4(self, unicode_cmap_offset, glyphToChar, charToGlyph):
    TTFontFile.getCMAP4(self, unicode_cmap_offset, glyphToChar, charToGlyph)
    self.saveChar = charToGlyph
      
  def getCMAP12(self, unicode_cmap_offset, glyphToChar, charToGlyph):
    TTFontFile.getCMAP12(self, unicode_cmap_offset, glyphToChar, charToGlyph)
    self.saveChar = charToGlyph

if sys.version_info >= (3, 0):
  unichr = chr

class CharmapTest(unittest.TestCase):
  def setUp(self):
    pass

  def test_first_999_chars(self):
    # fontpath = 'Roboto-Regular.ttf'
    fontpath = 'DejaVuSans.ttf'

    pdf = fpdf.FPDF()
    pdf.compression = True
    pdf.add_page()
    pdf.add_font('font', '', fontpath, uni = True)
    pdf.set_font('font', '', 10)

    ttf = MyTTFontFile()
    ttf.getMetrics(fontpath)

    for counter, character in enumerate(ttf.saveChar, 0):
      # print (counter, character)
      pdf.write(8, u"%03d) %06x - %c" % (counter, character, character))
      pdf.ln()

      if counter >= 999:
        break

    def compare_files_ignoring_CreationDate(new, known):
      """This function compares two files ignoring their /CreationDate line"""
      from itertools import ifilter
      predicate = lambda line: '/CreationDate' not in line

      with open(new, 'rt') as newfile, open(known, 'rt') as knownfile:
        newfile   = ifilter(predicate, newfile)
        knownfile = ifilter(predicate, knownfile)
        for line_new, line_known in zip(newfile, knownfile):
          self.assertEqual(line_new, line_known, "all lines equal")

    testing_output = 'charmap_test_output.pdf'
    known_output   = 'charmap_test_output_good.pdf'

    pdf.output(testing_output)
    compare_files_ignoring_CreationDate(testing_output, known_output)
    os.unlink(testing_output)

    # clear out all the pkl files
    pklList = [f for f in os.listdir(os.path.dirname(os.path.abspath(__file__)))
               if f.endswith(".pkl")]
    for f in pklList:
      os.remove(f)

if __name__ == '__main__':
  unittest.main()

import unittest

from fpdf.ttfonts import str_pad

# python -m unittest test.utils.text_utils.UtilsTest


class UtilsTest(unittest.TestCase):
    def test_str_pad(self):
        self.assertEqual(str_pad("ok", 20), "ok                  ")
        self.assertEqual(str_pad("ok", 20, "+"), "ok++++++++++++++++++")
        self.assertEqual(str_pad("ok", 20, "-", 0), "---------ok---------")
        self.assertEqual(str_pad("ok", 20, "-", 1), "ok------------------")
        self.assertEqual(str_pad("ok", 20, "-", -1), "------------------ok")

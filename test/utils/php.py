"""php.py"""

import unittest
import sys
import os
import fpdf

from six.moves import StringIO

# python -m unittest test.utils.php.PHPUtilsTest

class PHPUtilsTest(unittest.TestCase):
  def get_stdout(self, func):
    """https://stackoverflow.com/q/5136611"""
    # setup the environment
    backup = sys.stdout

    # ####
    sys.stdout = StringIO()     # capture output
    func()
    out = sys.stdout.getvalue() # release output
    # ####

    sys.stdout.close()  # close the stream 
    sys.stdout = backup # restore original stdout

    return out.strip()

  def test_print_r(self):
    p = fpdf.php.print_r
    s = self.get_stdout
    e = self.assertEqual
    e(s(lambda: p('a')), '[a] => a')
    e(s(lambda: p([1,2,3])), '[1] => 1 \n[2] => 2 \n[3] => 3')
    e(s(lambda: p([1,2,None])), '[1] => 1 \n[2] => 2 \n[None] => None')
    e(s(lambda: p([1,2,'None'])), '[1] => 1 \n[2] => 2 \n[None] => None')
    e(s(lambda: p({'a': 'maybe', 'ab': 'maybe'})), '[a] => maybe \n[ab] => maybe')
    e(s(lambda: p({'a': 'maybe', 'ab': 'None'})), '[a] => maybe \n[ab] => None')
    e(s(lambda: p({'a': 'maybe', 'ab': None})), '[a] => maybe \n[ab] => None')
    e(s(lambda: p({'a': 'maybe', 2: None})), '[2] => None \n[a] => maybe')
    e(s(lambda: p({'a': 1})), '[a] => 1')

  def test_UTF8ToUTF16BE(self):
    u = fpdf.php.UTF8ToUTF16BE
    self.assertTrue(u('abc', False) is not None)

  def test_string_functions(self):
    e = self.assertEqual

    r = fpdf.php.str_repeat
    e(r('ok', 3), 'okokok')

    p = fpdf.php.str_pad
    
    e(p('ok', 20), 'ok                  ')
    e(p('ok', 20, '+'), 'ok++++++++++++++++++')
    e(p('ok', 20, '-', 0), '---------ok---------')
    e(p('ok', 20, '-', 1), 'ok------------------')
    e(p('ok', 20, '-', -1), '------------------ok')

  def test_die(self):
    with self.assertRaises(RuntimeError) as e:
      fpdf.php.die('message')
      
    self.assertEqual(str(e.exception), 'message')

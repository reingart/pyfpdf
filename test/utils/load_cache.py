# """load_cache.py"""

import unittest
import sys
import os
import pickle
import fpdf

# # python -m unittest test.utils


import pickle


# with open('filename.pickle', 'rb') as handle:
#     b = pickle.load(handle)

# print a == b

class LoadCacheTest(unittest.TestCase):
  def test_load_cache_none(self):
    result = fpdf.fpdf.load_cache(None)
    self.assertTrue(result is None)

  @unittest.skip("built in function open behaves different python2/3")
  def test_load_cache_other_excpetion(self):
    with self.assertRaises(Exception) as e:
      fpdf.fpdf.load_cache(None)

    expected = 'coercing to Unicode: need string or buffer, int found'
    self.assertEqual(str(e.exception), expected, 'Did not pass expected exc')

  def test_load_cache_pickle(self):
    a = {'hello': 'world'}
    with open('filename.pickle', 'wb') as handle:
      pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    self.assertEqual(fpdf.fpdf.load_cache('filename.pickle'), a)
    self.assertEqual(fpdf.fpdf.load_cache('filename1.pickle'), None)

    os.unlink('filename.pickle')
    
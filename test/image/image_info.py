"""image_info.py"""

import unittest
import sys
import os
import pickle
import fpdf

from six import BytesIO
from PIL import Image 

# python -m unittest test.image.image_info.ImageParsingTest

from test.utilities import relative_path_to

class ImageParsingTest(unittest.TestCase):
  def break_down_filename(self, image):
    """
    filename:                               g04i2c08.png
                                            || ||||
    test feature (in this case gamma) ------+| ||||
    parameter of test (here gamma-value) ----+ ||||
    interlaced or non-interlaced --------------+|||
    color-type (numerical) ---------------------+||
    color-type (descriptive) --------------------+|
    bit-depth ------------------------------------|
    """
    return {
      'test_feature': image[0].lower(),
      'parameter_ot': image[1:3].lower(),
      'noninterlace': image[3].lower() != 'i',
      'colortype_nm': int(image[4], 10),
      'colortype_ds': image[5].lower(),
      'n_bits_depth': int(image[6:8], 10)
    }

  def test_get_img_info(self):
    img_dir = 'png_test_suite/'
    images = sorted(os.listdir(relative_path_to(img_dir))[:20])
    
    def isok(image):
      return image.endswith('.png') and not image.startswith('x')

    images = [image for image in images if isok(image)]
    # expln = [self.break_down_filename(name) for name in images]

    def get_contents(path):
        with open(path, 'rb') as f:
            return f.read()

    paths = [os.path.join(relative_path_to(img_dir), i) for i in images]
    blobs = [BytesIO(get_contents(path)) for path in paths]
    # modes = [Image.open(blob).mode for blob in blobs]

    infos = [fpdf.image_parsing.get_img_info(blob) for blob in blobs]

    short_keys = ['f', 'h', 'bpc', 'w', 'cs', 'trns', 'dp', 'pal']

    for info, image in zip(infos, images):
      short_info = {k: v for k, v in info.items() if k in short_keys}
      if image == 'g25n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'bgbn4a08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f03n0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 's09n3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 9, 'w': 9, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 9'})
      elif image == 'cs3n2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's40n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 40, 'w': 40, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 40'})
      elif image == 'cdhn2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 8, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'bgan6a16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cs8n3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ct1n0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cdun2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ps1n0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 's04n3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 4, 'w': 4, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 4'})
      elif image == 's33n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 33, 'w': 33, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 33'})
      elif image == 'z03n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f02n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'oi1n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's03n3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 3, 'w': 3, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 3'})
      elif image == 'oi4n2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f99n0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g07n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's32i3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tm3n3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ccwn2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tbwn3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cdfn2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 8, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 8'})
      elif image == 'ps2n2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's35n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 35, 'w': 35, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 35'})
      elif image == 's39i3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 39, 'w': 39, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 39'})
      elif image == 's05n3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 5, 'w': 5, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 5'})
      elif image == 'cdsn2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 8, 'w': 8, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 8'})
      elif image == 'tbgn3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tbrn2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f01n0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f03n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's36n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 36, 'w': 36, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 36'})
      elif image == 's06i3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 6, 'w': 6, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 6'})
      elif image == 'bgai4a16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g05n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'z00n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g04n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's01n3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 1, 'w': 1, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 1'})
      elif image == 'oi9n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tbgn2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cten0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tp0n0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'exif2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tbbn2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's36i3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 36, 'w': 36, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 36'})
      elif image == 'cs8n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ps2n0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f04n0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 's33i3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 33, 'w': 33, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 33'})
      elif image == 's35i3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 35, 'w': 35, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 35'})
      elif image == 'oi2n2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cs5n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'bggn4a16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's38i3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 38, 'w': 38, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 38'})
      elif image == 'ps1n2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cthn0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'oi1n2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ch2n3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g03n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's34i3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 34, 'w': 34, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 34'})
      elif image == 'tp0n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tp0n3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cm9n0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 's39n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 39, 'w': 39, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 39'})
      elif image == 'basi3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn0g02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'pp0n2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f01n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ctgn0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tp1n3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's05i3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 5, 'w': 5, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 5'})
      elif image == 'g10n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g03n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 's08i3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 8, 'w': 8, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 8'})
      elif image == 'basn6a08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f04n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cs3n3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tbbn0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 's02n3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 2, 'w': 2, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 2'})
      elif image == 's06n3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 6, 'w': 6, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 6'})
      elif image == 'bgwn6a08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi4a08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ctzn0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'oi2n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's03i3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 3, 'w': 3, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 3'})
      elif image == 'f00n0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ch1n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'bgai4a08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's40i3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 40, 'w': 40, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 40'})
      elif image == 'tbyn3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi0g02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f00n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's04i3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 4, 'w': 4, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 4'})
      elif image == 'basn0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'bgan6a08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's38n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 38, 'w': 38, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 38'})
      elif image == 's09i3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 9, 'w': 9, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 9'})
      elif image == 'tbwn0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g07n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn0g01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g05n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g05n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's34n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 34, 'w': 34, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 34'})
      elif image == 'basn3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi6a08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'oi9n2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn4a16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g10n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'bgyn6a16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'f02n0g08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ctjn0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'pp0n6a08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi0g01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's02i3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 2, 'w': 2, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 2'})
      elif image == 'ct0n0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 's08n3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 8, 'w': 8, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 8'})
      elif image == 'basi6a16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cm7n0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'ccwn3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'z06n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi4a16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'z09n2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's01i3p01.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 1, 'w': 1, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 1'})
      elif image == 'g25n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's07i3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 7, 'w': 7, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 7'})
      elif image == 'oi4n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g03n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g04n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g25n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basi2c08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's37i3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 37, 'w': 37, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 37'})
      elif image == 's32n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cm0n0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn2c16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's37n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 37, 'w': 37, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 37'})
      elif image == 'g07n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'cs5n3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'tbbn3p08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn4a08.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g10n0g16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 'basn6a16.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})
      elif image == 's07n3p02.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 7, 'w': 7, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 7'})
      elif image == 'ctfn0g04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceGray', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 32'})
      elif image == 'g04n3p04.png':
        self.assertEqual(short_info, {'bpc': 8, 'f': 'FlateDecode', 'h': 32, 'w': 32, 'cs': 'DeviceRGB', 'trns': '', 'pal': '', 'dp': '/Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns 32'})

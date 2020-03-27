# -*- coding: utf-8 -*-

import re
import struct
import zlib
from six import BytesIO

import numpy
from PIL import Image

from .errors import fpdf_error
from .php import substr
from .py3k import PY3K, b
from .util import freadint as read_integer
from six.moves.urllib.request import urlopen

def load_resource(filename, reason = "image"):
    """Load external file"""
    # if a bytesio instance is passed in, use it as is.
    if isinstance(filename, BytesIO):
       return filename
    # by default loading from network is allowed for all images
    if reason == "image":
        if filename.startswith("http://") or \
           filename.startswith("https://"):
            f = BytesIO(urlopen(filename).read())
        else:
            fl = open(filename, "rb")
            f = BytesIO(fl.read())
            fl.close()
        return f
    else:
        fpdf_error("Unknown resource loading reason \"%s\"" % reason)

def get_img_info(file_):
    img = Image.open(file_)
    if img.mode not in ['L', 'LA', 'RGBA']:
        img = img.convert('RGBA')
    w, h = img.size
    info = {
        'w': w,
        'h': h,
    }
    pal=''
    trns=''
    if img.mode == 'L':
        dpn = 1
        bpc = 8
        colspace = 'DeviceGray'
        data = numpy.asarray(img)
        z_data = numpy.insert(data, 0, 0, axis=1)
        info['data']= zlib.compress(z_data)
    elif img.mode == 'LA':
        dpn = 1
        bpc = 8
        colspace = 'DeviceGray'

        rgba_data = numpy.reshape(numpy.asarray(img), w * h * 2)
        a_data = numpy.ascontiguousarray(rgba_data[1::2])
        rgb_data = numpy.ascontiguousarray(rgba_data[0::2])

        a_data = numpy.reshape(a_data, (h, w))
        rgb_data = numpy.reshape(rgb_data, (h, w))

        za_data = numpy.insert(a_data.reshape((h, w)), 0, 0, axis=1)
        zrgb_data = numpy.insert(rgb_data.reshape((h, w)), 0, 0, axis=1)
        info['data']= zlib.compress(zrgb_data)
        info['smask'] = zlib.compress(za_data)

    # This will never happen, others get converted to RGBA
    # elif img.mode == 'RGBA':
    else:
        dpn = 3
        bpc = 8
        colspace = 'DeviceRGB'

        rgba_data = numpy.reshape(numpy.asarray(img), w * h * 4)
        a_data = numpy.ascontiguousarray(rgba_data[3::4])
        rgb_data = numpy.delete(rgba_data, numpy.arange(3, len(rgba_data), 4))

        a_data = numpy.reshape(a_data, (h, w))
        rgb_data = numpy.reshape(rgb_data, (h, w * 3))


        za_data = numpy.insert(a_data.reshape((h, w)), 0, 0, axis=1)
        zrgb_data = numpy.insert(rgb_data.reshape((h, w*3)), 0, 0, axis=1)
        info['data']= zlib.compress(zrgb_data)
        info['smask'] = zlib.compress(za_data)

    # This will never happen, others get converted to RGBA
    # else:
    #     self.error('Unsupport image: {}'.format(img.mode))

    dp='/Predictor 15 /Colors ' + str(dpn) + ' /BitsPerComponent '+str(bpc)+' /Columns '+str(w)+''

    info.update({
        'cs':colspace,
        'bpc':bpc,
        'f':'FlateDecode',
        'dp':dp,
        'pal':pal,
        'trns':trns,
    })

    return info

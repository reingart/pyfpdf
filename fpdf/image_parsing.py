# -*- coding: utf-8 -*-

import re
import struct
import zlib

from .errors import fpdf_error
from .php import substr
from .py3k import PY3K, b
from .util import freadint as read_integer

def load_resource(filename, reason = "image"):
    "Load external file"
    # by default loading from network is allowed for all images

    if reason == "image":
        if filename.startswith("http://") or \
           filename.startswith("https://"):
            f = BytesIO(urlopen(filename).read())
        else:
            f = open(filename, "rb")
        return f
    else:
        fpdf_error("Unknown resource loading reason \"%s\"" % reason)

def marker_in_range(ival, marker):
    """returns if the JPEG marker is in a given range"""
    return marker >= ival[0] and marker <= ival[1]

def get_jpg_info(file_):
    """Parse JPG File to Information Dict"""

    file_.seek(0)

    while True:
        markerHigh, markerLow = struct.unpack('BB', file_.read(2))
        ml = markerLow

        if markerHigh != 0xFF or markerLow < 0xC0:
            raise SyntaxError('No JPEG marker found')
        elif markerLow == 0xDA:  # SOS
            raise SyntaxError('No JPEG SOF marker found')
        elif (markerLow == 0xC8 or              # JPG
              marker_in_range((0xD0, 0xD9), ml) or  # RSTx
              marker_in_range((0xF0, 0xFD), ml)):   # JPGx
            pass
        else:
            dataSize, = struct.unpack('>H', file_.read(2))
            data = file_.read(dataSize - 2) if dataSize > 2 else ''

            if ((marker_in_range((0xC0, 0xC3), ml) or  # SOF0 - SOF3
                 marker_in_range((0xC5, 0xC7), ml) or  # SOF4 - SOF7
                 marker_in_range((0xC9, 0xCB), ml) or  # SOF9 - SOF11
                 marker_in_range((0xCD, 0xCF), ml))):  # SOF13 - SOF15
                bpc, height, width, layers = \
                    struct.unpack_from('>BHHB', data)

                colspace = {
                    3: 'DeviceRGB',
                    4: 'DeviceCMYK',
                }.get(layers, 'DeviceGray')
                break

    file_.seek(0)
    data = file_.read()
    info = {
        'w'  : width,       'h'    : height,
        'cs' : colspace,    'bpc'  : bpc,
        'f'  : 'DCTDecode', 'data' : data
    }
    return info

def get_png_info(file_):    
    """Parse PNG File to Information Dict"""

    # Check signature
    magic = file_.read(8).decode("latin1")
    signature = '\x89' + 'PNG' + '\r' + '\n' + '\x1a' + '\n'
    if not PY3K:
        signature = signature.decode("latin1")
    if (magic != signature):
        fpdf_error('Not a PNG file: ' + filename)

    # Read header chunk
    file_.read(4)
    chunk = file_.read(4).decode("latin1")
    if (chunk != 'IHDR'):
        fpdf_error('Incorrect PNG file: ' + filename)
    w = read_integer(file_)
    h = read_integer(file_)
    bpc = ord(file_.read(1))
    if (bpc > 8):
        fpdf_error('16-bit depth not supported: ' + filename)
    ct = ord(file_.read(1))
    if (ct == 0 or ct == 4):
        colspace = 'DeviceGray'
    elif (ct == 2 or ct == 6):
        colspace = 'DeviceRGB'
    elif (ct == 3):
        colspace = 'Indexed'
    else:
        fpdf_error('Unknown color type: ' + filename)

    if (ord(file_.read(1)) != 0):
        fpdf_error('Unknown compression method: ' + filename)
    if (ord(file_.read(1)) != 0):
        fpdf_error('Unknown filter method: '     + filename)
    if (ord(file_.read(1)) != 0):
        fpdf_error('Interlacing not supported: ' + filename)
    file_.read(4)

    dp = '/Predictor 15 /Colors '
    dp += '3' if colspace == 'DeviceRGB' else '1'
    dp += ' /BitsPerComponent ' + str(bpc) + ' /Columns ' + str(w) + ''

    # Scan chunks looking for palette, transparency and image data
    pal  = ''
    trns = ''
    data = bytes() if PY3K else str()
    n    = 1
    while n is not None:
        n       = read_integer(file_)

        my_type = file_.read(4).decode("latin1")
        if (my_type == 'PLTE'):
            # Read palette
            pal = file_.read(n)
            file_.read(4)

        elif (my_type == 'tRNS'):
            # Read transparency info
            t = file_.read(n)
            if (ct == 0):
                trns = [ord(substr(t, 1, 1))]
            elif (ct == 2):
                trns = [
                    ord(substr(t, 1, 1)),
                    ord(substr(t, 3, 1)),
                    ord(substr(t, 5, 1))
                ]
            else:
                pos = t.find('\x00'.encode("latin1"))
                if (pos != -1):
                    trns = [pos, ]
            file_.read(4)

        elif (my_type == 'IDAT'):
            # Read image data block
            data += file_.read(n)
            file_.read(4)

        elif (my_type == 'IEND'):
            break

        # bug fix @4306eaf24e81596af29117cf3d606242a5edfb89
        # shoutout to https://github.com/klaplong
        # read_integer returns None if struct#unpack errors out
        elif n is not None:
            file_.read(n + 4)

    if (colspace == 'Indexed' and not pal):
        fpdf_error('Missing palette in ' + filename)

    file_.close()

    info = {
        'w'  : w,             'h'   : h,
        'cs' : colspace,      'bpc' : bpc,
        'f'  : 'FlateDecode', 'dp'  : dp,
        'pal': pal,           'trns': trns
    }
    if (ct >= 4):  # if ct == 4, or == 6
        # Extract alpha channel
        make_re = lambda regex: re.compile(regex, flags = re.DOTALL)

        data  = zlib.decompress(data)
        color = b('')
        alpha = b('')
        if (ct == 4):
            # Gray image
            length = 2 * w
            for i in range(h):
                pos    = (1 + length) * i
                color += b(data[pos])
                alpha += b(data[pos])
                line   = substr(data, pos + 1, length)
                re_c   = make_re('(.).'.encode("ascii"))
                re_a   = make_re('.(.)'.encode("ascii"))
                color += re_c.sub(lambda m: m.group(1), line)
                alpha += re_a.sub(lambda m: m.group(1), line)
        else:
            # RGB image
            length = 4 * w
            for i in range(h):
                pos    = (1 + length) * i
                color += b(data[pos])
                alpha += b(data[pos])
                line   = substr(data, pos + 1, length)
                re_c   = make_re('(...).'.encode("ascii"))
                re_a   = make_re('...(.)'.encode("ascii"))
                color += re_c.sub(lambda m: m.group(1), line)
                alpha += re_a.sub(lambda m: m.group(1), line)
        del data
        data = zlib.compress(color)
        info['smask'] = zlib.compress(alpha)

    info['data'] = data
    return info

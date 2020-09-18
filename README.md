[![Pull Requests Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)
[![build status](https://github.com/reingart/pyfpdf/workflows/build/badge.svg)](https://github.com/reingart/pyfpdf/actions?query=workflow%3Abuild)
[![Pypi latest version](https://img.shields.io/pypi/v/pyfpdf.svg)](https://pypi.python.org/pypi/pyfpdf)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

pyfpdf: FPDF for Python
=======================

PyFPDF is a library for PDF document generation under Python, ported from PHP
(see [FPDF][1]: "Free"-PDF, a well-known PDFlib-extension replacement with many
examples, scripts and derivatives).

Compared with other PDF libraries, PyFPDF is simple, small and versatile, with
advanced capabilities, and is easy to learn, extend and maintain.

  [1]: http://www.fpdf.org/

**About the master branch of this fork**: it includes the following PRs:

  * [Deprecating .rotate() and introducing .rotation() context manager](https://github.com/reingart/pyfpdf/pull/161)
  * [Introducing a rect_clip() function](https://github.com/reingart/pyfpdf/pull/158)
  * [Fixing #159 issue with set_link + adding GitHub Actions pipeline & badges](https://github.com/reingart/pyfpdf/pull/160)
  * [Adding support for Contents alt text on Links](https://github.com/reingart/pyfpdf/pull/163)
  * [Making FPDF.output() x100 time faster by using a bytearray buffer](https://github.com/reingart/pyfpdf/pull/164)

Features:
---------

 * Python 2.5 to 3.4 support
 * Unicode (UTF-8) TrueType font subset embedding
 * Barcode I2of5 and code39, QR code coming soon ...
 * PNG, GIF and JPG support (including transparency and alpha channel)
 * Templates with a visual designer & basic html2pdf 
 * Exceptions support, other minor fixes, improvements and PEP8 code cleanups
 
Installation Instructions:
--------------------------

To get the latest development version you can download the source code running:

```
   git clone https://github.com/reingart/pyfpdf.git
   cd pyfpdf
   python setup.py install
```

You can also install PyFPDF from PyPI, with easyinstall or from Windows 
installers. For example, using pip:
```
   pip install fpdf
```

**Note:** the [Python Imaging Library](http://www.pythonware.com/products/pil/) 
(PIL) is needed for GIF support. PNG and JPG support is built-in and doesn't 
require any external dependency. For Python 3, 
[Pillow - The friendly PIL fork](https://github.com/python-pillow/Pillow) is 
supported.

Documentation:
--------------
[![Documentation Status](https://readthedocs.org/projects/pyfpdf/badge/?version=latest)](http://pyfpdf.rtfd.org)

 * [Read the Docs](http://pyfpdf.readthedocs.org/en/latest/)
 * [FAQ](docs/FAQ.md)
 * [Tutorial](docs/Tutorial.md) (Spanish translation available)
 * [Reference Manual](docs/ReferenceManual.md)

For further information, see the project site:
https://github.com/reingart/pyfpdf or the old Google Code project page
https://code.google.com/p/pyfpdf/.


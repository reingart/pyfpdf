pyfpdf: FPDF for python
=======================

PyFPDF is a library for PDF document generation under Python, ported from PHP
(see [FPDF][1] "Free"-PDF, a well-known PDFlib-extension replacement with many
examples, scripts and derivatives).

Compared with other PDF libraries, PyFPDF is simple, small and versatile, with
advanced capabilities and easy to learn, extend and maintain.

  [1]: http://www.fpdf.org/

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

**Note:** [Python Imaging Library](http://www.pythonware.com/products/pil/) 
(PIL) is needed for GIF support. PNG and JPG support is built-in and don't 
require any external dependency. For Python > 3.0 
[Pillow - The friendly PIL fork](https://github.com/python-pillow/Pillow) are 
supported.

Documentation:
--------------
[![Documentation Status](https://readthedocs.org/projects/pyfpdf/badge/?version=latest)](http://pyfpdf.rtfd.org)

 * [Read the Docs](http://pyfpdf.readthedocs.org/en/latest/)
 * [FAQ](docs/FAQ.md)
 * [Tutorial](docs/Tutorial.md)
 * [Reference Manual](docs/ReferenceManual.md) (spanish translation available)

For further information, see the project site:
https://github.com/reingart/pyfpdf or old google code project page
https://code.google.com/p/pyfpdf/


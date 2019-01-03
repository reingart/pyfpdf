pyfpdf: FPDF for Python
=======================

[![codecov](https://codecov.io/gh/alexanderankin/pyfpdf/branch/master/graph/badge.svg)](https://codecov.io/gh/alexanderankin/pyfpdf)

Minimalist PDF creation library for Python

```python
from fpdf import FPDF

document = FPDF()
document.add_page()
document.set_font('Arial', size=12)
document.cell(w=0, txt="hello world")
document.output("hello_world.pdf")
```

PyFPDF is a library for PDF document generation under Python, ported from PHP
(see [FPDF](http://www.fpdf.org/): "Free"-PDF, a well-known PDFlib-extension
replacement with many examples, scripts and derivatives).

Compared with other PDF libraries, PyFPDF is simple, small and versatile, with
advanced capabilities, and is easy to learn, extend and maintain.

Looking for Developer Help!
 
Installation Instructions:
--------------------------

You can install PyFPDF from PyPI, with easyinstall or from Windows 
installers. For example, using pip:

```bash
pip install fpdf2
```

To get the latest development version you can download the source code
running, you will need Pillow (`pip install pillow`)

```
  # Linux only:
  sudo apt-get install libjpeg-dev libpython-dev zlib1g-dev # libpython3.3-dev #(if necessary)

  # Linux and Windows:
  git clone https://github.com/alexanderankin/pyfpdf.git
  cd pyfpdf
  python setup.py install
```

Features:
---------

 * Python 2.7 to 3.5 support
 * Unicode (UTF-8) TrueType font subset embedding
 * Internal/External Links
 * PNG, GIF and JPG support (including transparency and alpha channel)
 * Shape, Line Drawing
 * Cell/Multi-cell/Plaintext writing, Automatic page breaks
 * Basic html2pdf (Templates with a visual designer in the works)
 * Exceptions support, other minor fixes, improvements and PEP8 code cleanups
 * Tox tests

Documentation:
--------------

[Documentation Home](https://alexanderankin.github.io/pyfpdf/).

Also read the design-spec/tests, they're great.

Developers:
-----------

To get development environment going, on Linux/Ubuntu:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python2.7 python3.4 python3.5 python3.6 \
  libpython2.7-dev libpython3.4-dev libpython3.5-dev \
  libpython3.6-dev
sudo apt-get install python3-distutils
wget 'https://bootstrap.pypa.io/get-pip.py'
python2.7 get-pip.py
sudo pip install tox
```

Lets try to improve the Code Coverage statistic so that we can safely
transition to external font and image libraries, and implement BytesIO usage
over string buffering!

Changes:
--------

`2.0.1`:

 * Clean up links and text files
 * Start to refactor syntax into own functions for readability
 * Replace pixel regexes with numpy in image parsing (s/o @pennersr)

`2.0.2`:

 * Attempt to fix missing `fpdf.util`, delete from [PyPI.org](https://pypi.org/project/fpdf2/2.0.2/)

`2.0.3`:

 * Change to `setup(packages = find_packages())`

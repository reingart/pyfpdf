#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import sys
import warnings
import subprocess

import fpdf
package_dir = 'fpdf'

# convert the README and format in restructured text (only when registering)
long_desc = ""
if os.path.exists("README.md"):
    try:
        cmd = ['pandoc', '--from=markdown', '--to=rst', 'README.md']
        long_desc = subprocess.check_output(cmd).decode("utf8")
    except Exception as e:
        warnings.warn("Exception when converting the README format: %s" % e)

setup(name='fpdf',
      version=fpdf.__version__,
      description='Simple PDF generation for Python',
      long_description=long_desc,
      author='Olivier PLATHEY ported by Max',
      author_email='maxpat78@yahoo.it',
      maintainer = "Mariano Reingart",
      maintainer_email = "reingart@gmail.com",
      url='http://code.google.com/p/pyfpdf',
      license='LGPLv3+',
      download_url="https://github.com/reingart/pyfpdf/tarball/%s" % fpdf.__version__,
      packages=['fpdf', ],
      package_dir={'fpdf': package_dir},
      package_data={'fpdf': ['font/*.ttf', 'font/*.txt']},
      classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.5",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: PHP Classes",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Multimedia :: Graphics",
      ],
      keywords=["pdf", "unicode", "png", "jpg", "ttf"],
     )


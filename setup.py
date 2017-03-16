#!/usr/bin/env python

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

import os
import sys
import warnings
import subprocess

import unittest
def run_test_suite():
  """Runs the tests in test/ folder with unittest
  
  Use the default shared TestLoader instance:
  # test_loader = unittest.defaultTestLoader
  test_loader = unittest.TestLoader()


  Automatically discover all tests in the current dir of the form test/*.py
  # NOTE: only works for python 2.7 and later
  test_suite = test_loader.discover('tests', pattern='test/*.py')

  To use the basic test runner that outputs to sys.stderr:
    # test_runner = unittest.TextTestRunner()
    # run the test suite
    # test_runner.run(test_suite)

  To run with setup.py test, tox, and codecov.io, return the test_suite:
  return test_suite
  """
  return unittest.TestLoader().discover('test', pattern = '*.py')

import fpdf
package_dir = 'fpdf'

def read(path):
  """Build a file path from *paths* and return the contents."""
  with open(path, 'r') as f:
    return f.read()

setup(
  name         = 'fpdf',
  version      = fpdf.__version__,
  description  = 'Simple PDF generation for Python',
  long_description = read('./PyPIReadme.rst'),
  author       ='Olivier PLATHEY ported by Max',
  author_email ='maxpat78@yahoo.it',
  maintainer       = "David Ankin",
  maintainer_email = "daveankin@gmail.com",
  url          = 'http://code.google.com/p/pyfpdf',
  license      = 'LGPLv3+',
  download_url = "https://github.com/alexanderankin/pyfpdf/tarball/%s" % fpdf.__version__,
  packages     = ['fpdf', ],
  package_dir  = {'fpdf': package_dir},
  package_data = {'fpdf': ['font/*.ttf', 'font/*.txt']},
  test_suite   = 'setup.run_test_suite',
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
  keywords = ["pdf", "unicode", "png", "jpg", "ttf"],
  # include_package_data = True,
)

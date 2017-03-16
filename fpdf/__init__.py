#!/usr/bin/env python
# -*- coding: utf-8 -*-
"FPDF for Python"

from .fpdf import FPDF, FPDF_VERSION, FPDF_FONT_DIR, \
                  FPDF_CACHE_MODE, FPDF_CACHE_DIR, SYSTEM_TTFONTS

__license__ = "LGPL 3.0"
__version__ = FPDF_VERSION

try:
  from .html import HTMLMixin
except ImportError:
  import warnings
  warnings.warn("web2py gluon package not installed, required for html2pdf")

from .template import Template

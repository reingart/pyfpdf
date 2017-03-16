# Python 3000 #

[TOC]

Python 3.x is a new version of the language, with some backward compatibility issues.

In general, Python 2.x code does not run unmodified under Python 3.x, mostly because the "unicode/string/buffer issue", so some steps are taking place to port this library to the new version.

# Chosen Path #

There will not be a manual py3k repository; all py3k changes will be back-ported to the trunk ~~in order to enable 2to3 conversion automatically~~ (unified codebase, compatible with both Python 2 and Python 3, without needing the 2to3 converter in the latest revisions).

As this library is pure Python and has no dependencies (beside PIL optionally), there is no need to do a huge re-factor.
BTW, initial py3k support took a few changes, see changeset c2f3bae9b379 (just 8 changes). More changes are coming to fix Unicode TTF and image support.

Most string and buffering methods are encapsulated in well-known places (like the `_out` and `sprintf` functions), so they should not cause a big impact.

Also, the library is Unicode aware since version 1.7, so also that impact could be mitigated.

**NOTE:** Until [PEP 461](http://www.python.org/dev/peps/pep-0461/) (add % formatting to bytes) is officialy accepted in Python or a suitable alternative is implemented, internal formatting is done using latin1 Unicode strings instead of raw bytes, as this feature is extensively used in the code and allows it to be clean and compact.

# Conversion Script #

**IMPORTANT NOTE**: since version 1.7.2 (revision ca2968763421) the codebase has been unified, so there is no need to run any conversion script. (Please skip this section.)

In Windows, you can use `py3k.bat`, which just calls `2to3.py`, install the package and run the basic test:

```
mkdir fpdf_py3k
c:\python32\tools\Scripts\2to3.py -f all -w -o fpdf_py3k -n fpdf 
c:\Python32\python.exe setup.py install
c:\Python32\python.exe tests\py3k.py
```

`setup.py` has the logic to detect the interpreter version and install the correct version of the library.

# Status #

Currently (version 1.7.2, January 2014) there is early experimental support for Python 3:

  * most directives are supported (at least `add_page`, `set_font`, `ln`, `write`, `output`)
  * compression is not yet supported (zlib support should be rewritten)
  * TTF Unicode fonts are not yet supported, use windows-1252 standard fonts (latin1)
  * image support is working at least for PNG (JPG and GIF are untested, and also depend on PIL)

# Example #

The following example runs unmodified on Python 2.x and Python 3.x

```python
from fpdf import FPDF
    
pdf = FPDF()
# compression is not yet supported in py3k version
pdf.compress = False
pdf.add_page()
# Unicode is not yet supported in the py3k version; use windows-1252 standard font
pdf.set_font('Arial', '', 14)  
pdf.ln(10)
pdf.write(5, 'hello world %s áéíóúüñ' % sys.version)
pdf.image("pyfpdf/tutorial/logo.png", 50, 50)
pdf.output('py3k.pdf', 'F')
```

View the result here: [py3k.pdf](https://github.com/reingart/pyfpdf/raw/master/tests/py3k.pdf)

It should contain:

```
hello world 3.2.2 (default, Sep 4 2011, 09:51:08) [MSC v.1500 32 bit (Intel)] áéíóúüñ
```

(áéíóúüñ is a latin1 test)

And the FPDF logo.

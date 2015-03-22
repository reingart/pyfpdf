# Python 3000 #

Python 3.x is a new version of the language, with some backward compatibility issues.

In general, Python 2.x code does not run unmodified under Python 3.x, mostly because the "unicode/string/buffer issue", so some steps are taking place to port this library to the new version.

# Chosen Path #

There will not be a manual py3k repository, all py3k changes will be back-ported to the trunk ~~in order to enable 2to3 conversion automatically~~ (unified codebase both Python 2 and Python 3 compatible, no need of 2to3 in latest revisions).

As this library is pure-python and has not dependencies (beside PIL optionally), there is no need to do a huge re-factory.
BTW, initial py3k support took a few changes, see changeset c2f3bae9b379 (just 8 changes). More changes are coming to fix unicode ttf and image support.

Most string/buffering methods are encapsulated in well-known places (like `_out ` or `sprintf` functions), so they should not cause a big impact.

Also, the library is unicode aware since version 1.7, so also that impact could be mitigated.

**NOTE:** Until [PEP 461](http://www.python.org/dev/peps/pep-0461/) (add % formating to bytes) is officialy accepted in python or a suitable alternative is implemented, internal formatting is done using latin1 unicode strings instead of raw bytes, as this feature is extensively used in the code and allows it to be clean and compact.

# Conversion Script #

**IMPORTANT NOTE**: since version 1.7.2 (revision ca2968763421) the codebase has been unified, so there is no need to run any conversion script (please skip this section).

In windows, you can use `py3k.bat`, that just calls `2to3.py`, install de package and runt the basic test:

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
  * ttf unicode fonts are not yet supported, use windows-1252 standards fonts (latin1)
  * image support is working at least for PNG (JPG/GIF is untested, and depends also on PIL)

# Example #

The following example runs unmodified on Python 2.x and Python 3.x

```
from fpdf import FPDF
    
pdf = FPDF()
# compression is not yet supported in py3k version
pdf.compress = False
pdf.add_page()
# unicode is not yet supported in py3k version, use windows-1252 standards font
pdf.set_font('Arial', '', 14)  
pdf.ln(10)
pdf.write(5, 'hello world %s áéíóúüñ' % sys.version)
pdf.image("pyfpdf/tutorial/logo.png", 50, 50)
pdf.output('py3k.pdf','F')
```

View the result here: [py3k.pdf](https://pyfpdf.googlecode.com/hg/tests/py3k.pdf)

It should contain:

```
hello world 3.2.2 (default, Sep 4 2011, 09:51:08) [MSC v.1500 32 bit (Intel)] áéíóúüñ
```

(áéíóúüñ is a latin1 test)

And the FPDF logo.
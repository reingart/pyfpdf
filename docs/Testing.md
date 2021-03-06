# Testing #

[TOC]

This page describes the test suite of the PyFPDF library.

This page applicable to version 1.7.1 and newer.

## Old tests ##

There are old tests in the `tests` folder from the stone-age. These will be removed when the test suite completely supersedes all the old tests.

## Purposes ##

  * Cover all fixed issues
  * Reach **byte-to-byte accuracy** with all Python versions (2.x and 3.x)
  * Alert when a change made in the library breaks something

## Selected solution ##

Currently we support two different ways to run the test suite:

  * `runtest.py` - custom script
  * [unittest](https://docs.python.org/3/library/unittest.html) - testing framework from the Python standard library

## runtest.py ##

  * Automatically tests all available Python interpreters.
  * Better support for older Python versions (prior to 2.7)
  * Shows a concise table of results
  * Shows hints
  * Temporary files are stored inside the `tests/out-x.x.x` folder.

### Quick start ###

This is not not an exclusive list of methods.

Installed copy:

  * Go to the _tests_ folder
  * Run `python runtest.py`

Local copy:

  * Go to the _tests_ folder
  * Set the PYFPDFTESTLOCAL variable
  * Run `prepare_local.sh` or `prepare_local.bat`
  * Run `python runtest.py`

Distributed copy:

  * In the root distributed folder:
  * `PYTHON_PATH=. python tests/runtest.py`

You can list specific tests and interpreters with the `--test` and `--interp` arguments. For detailed information see `--help`.

Please note, batch operations test required minimum in library, but when you call any test directly with `python test/cover/text_xx.py`.

Allowed syntax for calling `tests/cover/*` tests:
 
  * `--auto` - do not add timestamp and author metadata, do not open the created PDF (if the test produces one)
  * `--check` - check generated PDFs against an expected hash
  * result filename.

PDF output with `--auto` may differ.

### Structure ###

  * `cover` - all new tests
  * `fpdf_local` - local copy of fpdf, generated by prepare\_local
  * `out-x.x.x` - working directory for python x.x.x
  * `runtest.py` - batch tester
  * `resources.txt` - resources list
  * data files
  * old tests etc.

Every test can be executed as a standalone app from `tests/cover` or the `tests/out-x.x.x` folder.

## unittest ##

  * More familiar and well documented framework (to specify different interpreters, enable warnings, etc)
  * Better exception reporting when a test fails
  * Shows unclosed files and deprecation warnings
  * Files are created in the current folder

### Quck start ###

```
PYTHON_PATH=. python -m unittest discover -s tests/cover/
```

## Variables ##

Variables:

  * `format` - PDF, TXT
  * `fn` - result filename (if the test doesn't produce any external file, this can be omitted)
  * `hash` - hash when the file is created in automatic test mode
  * `2to3` - use the 2to3 tool (default - no)
  * `python2` - this test can be used with python2 (default - yes)
  * `python3` - this test can be used with python3 (default - yes)
  * `pil` - PIL or Pillow module is required (default - no)
  * `platform` - platform for this test (win32, linux2, etc; by default - all)

## Fonts ##

Some (most) tests use a font pack: <http://pyfpdf.googlecode.com/files/fpdf_unicode_font_pack.zip>

Place .ttf files in the _tests/font_ folder. You can use the `--downloadfonts` option of `runtest.py` to download and extract them.

## Test template ##

File `tests/cover/test_template.py` contains all additional information.



# History #

This project, `fpdf2` is a _fork_ of the `PyFPDF` project, which can be found
[on GitHub at reingart/pyfpdf](https://github.com/reingart/pyfpdf)
but has been inactive since January of 2018.

On 2023/08/04, `fpdf2` moved to the `py-pdf` organization: https://github.com/py-pdf/fpdf2. The context for this move can be found there: https://github.com/py-pdf/fpdf2/discussions/752. On this date, the `PyFPDF` GitHub organization has been **archived**.

About the original `PyFPDF` lib:

> This project started as a Python fork of the [FPDF](http://fpdf.org/) PHP library,
> ported to Python by Max Pat in 2006: <http://www.fpdf.org/dl.php?id=94>.
> Later, code for native reading TTF fonts was added.
> The project aim is to keep the library up to date, to fulfill the goals of its
> [original roadmap](https://github.com/reingart/pyfpdf/wiki/Roadmap) and provide
> a general overhaul of the codebase to address technical debt keeping features from being added
> and bugs to be eradicated.
> Until 2015 the code was developed at [Google Code](https://code.google.com/p/pyfpdf/):
> you can still access the [old issues](https://github.com/reingart/pyfpdf_googlecode/issues),
> and [old wiki](https://github.com/reingart/pyfpdf_googlecode/tree/wiki).

As of version [2.5.4](https://github.com/py-pdf/fpdf2/blob/master/CHANGELOG.md),
`fpdf2` is fully backward compatible with PyFPDF, with the exception of one minor point:
for the [`cell()` method](fpdf/fpdf.html#fpdf.fpdf.FPDF.cell), the default value of `h` has changed.
It used to be `0` and is now set to the current value of `FPDF.font_size`.

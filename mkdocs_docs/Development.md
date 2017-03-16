# Development #

[TOC]

## Introduction ##

This page has summary information about developing the PyPDF library.

This project started as Python fork of the [FPDF](http://fpdf.org/) PHP library. 
Later, code for native reading TTF fonts was added. FPDF has not been updated since
2011. See also the [TCPDF](http://www.tcpdf.org/) library.

Until 2015 the code was developed at [Google Code](https://code.google.com/p/pyfpdf/).
Now the main repository is at [Github](https://github.com/reingart/pyfpdf).

You can also view the
[old repository](https://github.com/reingart/pyfpdf_googlecode),
[old issues](https://github.com/reingart/pyfpdf_googlecode/issues), and 
[old wiki](https://github.com/reingart/pyfpdf_googlecode/tree/wiki).

After being committed to the master branch, code documentation is automatically uploaded to 
the [Read the Docs](http://pyfpdf.rtfd.org/) site.

## Repository structure ##

 * `[attic]` - folder with old code and useful, but unsupported things
 * `[docs]` - documenation folder
 * `[examples]` - some examples
 * `[fpdf]` - library source
 * `[test]` - test suite (see [Testing](Testing.md))
 * `[tools]` - some utilities
 * `[tutorial]` - tutorials (see also [Tutorial](Tutorial.md))
 * `LICENSE` - license information
 * `setup.cfg` - wheel configuration (see [wheel](https://wheel.rtfd.org))
 * `setup.py` - distutils installer (see [Python Packaging User Guide](https://python-packaging-user-guide.rtfd.org))
 * `mkdocs.yml` - config for [MkDocs](http://www.mkdocs.org/)

## Tips ##

### Code ###

To get the master branch of the code:
```shell
git clone https://github.com/reingart/pyfpdf.git
```

You can also use issues and pull requests at Github.

### Testing ###

Testing described in the standalone page [Testing](Testing.md).

### Documentation ###

Documentation is in the `docs` subfolder in 
[Markdown](http://daringfireball.net/projects/markdown/) format. To build it,
the `mkdocs` utility is used, which is directed by `mkdocs.yml`.

To build documentation, run in the repository root:

```
mkdocs build
```
HTML files are generated in a `html` subfolder.

To continiously rebuild docs on changing any `.md` files use:

```
mkdocs serve
```

Then open a browser at <http://localhost:8000>. (The port and address can be changed.)

**Note**: `mkdocs` internally checks the consistency of internal links. But somehow
code like this:

```
[Page Name][refe/PageName,md]
```

leads to nowhere and gives no error. To avoid this use:

```
grep -r * -e ',md'
```

And output should link to this page only.

## See also ##
[Project Home](index.md), [Frequently asked questions](FAQ.md), 
[Unicode](Unicode.md), [Python 3](Python3.md), [Testing](Testing.md).


# Delopment #

[TOC]

## Inroduction ##

This page summary information about development PyPDF library.

This project started as python fork of [FPDF](http://fpdf.org/) PHP library. 
Later code for native reading TTF fonts was added. FPDF was not updated since
2011. See also [TCPDF](http://www.tcpdf.org/) library.

Until 2015 code developed at [Google code](https://code.google.com/p/pyfpdf/).
Now main repository at [Github](https://github.com/reingart/pyfpdf).

You can also view 
[old repository](https://github.com/reingart/pyfpdf_googlecode),
[old issues](https://github.com/reingart/pyfpdf_googlecode/issues), and 
[old wiki](https://github.com/reingart/pyfpdf_googlecode/tree/wiki).

After commit to master repository code documentation will be uploaded to 
[Read the Docs](http://pyfpdf.rtfd.org/) site.

## Repository structure ##

 * `[attic]` - folder with old code and usefull, but unsupported things
 * `[docs]` - documenation folder
 * `[examples]` - some examples
 * `[fpdf]` - library source
 * `[test]` - test suite (see [Testing](Testing.md))
 * `[tools]` - some utilities
 * `[tutorial]` - tutorials (see also [Tutorial](Tutorial.md))
 * `LICENSE` - license information
 * `setup.cfg` - wheel configuration (see [wheel](https://wheel.rtfd.org))
 * `setup.py` - distutils installator (see [Python Packaging User Guide](https://python-packaging-user-guide.rtfd.org))
 * `mkdocs.yml` - config for [MkDocs](http://www.mkdocs.org/)

## Tips ##

### Code ###

Get master branch of code.
```shell
git clone https://github.com/reingart/pyfpdf.git
```

You can also use issues and pull requests at github.

### Testing ###

Testing described in standalone page [Testing](Testing.md).

### Documentation ###

Documentation are in `docs` subfolder in 
[Markdown](http://daringfireball.net/projects/markdown/) format. To build use
`mkdocs` utility, which directed by `mkdocs.yml`.

To build documentation use in repository root:

```
mkdocs build
```
HTML files are generated in `html` subfolder.

To continiously rebuild docs on changing any `.md` files use:

```
mkdocs serve
```

Then open browser at <http://localhost:8000>. (Port and address can be changed).

**Note**: `mkdocs` internally chack internal links consistency. But somhow
code like this:

```
[Page Name][refe/PageName,md]
```

Lead to nowhere and gives no error. To avoid this use:

```
grep -r * -e ',md'
```

And output should link to this page only.

## See also ##
[Project Home](index.md), [Frequently asked questions](FAQ.md), 
[Unicode](Unicode.md), [Python 3](Python3.md), [Testing](Testing.md).


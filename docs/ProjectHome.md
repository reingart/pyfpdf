# FPDF for Python #

<a href='https://github.com/reingart/pyfpdf'><img src='https://s3.amazonaws.com/github/ribbons/forkme_right_red_aa0000.png' alt='Fork me on GitHub' border='0' align='right' /></a>

_PyFPDF_ is a library for PDF document generation under Python, ported from PHP (see [FPDF](http://www.fpdf.org/): "Free"-PDF, a well-known PDFlib-extension replacement with many examples, scripts and derivatives).

**Latest Released Version: 1.7 (August 15th, 2012)**  -  **Current Development Version: 1.7.1**

## Main features ##
  * Easy to use (and easy to extend)
  * Many simple examples and scripts available in many languages
  * No external dependencies or extensions (optionally PIL for GIF support)
  * No installation, no compilation or other libraries (DLLs) required
  * Small and compact code, useful for testing new features and teaching

This repository is a fork of the library's [original port by Max Pat](http://www.fpdf.org/dl.php?id=94), with the following enhancements:

  * Python 2.5 to 3.4+ support (see [Python3](Python3.md) support)
  * [Unicode](Unicode.md) (UTF-8) TrueType font subset embedding (Central European, Cyrillic, Greek, Baltic, Thai, Chinese, Japanese, Korean, Hindi and almost any other language in the world) **New!** based on [sFPDF](http://www.fpdf.org/en/script/script91.php) LGPL3 PHP version from [Ian Back](mailto:ian@bpm1.com?subject=sFPDF)
  * Improved installers (setup.py, py2exe, PyPI) support
  * Barcode I2of5 and code39, QR code coming soon ...
  * PNG, GIF and JPG support (including transparency and alpha channel) **New!**
  * Exceptions support, other minor fixes, improvements and PEP8 code cleanups
  * Port of the [Tutorial](Tutorial.md) and [ReferenceManual](ReferenceManual.md)  (Spanish translation available)

FPDF original features:

  * Choice of measurement unit, page format and margins
  * Page header and footer management
  * Automatic page break
  * Automatic line break and text justification
  * Image, colors and links support
  * Page compression
  * Extensive [Tutorial](http://www.fpdf.org/en/tutorial/index.php) and complete online [documentation](http://www.fpdf.org/en/doc/index.php)

## Installation ##

  * Using [PyPI](http://pypi.python.org/pypi?:action=display&name=fpdf&version=1.7)
  * Using [EasyInstall](http://peak.telecommunity.com/DevCenter/EasyInstall) `c:\python27\Scripts\easy_install.exe fpdf`
  * From source:
    * [Download](https://github.com/reingart/pyfpdf/releases) and unpack source package (zip) or pull from the [repository](https://github.com/reingart/pyfpdf)
    * Run `python setup.py install`
  * Using [MSI](http://pyfpdf.googlecode.com/files/fpdf-1.7.win32.msi) or [Windows Installers](http://pyfpdf.googlecode.com/files/fpdf-1.7.hg.zip)

For your convenience, some installers include the optional ["Free Unicode TrueType Font Pack"](http://pyfpdf.googlecode.com/files/fpdf_unicode_font_pack.zip) (96 TTF files, 16MB compressed). Please note that copyright restrictions may apply when embedding fonts.

## Support ##

For community support, please feel free to file an [issue](https://github.com/reingart/pyfpdf/issues).

For priority technical support, you can contact [Mariano Reingart](mailto:reingart@gmail.com) (current maintainer and project owner). Online payments accepted through PayPal.

### Pre-paid priority tech support plans ###

  * <a href='https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=KYCMCYA3LX4KG&on0=Coverage+plan&os0=per+email%3A+1+day%2C+up+to+15+min&currency_code=USD&submit.x=89&submit.y=8'>per email: 1 day coverage, up to 15 min $10,00 USD</a>
  * <a href='https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=KYCMCYA3LX4KG&on0=Coverage+plan&os0=per+incident%3A+1+week%2C++up+to+2+hs&currency_code=USD&submit.x=112&submit.y=15'>per incident: 1 week coverage, up to 2 hs $50,00 USD</a>
  * <a href='https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=KYCMCYA3LX4KG&on0=Coverage+plan&os0=per+feature%3A+1+month%2C+up+to+6+hs&currency_code=USD&submit.x=64&submit.y=18'>per feature: 1 month coverage, up to 6 hs $150,00 USD</a>
  * <a href='https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=KYCMCYA3LX4KG&on0=Coverage+plan&os0=per+project%3A+3+month%2C+up+to+15+hs&currency_code=USD&submit.x=87&submit.y=14'>per project: 3 month coverage, up to 15 hs $350,00 USD</a>
  * <a href='https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=KYCMCYA3LX4KG&on0=Coverage+plan&os0=extended%3A+9+month%2C+up+to+30hs&currency_code=USD&submit.x=90&submit.y=9'>extended: 9 month coverage, up to 30hs $750,00 USD</a>

<a href='https://www.paypal.com/ar/cgi-bin/webscr?cmd=xpt/Marketing/general/WIPaypal-outside'><img src='https://www.paypal.com/es_XC/Marketing/i/logo/bnr_international_buyer3_347x41.gif' alt='Vendedor internacional' border='0' /></a>

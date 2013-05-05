# -*- coding: utf-8 -*-

"HTML Renderer for FPDF.py (unicode)"

__author__ = "Mariano Reingart <reingart@gmail.com>"
__copyright__ = "Copyright (C) 2010 Mariano Reingart"
__license__ = "LGPL 3.0"

# Inspired by tuto5.py and several examples from fpdf.org, html2fpdf, etc.

from fpdf import FPDF, HTMLMixin


if __name__ == '__main__':

   
    class MyFPDF(FPDF, HTMLMixin): pass
    
    pdf=MyFPDF()
    
    # load the unicode font
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    
    pdf.add_page()
    
    # test the basic fonts
    pdf.write_html("""<p><font face="Arial"><B>hello</B> <I>world</I></font></p>""")
    pdf.write_html("""<p><font face="Times"><B>hello</B> <I>world</I></font></p>""")
    pdf.write_html("""<p><font face="Courier"><B>hello</B> <I>world</I></font></p>""")
    pdf.write_html("""<p><font face="zapfdingbats"><B>hello</B> <I>world</I></font></p>""")
    
    # test the unicode (utf8) font:
    
    # greek
    pdf.write_html(u"""<p><font face="DejaVu">Γειά σου κόσμος</font></p>""")
    # russian
    pdf.write_html(u"""<p><font face="DejaVu">Здравствуй, Мир</font></p>""")

    pdf.output('html_unicode.pdf','F')
        
    import os
    try:
        os.startfile("html_unicode.pdf")
    except:
        os.system("xdg-open \"%s\"" % fn)

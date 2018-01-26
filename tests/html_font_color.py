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
    
    pdf.add_page()
    
    # test the basic fonts and colors
    
    pdf.write_html("""<p><font color='#FFC0CB'><B>hello</B> <I>world</I></font></p>""")
    pdf.write_html("""<p><font face="Arial" color='#FF0000'><B>hello</B> <I>world</I></font></p>""")
    pdf.write_html("""<p><font face="Times" color='#0000FF'><B>hello</B> <I>world</I></font></p>""")
    pdf.write_html("""<p><font face="Courier" color='#A020F0'><B>hello</B> <I>world</I></font></p>""")
    pdf.write_html("""<p><font face="zapfdingbats" color='#A52A2A'><B>hello</B> <I>world</I></font></p>""")

    fn = 'html_font_color.pdf'
    pdf.output(fn,'F')
        
    import os
    try:
        os.startfile(fn)
    except:
        os.system("xdg-open \"%s\"" % fn)

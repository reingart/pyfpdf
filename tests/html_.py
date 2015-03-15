# -*- coding: latin-1 -*-

"HTML Renderer for FPDF.py"

__author__ = "Mariano Reingart <reingart@gmail.com>"
__copyright__ = "Copyright (C) 2010 Mariano Reingart"
__license__ = "LGPL 3.0"

# Inspired by tuto5.py and several examples from fpdf.org, html2fpdf, etc.

from fpdf import FPDF, HTMLMixin


if __name__=='__main__':
    html="""
<H1 align="center">html2fpdf</H1>
<h2>Basic usage</h2>
<p>You can now easily print text mixing different
styles : <B>bold</B>, <I>italic</I>, <U>underlined</U>, or
<B><I><U>all at once</U></I></B>!<BR>You can also insert links
on text, such as <A HREF="http://www.fpdf.org">www.fpdf.org</A>,
or on an image: click on the logo.<br>
<center>
<A HREF="http://www.fpdf.org"><img src="../tutorial/logo.png" width="104" height="71"></A>
</center>
<h3>Sample List</h3>
<ul><li>option 1</li>
<ol><li>option 2</li></ol>
<li>option 3</li></ul>

<table border="0" align="center" width="50%">
<thead><tr><th width="30%">Header 1</th><th width="70%">header 2</th></tr></thead>
<tbody>
<tr><td>cell 1</td><td>cell 2</td></tr>
<tr><td>cell 2</td><td>cell 3</td></tr>
</tbody>
</table>


<table border="1">
<thead><tr bgcolor="#A0A0A0"><th width="30%">Header 1</th><th width="70%">header 2</th></tr></thead>
<tfoot><tr bgcolor="#E0E0E0"><td>footer 1</td><td>footer 2</td></tr></tfoot>
<tbody>
<tr><td>cell 1</td><td>cell 2</td></tr>
<tr>
<td width="30%">cell 1</td><td width="70%" bgcolor="#D0D0FF" align='right'>cell 2</td>
</tr>
</tbody>
<tbody><tr><td colspan="2">cell spanned</td></tr></tbody>
<tbody>
""" + """<tr bgcolor="#F0F0F0">
<td>cell 3</td><td>cell 4</td>
</tr><tr bgcolor="#FFFFFF">
<td>cell 5</td><td>cell 6</td>
</tr>""" * 200 + """
</tbody>
</table>

<font face='helvetica' size='40'>Font example: Arial 40pt</font>
 

"""

    class MyFPDF(FPDF, HTMLMixin):
        def header(self):
            self.image('../tutorial/logo_pb.png',10,8,33)
            self.set_font('Arial','B',15)
            self.cell(80)
            self.cell(30,10,'Title',1,0,'C')
            self.ln(20)
            
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial','I',8)
            txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(0,10,txt,0,0,'C')
        
    pdf=MyFPDF()
    #First page
    pdf.add_page()
    pdf.write_html(html)

    # this will fail (tables without width are not supported):
    try:
        pdf.write_html("""<table><tr><td></td></tr></table>""")
    except RuntimeError:
        pass

    # this may be rendered incorrectly as currently there is no two pass auto-layout:
    pdf.write_html("""<table><tr><th></th><td width="100%">100%</td></tr></table>""")

    fn = 'html.pdf'
    pdf.output(fn,'F')
        
    import os
    try:
        os.startfile(fn)
    except:
        os.system("xdg-open \"%s\"" % fn)

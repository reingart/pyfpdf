# PyFPDF Reference Manual #

[TOC]

## Original FPDF API ##

**Important**: original FPDF (PHP) naming convention is CamelCase. This library uses [PEP8](http://www.python.org/dev/peps/pep-0008/) lower\_case\_with\_underscores recommendation.

  * [accept_page_break](reference/AcceptPageBreak.md) - accept or not automatic page break
  * [add_font](reference/AddFont.md) - add a new font
  * [add_link](reference/AddLink.md) - create an internal link
  * [add_page](reference/AddPage.md) - add a new page
  * [alias_nb_pages](reference/AliasNbPages.md) - define an alias for number of pages
  * [cell](reference/Cell.md) - print a cell
  * [close](reference/Close.md) - terminate the document
  * [error](reference/Error.md) - fatal error
  * [footer](reference/Footer.md) - page footer
  * [FPDF](reference/FPDF.md) - constructor
  * [get_string_width](reference/GetStringWidth.md) - compute string length
  * [get_x](reference/GetX.md) - get current x position
  * [get_y](reference/GetY.md) - get current y position
  * [header](reference/Header.md) - page header
  * [image](reference/Image.md) - output an image
  * [line](reference/Line.md) - draw a line
  * [link](reference/Link.md) - put a link
  * [ln](reference/Ln.md) - line break
  * [multi_cell](reference/MultiCell.md) - print text with line breaks
  * [output](reference/Output.md) - save or send the document
  * [page_no](reference/PageNo.md) - page number
  * [rect](reference/Rect.md) - draw a rectangle
  * [set_author](reference/SetAuthor.md) - set the document author
  * [set_auto_page_break](reference/SetAutoPageBreak.md) - set the automatic page breaking mode
  * [set_compression](reference/SetCompression.md) - turn compression on or off
  * [set_creator](reference/SetCreator.md) - set document creator
  * [set_display_mode](reference/SetDisplayMode.md) - set display mode
  * [set_draw_color](reference/SetDrawColor.md) - set drawing color
  * [set_fill_color](reference/SetFillColor.md) - set filling color
  * [set_font](reference/SetFont.md) - set font
  * [set_font_size](reference/SetFontSize.md) - set font size
  * [set_keywords](reference/SetKeywords.md) - associate keywords with document
  * [set_left_margin](reference/SetLeftMargin.md) - set left margin
  * [set_line_width](reference/SetLineWidth.md) - set line width
  * [set_link](reference/SetLink.md) - set internal link destination
  * [set_margins](reference/SetMargins.md) - set margins
  * [set_right_margin](reference/SetRightMargin.md) - set right margin
  * [set_subject](reference/SetSubject.md) - set document subject
  * [set_text_color](reference/SetTextColor.md) - set text color
  * [set_title](reference/SetTitle.md) - set document title
  * [set_top_margin](reference/SetTopMargin.md) - set top margin
  * [set_x](reference/SetX.md) - set current x position
  * [set_xy](reference/SetXY.md) - set current x and y positions
  * [set_y](reference/SetY.md) - set current y position
  * [text](reference/Text.md) - print a string
  * [write](reference/Write.md) - print flowing text

## Additional API ##
  
This features not available in original FPDF and implemented after fork.

  * [dashed_line](reference/DashedLine.md) - draw a dashed line
  * [ellipse](reference/Ellipse.md) - draw an ellipse
  * [set_stretching](reference/SetStretching.md) - set horizontal font stretching
  * [write_html](reference/WriteHTML.md) - print text with HTML markup


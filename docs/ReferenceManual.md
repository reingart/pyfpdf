# PyFPDF Reference Manual #

[TOC]

## Original FPDF API ##

**Important**: original FPDF (PHP) naming convention is CamelCase. This library uses [PEP8](http://www.python.org/dev/peps/pep-0008/) lower\_case\_with\_underscores recommendation.

  * [AcceptPageBreak](reference/AcceptPageBreak.md) - accept or not automatic page break
  * [AddFont](reference/AddFont.md) - add a new font
  * [AddLink](reference/AddLink.md) - create an internal link
  * [AddPage](reference/AddPage.md) - add a new page
  * [AliasNbPages](reference/AliasNbPages.md) - define an alias for number of pages
  * [Cell](reference/Cell.md) - print a cell
  * [Close](reference/Close.md) - terminate the document
  * [Error](reference/Error.md) - fatal error
  * [Footer](reference/Footer.md) - page footer
  * [FPDF](reference/FPDF.md) - constructor
  * [GetStringWidth](reference/GetStringWidth.md) - compute string length
  * [GetX](reference/GetX.md) - get current x position
  * [GetY](reference/GetY.md) - get current y position
  * [Header](reference/Header.md) - page header
  * [Image](reference/Image.md) - output an image
  * [Line](reference/Line.md) - draw a line
  * [Link](reference/Link.md) - put a link
  * [Ln](reference/Ln.md) - line break
  * [MultiCell](reference/MultiCell.md) - print text with line breaks
  * [Output](reference/Output.md) - save or send the document
  * [PageNo](reference/PageNo.md) - page number
  * [Rect](reference/Rect.md) - draw a rectangle
  * [SetAuthor](reference/SetAuthor.md) - set the document author
  * [SetAutoPageBreak](reference/SetAutoPageBreak.md) - set the automatic page breaking mode
  * [SetCompression](reference/SetCompression.md) - turn compression on or off
  * [SetCreator](reference/SetCreator.md) - set document creator
  * [SetDisplayMode](reference/SetDisplayMode.md) - set display mode
  * [SetDrawColor](reference/SetDrawColor.md) - set drawing color
  * [SetFillColor](reference/SetFillColor.md) - set filling color
  * [SetFont](reference/SetFont.md) - set font
  * [SetFontSize](reference/SetFontSize.md) - set font size
  * [SetKeywords](reference/SetKeywords.md) - associate keywords with document
  * [SetLeftMargin](reference/SetLeftMargin.md) - set left margin
  * [SetLineWidth](reference/SetLineWidth.md) - set line width
  * [SetLink](reference/SetLink.md) - set internal link destination
  * [SetMargins](reference/SetMargins.md) - set margins
  * [SetRightMargin](reference/SetLeftMargin.md) - set right margin
  * [SetSubject](reference/SetSubject) - set document subject
  * [SetTextColor](reference/SetTextColor.md) - set text color
  * [SetTitle](reference/SetTitle.md) - set document title
  * [SetTopMargin](reference/SetLeftMargin.md) - set top margin
  * [SetX](reference/SetX.md) - set current x position
  * [SetXY](reference/SetXY.md) - set current x and y positions
  * [SetY](reference/SetY.md) - set current y position
  * [Text](reference/Text.md) - print a string
  * [Write](reference/Write.md) - print flowing text

## Additional API ##
  
This features not available in original FPDF and implemented after fork.

  * [DashedLine](reference/DashedLine.md) - draw a dashed line
  * [Ellipse](reference/Ellipse.md) - draw an ellipse
  * [SetStretching](reference/SetStretching.md) - set horizontal font stretching
  * [WriteHTML](reference/WriteHTML.md) - print text with HTML markup


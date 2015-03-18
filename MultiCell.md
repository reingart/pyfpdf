## MultiCell ##

```
fpdf.multi_cell(w: float, h: float, txt: str, border=0, align: str = 'J', fill: bool = 0)
```

### Description ###

This method allows printing text with line breaks. They can be automatic (as soon as the text reaches the right border of the cell) or explicit (via the \n character). As many cells as necessary are output, one below the other.
Text can be aligned, centered or justified. The cell block can be framed and the background painted.

### Parameters ###

w:
> Width of cells. If 0, they extend up to the right margin of the page.
h:
> Height of cells.
txt:
> String to print.
border:
> Indicates if borders must be drawn around the cell block. The value can be either a number:
    * 0: no border
    * 1: frame
> or a string containing some or all of the following characters (in any order):
    * L: left
    * T: top
    * R: right
    * B: bottom
> Default value: 0.
align:
> Sets the text alignment. Possible values are:
    * L: left alignment
    * C: center
    * R: right alignment
    * J: justification (default value)
fill
> Indicates if the cell background must be painted (true) or transparent (false). Default  value: false.

### See also ###

SetFont, SetDrawColor, SetFillColor, SetTextColor, SetLineWidth, [Cell](Cell.md), [Write](Write.md), SetAutoPageBreak.
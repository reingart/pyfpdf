## AddPage ##

```
fpdf.add_page(orientation='')
```

### Description ###

Adds a new page to the document. If a page is already present, the [Footer](Footer.md) method is called first to output the footer. Then the page is added, the current position set to the top-left corner according to the left and top margins, and Header() is called to display the header.
The font which was set before calling is automatically restored. There is no need to call SetFont again if you want to continue with the same font. The same is true for colors and line width.
The origin of the coordinate system is at the top-left corner and increasing ordinates go downwards.

### Parameters ###

orientation:
> Page orientation. Possible values are (case insensitive):
    * P or Portrait
    * L or Landscape
> The default value is the one passed to the constructor.

format:
> Page format. It can be either one of the following values (case insensitive):
    * A3
    * A4
    * A5
    * Letter
    * Legal
> or an array containing the width and the height (expressed in user unit).
> The default value is the one passed to the constructor.

### See also ###

[FPDF](FPDF.md), [Header](Header.md), [Footer](Footer.md), SetMargins.
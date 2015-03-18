## SetDrawColor ##

```
fpdf.set_draw_color(r:int, [g: int, b:int])
```

### Description ###

Defines the color used for all drawing operations (lines, rectangles and cell borders). It can be expressed in RGB components or gray scale. The method can be called before the first page is created and the value is retained from page to page.

### Parameters ###

r:
> If g et b are given, red component; if not, indicates the gray level. Value between 0 and 255.
g:
> Green component (between 0 and 255).
b:
> Blue component (between 0 and 255).

### See also ###

SetFillColor, SetTextColor, [Line](Line.md), [Rect](Rect.md), [Cell](Cell.md), MultiCell.
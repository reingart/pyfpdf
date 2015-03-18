## SetFillColor ##

```
fpdf.set_fill_color(r:int [, g:int, b:int])
```

### Description ###

Defines the color used for all filling operations (filled rectangles and cell backgrounds). It can be expressed in RGB components or gray scale. The method can be called before the first page is created and the value is retained from page to page.

### Parameters ###

r:
> If g and b are given, red component; if not, indicates the gray level. Value between 0 and 255.
g:
> Green component (between 0 and 255).
b:
> Blue component (between 0 and 255).

### See also ###

SetDrawColor, SetTextColor, [Rect](Rect.md), [Cell](Cell.md), MultiCell.
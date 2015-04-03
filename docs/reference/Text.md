## text ##

```python
fpdf.text(x: float, y: float, txt: str)
```
### Description ###

Prints a character string. The origin is on the left of the first character, on the baseline. This method allows to place a string precisely on the page, but it is usually easier to use [cell](Cell.md), [multi_cell](MultiCell.md) or [write](Write.md) which are the standard methods to print text.

### Parameters ###

x:
> Abscissa of the origin.

y:
> Ordinate of the origin.

txt:
> String to print.

### See also ###

[set_font](SetFont.md), [set_text_color](SetTextColor.md), [cell](Cell.md), [multi_cell](MultiCell.md), [write](Write.md).

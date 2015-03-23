## Text ##

```python
fpdf.text(x: float, y: float, txt : str)
```
### Description ###

Prints a character string. The origin is on the left of the first character, on the baseline. This method allows to place a string precisely on the page, but it is usually easier to use [Cell](Cell.md), [MultiCell](MultiCell.md) or [Write](Write.md) which are the standard methods to print text.

### Parameters ###

x:
> Abscissa of the origin.

y:
> Ordinate of the origin.

txt:
> String to print.

### See also ###

[SetFont](SetFont.md), [SetTextColor](SetTextColor.md), [Cell](Cell.md), [MultiCell](MultiCell.md), [Write](Write.md).

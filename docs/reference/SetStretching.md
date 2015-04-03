## SetStretching ##

```python
fpdf.set_stretching(stretching: float)
```

### Description ###

Sets horizontal font stretching. By default, if this method is not called, no stretching is set (equivalent to a value of 100).

### Version ###

Since 1.7.3

### Parameters ###

stretching:
> Define horizontal stretching (scaling) in percents.

### Example ###

```python
# Arial regular 14
pdf.set_font('Arial')
# Set stretching to 50%, narrow text
pdf.set_stretching(50.0)
```

### See also ###

[SetFont](SetFont.md), [SetFontSize](SetFontSize.md), [GetStringWidth](GetStringWidth.md).

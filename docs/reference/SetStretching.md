## SetStretching ##

```python
fpdf.set_stretching(stretching: float = 100.0)
```

### Description ###

Sets horizontal font stretching. 

### Version ###

Since 1.7.3

### Parameters ###

stretching:
> Define horizontal stretching (scaling) in percents. Default value 100 (i.e. no stretching).

### Example ###

```python
# Arial regular 14
pdf.set_font('Arial')
# Set stretching to 50%, narrow text
pdf.set_stretching(50.0)
```

### See also ###

[SetFont](SetFont.md), [SetFontSize](SetFontSize.md), [GetStringWidth](GetStringWidth.md).

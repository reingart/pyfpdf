## SetStretching ##

```
fpdf.set_stretching(stretching=100)
```

### Description ###

Sets the font stretching. Default value 100 (i.e. no stretching).

**Note**: This function introduced in 1.7.2 development version.

### Parameters ###

stretcing:

### Example ###

```
# Arial regular 14
pdf.set_font('Arial')
# Set stretching to 50%, narrow text
pdf.set_stretching(50.0)
```

### See also ###

SetFont, SetFontSize.
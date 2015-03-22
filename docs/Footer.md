## Footer ##

```
fpdf.footer()
```

### Description ###

This method is used to render the page footer. It is automatically called by AddPage and [Close](Close.md) and should not be called directly by the application. The implementation in FPDF is empty, so you have to subclass it and override the method if you want a specific processing.

### Example ###
```
class PDF(FPDF):
  def footer(this):
    # Go to 1.5 cm from bottom
    this.set_y(-15)
    # Select Arial italic 8
    this.set_font('Arial','I',8)
    # Print centered page number
    this.cell(0,10,'Page %s' % this.PageNo(),0,0,'C')
```

### See also ###

Header.
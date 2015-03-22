## AliasNbPages ##

fpdf.alias\_nb\_pages()

### Description ###

Defines an alias for the total number of pages. It will be substituted as the document is closed.

### Parameters ###

alias:
> The alias. Default value: {nb}.

### Example ###
```
class PDF(FPDF):
  def footer(this):
    # Go to 1.5 cm from bottom
    this.set_y(-15)
    # Select Arial italic 8
    this.set_font('Arial','I',8)
    # Print current and total page numbers
    this.cell(0,10,'Page %s' % this.PageNo() + '/{nb}',0,0,'C')

pdf=PDF()
pdf.alias_nb_pages()

```

### See also ###

PageNo, [Footer](Footer.md).
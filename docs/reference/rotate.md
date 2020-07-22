## rotate ##

```python
rotate(angle: float, x = None, y = None)
```

### DEPRECATED ###

This method is **deprecated** because it can produce malformed PDFs.

Example of code generating an invalid PDF:
```python
pdf = fpdf.FPDF()
pdf.add_page()
pdf.rotate(90)
pdf.image("lena.gif")
# Not calling pdf.angle(0) before switching to a new page causes the issue
pdf.add_page()
pdf.rotate(90)
pdf.image("lena.gif")
pdf.output("out.pdf")
```

Use the [rotation()](rotation.md) context manager instead.

## interleaved2of5 ##

```python
fpdf.interleaved2of5(txt: str, x: float, y: float, w=1.0, h=10.0)
```

### Description ###

Add a new barcode following Interleaved 2 of 5 schema.

### Parameters ###

txt:
> The text to be represented by the barcode.
> Method accepts string containing only digits. Take a note, 'A' and 'Z' are
also accepted (do not couse an error), but they lead to generate incorrect
barcodes as those characters are used to escape barcode.

x:
> Abscissa of upper-left barcode.

y:
> Ordinate of upper-left barcode.

w:
> Width of rectangles the barcode is built on. For example `0` is represented
by `nnwwn` where 'w' is a rectangle with width equals to `w` and 'n' is equal to
`w/3`

h:
> Height of the barcode


### See also ###

[code39](code39.md)

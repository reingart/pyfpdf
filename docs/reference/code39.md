## code39 ##

```python
fpdf.code39(txt: str, x: float, y: float, w=1.5, h=5.0)
```

### Description ###

Add a new barcode following C39 schema.

### Parameters ###

txt:
> The text to be represented by the barcode.
> Method accepts characters from following list: `'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. $/+%'`.
To be more precise, it's equal to following expression:
`string.digits + string.ascii_uppercase + '-. $/+%'`,. Take a not, method also
accepts `'*'`, but this character is used to escape barcode text and shouldn't be used
to code text.

x:
> Abscissa of upper-left barcode.

y:
> Ordinate of upper-left barcode.

w:
> Width of rectangles the barcode is built on. For example `0` is represented
by `nnnwwnwnn` where 'w' is a rectangle with width equals to `w` and 'n' is equal to
`w/3`

h:
> Height of the barcode


### See also ###

[interleaved2of5](interleaved2of5.md)

## rect_clip ##

```python
with pdf.rect_clip(x=..., y=..., w=..., h=...):
    pdf.image(filepath, x, y)
```

### Description ###

Performs image clipping, using the `W` operator.

### Parameters ###

x:
> Abscissa of upper-left corner.

y:
> Ordinate of upper-left corner.

w:
> Width.

h:
> Height.

### See also ###

[image](image.md), [rect](rect.md).

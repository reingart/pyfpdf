## Link ##

```
fpdf.link(float x, float y, float w, float h, mixed link)
```

### Description ###

Puts a link on a rectangular area of the page. Text or image links are generally put via Cell(), Write() or Image(), but this method can be useful for instance to define a clickable area inside an image.

### Parameters ###

x:
> Abscissa of the upper-left corner of the rectangle.
y:
> Ordinate of the upper-left corner of the rectangle.
w:
> Width of the rectangle.
h:
> Height of the rectangle.
link:
> URL or identifier returned by AddLink().

### See also ###

AddLink, [Cell](Cell.md), [Write](Write.md), [Image](Image.md).

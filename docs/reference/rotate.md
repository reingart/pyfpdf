## rotate ##

```python
rotate(angle: float, x = None, y = None)
```

### Description ###

This method allows to perform a rotation around a given center.

The rotation affects all elements which are printed after the method call 
(with the exception of clickable areas).

Remarks:

Only the display is altered. The get_x() and get_y() methods are not affected, 
nor the automatic page break mechanism. Rotation is not kept from page to page.
Each page begins with a null rotation. Note: this behaviour are subject to 
change.

### Parameters ###

angle: 
> Angle in degrees.

x:
> Abscissa of the rotation center. Default value: current position.

y:
> Ordinate of the rotation center. Default value: current position.

### Example ###
```python
pdf.set_font('Arial', '', 14)
pdf.add_page()
# Rotate all consequenced operations
pdf.rotate(-30)
pdf.write(5, "Rotated")
pdf.write(5, " text")
```

### See also ###

[set_x](set_x.md), [set_y](set_y.md), [write](write.md)


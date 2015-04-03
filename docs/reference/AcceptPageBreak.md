## accept_page_break ##

```python
fpdf.accept_page_break()
```

### Description ###

Whenever a page break condition is met, the method is called, and the break is issued or not depending on the returned value. The default implementation returns a value according to the mode selected by [set_auto_page_break](SetAutoPageBreak.md). 
This method is called automatically and should not be called directly by the application.

### See also ###

[set_auto_page_break](SetAutoPageBreak.md).

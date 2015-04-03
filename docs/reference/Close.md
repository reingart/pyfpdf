## close ##

```python
fpdf.close()
```

### Description ###

Terminates the PDF document. It is not necessary to call this method explicitly because [output](Output.md) does it automatically. 
If the document contains no page, [add_page](AddPage.md) is called to prevent from getting an invalid document.


### See also ###

[open](Open.md), [output](Output.md).

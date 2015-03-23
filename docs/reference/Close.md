## Close ##

```python
fpdf.close()
```

### Description ###

Terminates the PDF document. It is not necessary to call this method explicitly because [Output](Output.md) does it automatically. 
If the document contains no page, [AddPage](AddPage.md) is called to prevent from getting an invalid document.


### See also ###

[Open](Open.md), [Output](Output.md).

## output ##

```python
fpdf.output(name = '', dest = '')
```

### Description ###

Send the document to some destination: standard output, a file or a byte string.

The method first calls [close](close.md) if necessary to terminate the document.

### Parameters ###

name:
> The name of the file. Only used when writing to a file.

dest:
> Destination to send the document. It can take one of the following values:
>>   * `I` or `D`: write the document to _sys.stdout_. This is the default if no file name is given.
>>   * `F`: save to a local file with the given name (may include a path). This is the default if a file name is given.
>>   * `S`: return the document as a byte string.

### See also ###

[close](close.md).

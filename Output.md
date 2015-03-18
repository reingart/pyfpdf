## Output ##

```
fpdf.output(name='',dest=''):
```

### Description ###

Send the document to a given destination: browser, file or string. In the case of browser, the plug-in may be used (if present) or a download ("Save as" dialog box) may be forced.

The method first calls Close() if necessary to terminate the document.

### Parameters ###

name:
> The name of the file. If not specified, the document will be sent to the browser (destination I) with the name doc.pdf.
dest:
> Destination where to send the document. It can take one of the following values:
    * I: send the file inline to the browser. The plug-in is used if available. The name given by name is used when one selects the "Save as" option on the link generating the PDF.
    * D: send to the browser and force a file download with the name given by name.
    * F: save to a local file with the name given by name (may include a path).
    * S: return the document as a string. name is ignored.

### See also ###

[Close](Close.md).
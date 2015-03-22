## SetAutoPageBreak ##

```
fpdf.set_auto_page_break(auto,margin=0)
```

### Description ###

Enables or disables the automatic page breaking mode. When enabling, the second parameter is the distance from the bottom of the page that defines the triggering limit. By default, the mode is on and the margin is 2 cm.

### Parameters ###

auto:
> Boolean indicating if mode should be on or off.
margin:
> Distance from the bottom of the page.

### See also ###

[Cell](Cell.md), MultiCell, AcceptPageBreak.
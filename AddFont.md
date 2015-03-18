## AddFont ##

```
fpdf.add_font(family, style='', fname='', uni=False)
```

### Description ###

Imports a TrueType, OpenType or Type1 font and makes it available.

**Warning:** For !Type1 and legacy fonts it is necessary to generate a font definition file first with the `MakeFont` utility. This feature is currently deprecated in favour to TrueType unicode font support (whose are automatically processed with the `ttfonts.py` included utility).

**Note**: the font source files must be accessible. They are searched successively in (if this constants are defined):
  * `FPDF_FONTPATH` (by default, `font` folder in the fpdf package directory)
  * `SYSTEM_TTFONTS` (i.e. `C:\WINDOWS\FONTS`)

If the file corresponding to the requested font is not found, the runtime exception _"TTF Font file not found: "_ is raised.

For more information, see [Unicode](Unicode.md) support page.

The method should be called before SetFont method is used, and the font will be available for the whole document.

**Note**: due font processing can occupy large amount of time some data are cached.
Files created in same folder by default. This can be changed by `FPDF_CACHE_MODE` constant:
  * 0 - (by default), store cache in the same folder as font file
  * 1 - disable caching at all
  * 2 - store cache files in `FPDF_CACHE_DIR` directory with cryptic names

### Parameters ###

family:
> Family font. Used as a reference for SetFont, for example: `'dejavu'`

style:
> Font style. Deprecated, maintained only for backward compatibility.

fname:
> Font file name (i.e. `'DejaVuSansCondensed.ttf'`). You can specify a full path, if not, the file will be searched in `FPDF_FONTPATH` or `SYSTEM_TTFONTS`

uni:
> TTF Unicode flag (if set to `True`, TrueType font subset embedding will be enabled and text will be treated as `utf8` by default).

You must _not call_ AddFont for PDF Standard Latin-1 fonts (Courier, Helvetica, Times, Symbol, Zapfdingbats), use SetFont directly in that case.

Calling this method with uni=False is discouraged as legacy font support is complex and deprecated.


### Example ###

```
# Add a Unicode free font
pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)

# Add a Unicode system font (using full path)
pdf.add_font('sysfont', '', r"c:\WINDOWS\Fonts\arial.ttf", uni=True)
```

### See also ###

SetFont, SetFontSize, [Cell](Cell.md), MultiCell, [Write](Write.md).
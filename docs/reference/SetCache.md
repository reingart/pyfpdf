## SetCache ##

```python
fpdf.set_cache(cache)
```

### Description ###

This method change caching mechanism for current fpdf class instance.
If this method not called before [AddFont](AddFont.md) cached files are
created in same folder with fonts.

**Note**: Prior to version `1.7.2` caching behaviour can be changed 
by `FPDF_CACHE_MODE` constant:

  * 0 - (by default), store cache in the same folder as font file
  * 1 - disable caching at all
  * 2 - store cache files in `FPDF_CACHE_DIR` directory with cryptic names

### Parameters ###

cache:
>> * str instance - path to cache folder
>> * cache instance - caching class (see Builtin cache classes)

### Builtin cache classes ###

#### NoneCache ####

This class are base for all other classes.

 * `cache_for(fname, ext = ".pkl")` - return full name of cache file, with
   specified extension, or None if not applicable

#### StdCache ####

This is default class instanted with fpdf library by default and applied to all
instances of FPDF class.

 * `load_cache(filename, ttf = None)` - load cached data, with optional check 
    TTF filename
 * `save_cache(filename, data, ttf = None)` - save cached data, with optional
    TTF filename

#### HashCache ####

This class can be used to store all cache in one folder, where full font path 
encoded as hash. Instantiated when `cache` parameter is `str`.

### Example ###

For complex example refer to `tests/cover/test_cache_cls.py`.

```python
pdf = FPDF('P', 'mm', (100, 150))
# disable cache
pdf.set_cache(NoneCache())
# add font, no .pkl files
pdf.add_font('DejaVu', '', "./fonts/DejaVuSans.ttf", uni = True) 
```

### See also ###

[AddFont](AddFont.md), [SetFont](SetFont.md).

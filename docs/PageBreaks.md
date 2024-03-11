# Page breaks #

By default, `fpdf2` will automatically perform page breaks whenever a cell or
the text from a `write()` is rendered at the bottom of a page with a height
greater than the page bottom margin.

This behaviour can be controlled using the
[`set_auto_page_break`](fpdf/fpdf.html#fpdf.fpdf.FPDF.set_auto_page_break)
and
[`accept_page_break`](fpdf/fpdf.html#fpdf.fpdf.FPDF.accept_page_break)
methods.


## Manually trigger a page break ##

Simply call `.add_page()`.


## Inserting the final number of pages of the document ##

The special string `{nb}` will be substituted by the total number of pages on document closure.
This special value can changed by calling [alias_nb_pages()](fpdf/fpdf.html#fpdf.fpdf.FPDF.alias_nb_pages).

## will_page_break ##

`will_page_break(height)` lets you know if adding an element will trigger a page break,
based on its `height` and the current ordinate (`y` position).


## Unbreakable sections ##

In order to render content, like [tables](Tables.md),
with the insurance that no page break will be performed in it,
on the can use the `FPDF.unbreakable()` context-manager:

```python
pdf = fpdf.FPDF()
pdf.add_page()
pdf.set_font("Times", size=16)
line_height = pdf.font_size * 2
col_width = pdf.epw / 4  # distribute content evenly
for i in range(4):  # repeat table 4 times
    with pdf.unbreakable() as doc:
        for row in data:  # data comes from snippets on the Tables documentation page
            for datum in row:
                doc.cell(col_width, line_height, f"{datum} ({i})", border=1)
            doc.ln(line_height)
    print('page_break_triggered:', doc.page_break_triggered)
    pdf.ln(line_height * 2)
pdf.output("unbreakable_tables.pdf")
```

An alternative approach is [`offset_rendering()`](fpdf/fpdf.html#fpdf.fpdf.FPDF.offset_rendering)
that allows to test the results of some operations on the global layout
before performing them "for real":

```python
with pdf.offset_rendering() as dummy:
    # Dummy rendering:
    dummy.multi_cell(...)
if dummy.page_break_triggered:
    # We trigger a page break manually beforehand:
    pdf.add_page()
    # We duplicate the section header:
    pdf.cell(text="Appendix C")
# Now performing our rendering for real:
pdf.multi_cell(...)
```
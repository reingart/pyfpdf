# Annotations #

The PDF format allows to add various annotations to a document.


## Text annotations ##

They are rendered this way by Sumatra PDF reader:

![Screenshot of text annotation rendered by Sumatra PDF reader](text-annotation.png)

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=24)
pdf.text(x=60, y=140, text="Some text.")
pdf.text_annotation(
    x=100,
    y=130,
    text="This is a text annotation.",
)
pdf.output("text_annotation.pdf")
```

Method documentation: [`FPDF.text_annotation`](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.text_annotation)

## Free Text Annotations

They are rendered this way by Adobe Acrobat Reader:

![Screenshot of text annotation rendered by Adobe Acrobat Reader](free-text-annotation.png)

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica",size=24)
pdf.text(x=60, y=140, text="Some text.")
pdf.set_draw_color(255,0,0)
pdf.set_font_size(12)
pdf.free_text_annotation(
    x=100,
    y=130,
    text="This is a free text annotation.",
    w=150,
    h=15,
)
pdf.output("free_text_annotation.pdf")
```
Method documentation: [`FPDF.free_text_annotation`](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.free_text_annotation)


## Highlights ##

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=24)
with pdf.highlight("Highlight comment"):
    pdf.text(50, 50, "Line 1")
    pdf.set_y(50)
    pdf.multi_cell(w=30, text="Line 2")
pdf.cell(w=60, text="Not highlighted", border=1)
pdf.output("highlighted.pdf")
```

Rendering by Sumatra PDF reader:
![Screenshot of highlight annotation rendered by Sumatra PDF reader](highlighted.png)

Method documentation: [`FPDF.highlight`](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.highlight)

The appearance of the "highlight effect" can be controlled through the `type` argument:
it can be `Highlight` (default), `Underline`, `Squiggly` or `StrikeOut`.


## Ink annotations ##

Those annotations allow to draw paths around parts of a document to highlight them:
```python
from fpdf import FPDF

pdf = FPDF()
pdf.ink_annotation([(100, 200), (200, 100), (300, 200), (200, 300), (100, 200)],
                   title="Lucas", contents="Hello world!")
pdf.output("ink_annotation_demo.pdf")
```

Rendering by Firefox internal PDF viewer:
![Screenshot of ink annotation rendered by Firefox](ink_annotation.png)

Method documentation: [`FPDF.ink_annotation`](https://py-pdf.github.io/fpdf2/fpdf/fpdf.html#fpdf.fpdf.FPDF.ink_annotation)


## File attachments ##

_cf._ the dedicated page: [File attachments](FileAttachments.md)


## Named actions ##

The four standard PDF named actions provide some basic navigation relative to the current page:
`NextPage`, `PrevPage`, `FirstPage` and `LastPage`.

```python
from fpdf import FPDF
from fpdf.actions import NamedAction

pdf = FPDF()
pdf.set_font("Helvetica", size=24)
pdf.add_page()
pdf.text(x=80, y=140, text="First page")
pdf.add_page()
pdf.underline = True
for x, y, named_action in ((40, 80, "NextPage"), (120, 80, "PrevPage"), (40, 200, "FirstPage"), (120, 200, "LastPage")):
    pdf.text(x=x, y=y, text=named_action)
    pdf.add_action(
        NamedAction(named_action),
        x=x,
        y=y - pdf.font_size,
        w=pdf.get_string_width(named_action),
        h=pdf.font_size,
    )
pdf.underline = False
pdf.add_page()
pdf.text(x=80, y=140, text="Last page")
pdf.output("named_actions.pdf")
```


## Launch actions ##

Used to launch an application or open or print a document:

```python
from fpdf import FPDF
from fpdf.actions import LaunchAction

pdf = FPDF()
pdf.set_font("Helvetica", size=24)
pdf.add_page()
x, y, text = 80, 140, "Launch action"
pdf.text(x=x, y=y, text=text)
pdf.add_action(
    LaunchAction("another_file_in_same_directory.pdf"),
    x=x,
    y=y - pdf.font_size,
    w=pdf.get_string_width(text),
    h=pdf.font_size,
)
pdf.output("launch_action.pdf")
```

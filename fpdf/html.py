"""
HTML renderer

The contents of this module are internal to fpdf2, and not part of the public API.
They may change at any time without prior warning or any deprecation period,
in non-backward-compatible ways.
"""

from html.parser import HTMLParser
from string import ascii_lowercase, ascii_uppercase
import logging, re, warnings

from .deprecation import get_stack_level
from .drawing import color_from_hex_string, convert_to_device_color
from .enums import TextEmphasis, XPos, YPos
from .errors import FPDFException
from .fonts import FontFace
from .table import Table
from .util import int2roman

LOGGER = logging.getLogger(__name__)
BULLET_WIN1252 = "\x95"  # BULLET character in Windows-1252 encoding
DEGREE_WIN1252 = "\xb0"
HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")
DEFAULT_TAG_STYLES = {
    "a": FontFace(color=(0, 0, 255)),
    "blockquote": FontFace(color=(100, 0, 45)),
    "code": FontFace(family="Courier"),
    "h1": FontFace(color=(150, 0, 0), size_pt=24),
    "h2": FontFace(color=(150, 0, 0), size_pt=18),
    "h3": FontFace(color=(150, 0, 0), size_pt=14),
    "h4": FontFace(color=(150, 0, 0), size_pt=12),
    "h5": FontFace(color=(150, 0, 0), size_pt=10),
    "h6": FontFace(color=(150, 0, 0), size_pt=8),
    "pre": FontFace(family="Courier"),
}
DEFAULT_TAG_INDENTS = {
    "blockquote": 0,
    "dd": 10,
    "li": 5,
}

# Pattern to substitute whitespace sequences with a single space character each.
# The following are all Unicode characters with White_Space classification plus the newline.
# The pattern excludes the non-breaking spaces that are included in "\s".
# We also exclude the OGHAM SPACE MARK for now, because while being a word separator,
# it is usually a graphically visible glyph.
_WS_CHARS = "".join(
    (
        # "\u0009",  # CHARACTER TABULATION
        # "\u000a",  # LINE FEED
        # "\u000b",  # LINE TABULATION
        # "\u000c",  # FORM FEED
        # "\u000d",  # CARRIAGE RETURN
        "\u0009-\u000d",  # combine the above
        "\u0020",  # SPACE
        "\u0085",  # NEXT LINE
        # "\u00a0",  # NO-BREAK SPACE   (keep)
        # "\u1680",  # OGHAM SPACE MARK (not actually white)
        # "\u2000",  # EN QUAD
        # "\u2001",  # EM QUAD
        # "\u2002",  # EN SPACE
        # "\u2003",  # EM SPACE
        # "\u2004",  # THREE-PER-EM SPACE
        # "\u2005",  # FOUR-PER-EM SPACE
        # "\u2006",  # SIX-PER-EM SPACE
        # "\u2007",  # FIGURE SPACE
        # "\u2008",  # PUNCTUATION SPACE
        # "\u2009",  # THIN SPACE
        # "\u200a",  # HAIR SPACE
        "\u2000-\u200a",  # combine the above
        "\u2028",  # LINE SEPARATOR
        "\u2029",  # PARAGRAPH SEPARATOR
        # "\u202f",  # NARROW NO-BREAK SPACE (keep)
        "\u205f",  # MEDIUM MATHEMATICAL SPACE
        "\u3000",  # IDEOGRAPHIC SPACE
    )
)
_WS_SUB_PAT = re.compile(f"[{_WS_CHARS}]+")

COLOR_DICT = {
    "black": "#000000",
    "navy": "#000080",
    "darkblue": "#00008b",
    "mediumblue": "#0000cd",
    "blue": "#0000ff",
    "darkgreen": "#006400",
    "green": "#008000",
    "teal": "#008080",
    "darkcyan": "#008b8b",
    "deepskyblue": "#00bfff",
    "darkturquoise": "#00ced1",
    "mediumspringgreen": "#00fa9a",
    "lime": "#00ff00",
    "springgreen": "#00ff7f",
    "aqua": "#00ffff",
    "cyan": "#00ffff",
    "midnightblue": "#191970",
    "dodgerblue": "#1e90ff",
    "lightseagreen": "#20b2aa",
    "forestgreen": "#228b22",
    "seagreen": "#2e8b57",
    "darkslategray": "#2f4f4f",
    "darkslategrey": "#2f4f4f",
    "limegreen": "#32cd32",
    "mediumseagreen": "#3cb371",
    "turquoise": "#40e0d0",
    "royalblue": "#4169e1",
    "steelblue": "#4682b4",
    "darkslateblue": "#483d8b",
    "mediumturquoise": "#48d1cc",
    "indigo": "#4b0082",
    "darkolivegreen": "#556b2f",
    "cadetblue": "#5f9ea0",
    "cornflowerblue": "#6495ed",
    "rebeccapurple": "#663399",
    "mediumaquamarine": "#66cdaa",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "slateblue": "#6a5acd",
    "olivedrab": "#6b8e23",
    "slategray": "#708090",
    "slategrey": "#708090",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "mediumslateblue": "#7b68ee",
    "lawngreen": "#7cfc00",
    "chartreuse": "#7fff00",
    "aquamarine": "#7fffd4",
    "maroon": "#800000",
    "purple": "#800080",
    "olive": "#808000",
    "gray": "#808080",
    "grey": "#808080",
    "skyblue": "#87ceeb",
    "lightskyblue": "#87cefa",
    "blueviolet": "#8a2be2",
    "darkred": "#8b0000",
    "darkmagenta": "#8b008b",
    "saddlebrown": "#8b4513",
    "darkseagreen": "#8fbc8f",
    "lightgreen": "#90ee90",
    "mediumpurple": "#9370db",
    "darkviolet": "#9400d3",
    "palegreen": "#98fb98",
    "darkorchid": "#9932cc",
    "yellowgreen": "#9acd32",
    "sienna": "#a0522d",
    "brown": "#a52a2a",
    "darkgray": "#a9a9a9",
    "darkgrey": "#a9a9a9",
    "lightblue": "#add8e6",
    "greenyellow": "#adff2f",
    "paleturquoise": "#afeeee",
    "lightsteelblue": "#b0c4de",
    "powderblue": "#b0e0e6",
    "firebrick": "#b22222",
    "darkgoldenrod": "#b8860b",
    "mediumorchid": "#ba55d3",
    "rosybrown": "#bc8f8f",
    "darkkhaki": "#bdb76b",
    "silver": "#c0c0c0",
    "mediumvioletred": "#c71585",
    "indianred": "#cd5c5c",
    "peru": "#cd853f",
    "chocolate": "#d2691e",
    "tan": "#d2b48c",
    "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3",
    "thistle": "#d8bfd8",
    "orchid": "#da70d6",
    "goldenrod": "#daa520",
    "palevioletred": "#db7093",
    "crimson": "#dc143c",
    "gainsboro": "#dcdcdc",
    "plum": "#dda0dd",
    "burlywood": "#deb887",
    "lightcyan": "#e0ffff",
    "lavender": "#e6e6fa",
    "darksalmon": "#e9967a",
    "violet": "#ee82ee",
    "palegoldenrod": "#eee8aa",
    "lightcoral": "#f08080",
    "khaki": "#f0e68c",
    "aliceblue": "#f0f8ff",
    "honeydew": "#f0fff0",
    "azure": "#f0ffff",
    "sandybrown": "#f4a460",
    "wheat": "#f5deb3",
    "beige": "#f5f5dc",
    "whitesmoke": "#f5f5f5",
    "mintcream": "#f5fffa",
    "ghostwhite": "#f8f8ff",
    "salmon": "#fa8072",
    "antiquewhite": "#faebd7",
    "linen": "#faf0e6",
    "lightgoldenrodyellow": "#fafad2",
    "oldlace": "#fdf5e6",
    "red": "#ff0000",
    "fuchsia": "#ff00ff",
    "magenta": "#ff00ff",
    "deeppink": "#ff1493",
    "orangered": "#ff4500",
    "tomato": "#ff6347",
    "hotpink": "#ff69b4",
    "coral": "#ff7f50",
    "darkorange": "#ff8c00",
    "lightsalmon": "#ffa07a",
    "orange": "#ffa500",
    "lightpink": "#ffb6c1",
    "pink": "#ffc0cb",
    "gold": "#ffd700",
    "peachpuff": "#ffdab9",
    "navajowhite": "#ffdead",
    "moccasin": "#ffe4b5",
    "bisque": "#ffe4c4",
    "mistyrose": "#ffe4e1",
    "blanchedalmond": "#ffebcd",
    "papayawhip": "#ffefd5",
    "lavenderblush": "#fff0f5",
    "seashell": "#fff5ee",
    "cornsilk": "#fff8dc",
    "lemonchiffon": "#fffacd",
    "floralwhite": "#fffaf0",
    "snow": "#fffafa",
    "yellow": "#ffff00",
    "lightyellow": "#ffffe0",
    "ivory": "#fffff0",
    "white": "#ffffff",
}


def color_as_decimal(color="#000000"):
    if not color:
        return None

    # Checks if color is a name and gets the hex value
    hexcolor = COLOR_DICT.get(color.lower(), color)
    return color_from_hex_string(hexcolor).colors255


class HTML2FPDF(HTMLParser):
    "Render basic HTML to FPDF"

    HTML_UNCLOSED_TAGS = ("br", "dd", "dt", "hr", "img", "li", "td", "tr")

    def __init__(
        self,
        pdf,
        image_map=None,
        li_tag_indent=5,
        dd_tag_indent=10,
        table_line_separators=False,
        ul_bullet_char=BULLET_WIN1252,
        li_prefix_color=(190, 0, 0),
        heading_sizes=None,
        pre_code_font=DEFAULT_TAG_STYLES["pre"].family,
        warn_on_tags_not_matching=True,
        tag_indents=None,
        tag_styles=None,
        **_,
    ):
        """
        Args:
            pdf (FPDF): an instance of `fpdf.FPDF`
            image_map (function): an optional one-argument function that map <img> "src"
                to new image URLs
            li_tag_indent (int): [**DEPRECATED since v2.7.9**] numeric indentation of <li> elements - Set tag_indents instead
            dd_tag_indent (int): [**DEPRECATED since v2.7.9**] numeric indentation of <dd> elements - Set tag_indents instead
            table_line_separators (bool): enable horizontal line separators in <table>
            ul_bullet_char (str): bullet character preceding <li> items in <ul> lists.
            li_prefix_color (tuple | str | drawing.Device* instance): color for bullets or numbers preceding <li> tags.
                This applies to both <ul> & <ol> lists.
            heading_sizes (dict): [**DEPRECATED since v2.7.9**] font size per heading level names ("h1", "h2"...) - Set tag_styles instead
            pre_code_font (str): [**DEPRECATED since v2.7.9**] font to use for <pre> & <code> blocks - Set tag_styles instead
            warn_on_tags_not_matching (bool): control warnings production for unmatched HTML tags
            tag_indents (dict): mapping of HTML tag names to numeric values representing their horizontal left identation
            tag_styles (dict): mapping of HTML tag names to colors
        """
        super().__init__()
        self.pdf = pdf
        self.image_map = image_map or (lambda src: src)
        self.ul_bullet_char = ul_bullet_char
        self.li_prefix_color = (
            color_as_decimal(li_prefix_color)
            if isinstance(li_prefix_color, str)
            else convert_to_device_color(li_prefix_color).colors255
        )
        self.warn_on_tags_not_matching = warn_on_tags_not_matching

        # We operate in a local context and will only temporarily switch to the outer one for rendering.
        # This is necessary because of the deferred execution of text region writes. Changing fonts and
        # colors in here must not affect the output and/or interfere with the settings during rendering.
        # The TOC gets rendered outside of our scope, so we need to set a font first, in order to
        # ensure that the TOC has one available.
        # If a font was defined previously, we reinstate that seperately after we're finished here.
        # In this case the TOC will be rendered with that font and not ours. But adding a TOC tag only
        # makes sense if the whole document gets converted from HTML, so this should be acceptable.
        self.emphasis = dict(b=False, i=False, u=False)
        self.font_size = pdf.font_size_pt
        self.set_font(pdf.font_family or "times", size=self.font_size, set_default=True)
        self._prev_font = (pdf.font_family, self.font_size, self.emphasis)
        self.pdf._push_local_stack()  # xpylint: disable=protected-access

        self._pre_formatted = False  # preserve whitespace while True.
        self._pre_started = (
            False  # nothing written yet to <pre>, remove one initial nl.
        )
        self.follows_trailing_space = False  # The last write has ended with a space.
        self.follows_heading = False  # We don't want extra space below a heading.
        self.href = ""
        self.align = ""
        self.style_stack = []  # list of FontFace
        self.indent = 0
        self.ol_type = []  # when inside a <ol> tag, can be "a", "A", "i", "I" or "1"
        self.bullet = []
        self.font_color = pdf.text_color.colors255
        self.heading_level = None
        self.heading_above = 0.2  # extra space above heading, relative to font size
        self.heading_below = 0.4  # extra space below heading, relative to font size
        self._tags_stack = []
        self._column = self.pdf.text_columns(skip_leading_spaces=True)
        self._paragraph = self._column.paragraph()
        # <table>-related properties:
        self.table_line_separators = table_line_separators
        self.table = None  # becomes a Table instance when processing <table> tags
        self.table_row = None  # becomes a Row instance when processing <tr> tags
        self.tr = None  # becomes a dict of attributes when processing <tr> tags
        self.td_th = None  # becomes a dict of attributes when processing <td>/<th> tags
        #                    "inserted" is a special attribute indicating that a cell has be inserted in self.table_row

        if not tag_indents:
            tag_indents = {}
        if dd_tag_indent != DEFAULT_TAG_INDENTS["dd"]:
            warnings.warn(
                (
                    "The dd_tag_indent parameter is deprecated since v2.7.9 "
                    "and will be removed in a future release. "
                    "Set the `tag_indents` parameter instead."
                ),
                DeprecationWarning,
                stacklevel=get_stack_level(),
            )
            tag_indents["dd"] = dd_tag_indent
        if li_tag_indent != DEFAULT_TAG_INDENTS["li"]:
            warnings.warn(
                (
                    "The li_tag_indent parameter is deprecated since v2.7.9 "
                    "and will be removed in a future release. "
                    "Set the `tag_indents` parameter instead."
                ),
                DeprecationWarning,
                stacklevel=get_stack_level(),
            )
            tag_indents["li"] = li_tag_indent
        for tag in tag_indents:
            if tag not in DEFAULT_TAG_INDENTS:
                raise NotImplementedError(
                    f"Cannot set indent for HTML tag <{tag}> (contributions are welcome to add support for this)"
                )
        self.tag_indents = {**DEFAULT_TAG_INDENTS, **tag_indents}

        if not tag_styles:
            tag_styles = {}
        for tag in tag_styles:
            if tag not in DEFAULT_TAG_STYLES:
                raise NotImplementedError(
                    f"Cannot set style for HTML tag <{tag}> (contributions are welcome to add support for this)"
                )
        self.tag_styles = {**DEFAULT_TAG_STYLES, **tag_styles}
        if heading_sizes is not None:
            warnings.warn(
                (
                    "The heading_sizes parameter is deprecated since v2.7.9 "
                    "and will be removed in a future release. "
                    "Set the `tag_styles` parameter instead."
                ),
                DeprecationWarning,
                stacklevel=get_stack_level(),
            )
            for tag, size in heading_sizes.items():
                self.tag_styles[tag] = self.tag_styles[tag].replace(size_pt=size)
        if pre_code_font != DEFAULT_TAG_STYLES["pre"].family:
            warnings.warn(
                (
                    "The pre_code_font parameter is deprecated since v2.7.9 "
                    "and will be removed in a future release. "
                    "Set the `tag_styles` parameter instead."
                ),
                DeprecationWarning,
                stacklevel=get_stack_level(),
            )
            self.tag_styles["code"] = self.tag_styles["code"].replace(
                family=pre_code_font
            )
            self.tag_styles["pre"] = self.tag_styles["pre"].replace(
                family=pre_code_font
            )

    def _new_paragraph(
        self, align=None, line_height=1.0, top_margin=0, bottom_margin=0
    ):
        self._end_paragraph()
        self.align = align or ""
        if not top_margin and not self.follows_heading:
            top_margin = self.font_size / self.pdf.k
        self._paragraph = self._column.paragraph(
            text_align=align,
            line_height=line_height,
            skip_leading_spaces=True,
            top_margin=top_margin,
            bottom_margin=bottom_margin,
        )
        self.follows_trailing_space = True
        self.follows_heading = False

    def _end_paragraph(self):
        self.align = ""
        if self._paragraph:
            self._column.end_paragraph()
            our_context = (
                self.pdf._pop_local_stack()  # pylint: disable=protected-access
            )
            self._column.render()
            self.pdf._push_local_stack(our_context)  # pylint: disable=protected-access
            self._paragraph = None
            self.follows_trailing_space = True

    def _write_paragraph(self, text, link=None):
        if not self._paragraph:
            self._new_paragraph()
        self._paragraph.write(text, link=link)

    def _ln(self, h=None):
        if self._paragraph:
            self._paragraph.ln(h=h)
        else:
            self._column.ln(h=h)
        self.follows_trailing_space = True

    def handle_data(self, data):
        if self.td_th is not None:
            data = data.strip()
            if not data:
                return
            if "inserted" in self.td_th:
                td_th_tag = self.td_th["tag"]
                raise NotImplementedError(
                    f"Unsupported nested HTML tags inside <{td_th_tag}> element: <{self._tags_stack[-1]}>"
                )
                # We could potentially support nested <b> / <em> / <font> tags
                # by building a list of Fragment instances from the HTML cell content
                # and then passing those fragments to Row.cell().
                # However there should be an incoming refactoring of this code
                # dedicated to text layout, and we should probably wait for that
                # before supporting this feature.
            align = self.td_th.get("align", self.tr.get("align"))
            if align:
                align = align.upper()
            bgcolor = color_as_decimal(
                self.td_th.get("bgcolor", self.tr.get("bgcolor", None))
            )
            colspan = int(self.td_th.get("colspan", "1"))
            rowspan = int(self.td_th.get("rowspan", "1"))
            emphasis = 0
            if self.td_th.get("b"):
                emphasis |= TextEmphasis.B
            if self.td_th.get("i"):
                emphasis |= TextEmphasis.I
            if self.td_th.get("U"):
                emphasis |= TextEmphasis.U
            style = None
            if bgcolor or emphasis:
                style = FontFace(
                    emphasis=emphasis, fill_color=bgcolor, color=self.pdf.text_color
                )
            self.table_row.cell(
                text=data, align=align, style=style, colspan=colspan, rowspan=rowspan
            )
            self.td_th["inserted"] = True
        elif self.table is not None:
            # ignore anything else than td inside a table
            pass
        elif self._pre_formatted:  # pre blocks
            # If we want to mimick the exact HTML semantics about newlines at the
            # beginning and end of the block, then this needs some more thought.
            s_nl = data.startswith("\n") and self._pre_started
            self._pre_started = False
            e_nl = data.endswith("\n")
            if s_nl and e_nl:
                data = data[1:-1]
            elif s_nl:
                data = data[1:]
            # elif e_nl:
            #    data = data[:-1]
            self._write_data(data)
        else:
            data = _WS_SUB_PAT.sub(" ", data)
            if self.follows_trailing_space and data[0] == " ":
                self._write_data(data[1:])
            else:
                self._write_data(data)
            self.follows_trailing_space = data[-1] == " "

    def _write_data(self, data):
        if self.href:
            self.put_link(data)
        else:
            if self.heading_level:
                if self.pdf.section_title_styles:
                    raise NotImplementedError(
                        "Combining write_html() & section styles is currently not supported."
                        " You can open up an issue on github.com/py-pdf/fpdf2 if this is something you would like to see implemented."
                    )
                self.pdf.start_section(data, self.heading_level - 1, strict=False)
            LOGGER.debug(f"write: '%s' h={self.h:.2f}", data)
            self._write_paragraph(data)

    def handle_starttag(self, tag, attrs):
        self._pre_started = False
        attrs = dict(attrs)
        LOGGER.debug("STARTTAG %s %s", tag, attrs)
        self._tags_stack.append(tag)
        if tag == "dt":
            self._write_paragraph("\n")
            tag = "b"
        if tag == "dd":
            self._write_paragraph("\n" + "\u00a0" * self.tag_indents["dd"])
        if tag == "strong":
            tag = "b"
        if tag == "em":
            tag = "i"
        if tag in ("b", "i", "u"):
            if self.td_th is not None:
                self.td_th[tag] = True
            else:
                self.set_style(tag, True)
        if tag == "a":
            self.href = attrs["href"]
            try:
                page = int(self.href)
                self.href = self.pdf.add_link(page=page)
            except ValueError:
                pass
        if tag == "br":
            self._write_paragraph("\n")
        if tag == "p":
            align = None
            if "align" in attrs:
                align = attrs.get("align")[0].upper()
                if not align in ["L", "R", "J", "C"]:
                    align = None
            line_height = None
            if "line-height" in attrs:
                try:
                    # YYY parse and convert non-float line_height values
                    line_height = float(attrs.get("line-height"))
                except ValueError:
                    pass
            self._new_paragraph(align=align, line_height=line_height)
        if tag in HEADING_TAGS:
            prev_font_height = self.font_size / self.pdf.k
            self.style_stack.append(
                FontFace(
                    family=self.font_family,
                    size_pt=self.font_size,
                    color=self.font_color,
                )
            )
            self.heading_level = int(tag[1:])
            tag_style = self.tag_styles[tag]
            hsize = (tag_style.size_pt or self.font_size) / self.pdf.k
            if attrs:
                align = attrs.get("align")
                if not align in ["L", "R", "J", "C"]:
                    align = None
            else:
                align = None
            self._new_paragraph(
                align=align,
                top_margin=prev_font_height + self.heading_above * hsize,
                bottom_margin=self.heading_below * hsize,
            )
            color = None
            if "color" in attrs:
                color = color_as_decimal(attrs["color"])
            elif tag_style.color:
                color = tag_style.color.colors255
            if color:
                self.set_text_color(*color)
            self.set_font(
                family=tag_style.family or self.font_family,
                size=tag_style.size_pt or self.font_size,
            )
        if tag == "hr":
            self.pdf.add_page(same=True)
        if tag == "code":
            self.style_stack.append(
                FontFace(
                    family=self.font_family,
                    size_pt=self.font_size,
                    color=self.font_color,
                )
            )
            tag_style = self.tag_styles[tag]
            if tag_style.color:
                self.set_text_color(*tag_style.color.colors255)
            self.set_font(
                family=tag_style.family or self.font_family,
                size=tag_style.size_pt or self.font_size,
            )
        if tag == "pre":
            self.style_stack.append(
                FontFace(
                    family=self.font_family,
                    size_pt=self.font_size,
                    color=self.font_color,
                )
            )
            tag_style = self.tag_styles[tag]
            if tag_style.color:
                self.set_text_color(*tag_style.color.colors255)
            self.set_font(
                family=tag_style.family or self.font_family,
                size=tag_style.size_pt or self.font_size,
            )
            self._pre_formatted = True
            self._new_paragraph()
            self._pre_started = True
        if tag == "blockquote":
            tag_style = self.tag_styles[tag]
            if tag_style.color:
                self.set_text_color(*tag_style.color.colors255)
            self.set_font(
                family=tag_style.family or self.font_family,
                size=tag_style.size_pt or self.font_size,
            )
            self.indent += 1
            self._new_paragraph(top_margin=3, bottom_margin=3)
            if self.tag_indents["blockquote"]:
                self._write_paragraph("\u00a0" * self.tag_indents["blockquote"])
        if tag == "ul":
            self.indent += 1
            bullet_char = (
                ul_prefix(attrs["type"]) if "type" in attrs else self.ul_bullet_char
            )
            self.bullet.append(bullet_char)
            self._new_paragraph()
        if tag == "ol":
            self.indent += 1
            start = int(attrs["start"]) if "start" in attrs else 1
            self.bullet.append(start - 1)
            self.ol_type.append(attrs.get("type", "1"))
            self._new_paragraph()
        if tag == "li":
            self._ln(2)
            self.set_text_color(*self.li_prefix_color)
            if self.bullet:
                bullet = self.bullet[self.indent - 1]
            else:
                # Allow <li> to be used outside of <ul> or <ol>.
                bullet = self.ul_bullet_char
            if not isinstance(bullet, str):
                bullet += 1
                self.bullet[self.indent - 1] = bullet
                ol_type = self.ol_type[self.indent - 1]
                bullet = f"{ol_prefix(ol_type, bullet)}. "
            indent = "\u00a0" * self.tag_indents["li"] * self.indent
            self._write_paragraph(f"{indent}{bullet} ")
            self.set_text_color(*self.font_color)
        if tag == "font":
            # save previous font state:
            self.style_stack.append(
                FontFace(
                    family=self.font_family,
                    size_pt=self.font_size,
                    color=self.font_color,
                )
            )
            if "color" in attrs:
                color = color_as_decimal(attrs["color"])
                self.font_color = color
            if "face" in attrs:
                face = attrs.get("face").lower()
                # This may result in a FPDFException "font not found".
                self.set_font(face)
                self.font_family = face
            if "size" in attrs:
                self.font_size = int(attrs.get("size"))
            self.set_font()
            self.set_text_color(*self.font_color)
        if tag == "table":
            width = attrs.get("width")
            if width:
                if width[-1] == "%":
                    width = self.pdf.epw * int(width[:-1]) / 100
                else:
                    width = int(width) / self.pdf.k
            if "border" not in attrs:  # default borders
                borders_layout = (
                    "HORIZONTAL_LINES"
                    if self.table_line_separators
                    else "SINGLE_TOP_LINE"
                )
            elif int(attrs["border"]):  # explicitly enabled borders
                borders_layout = (
                    "ALL" if self.table_line_separators else "NO_HORIZONTAL_LINES"
                )
            else:  # explicitly disabled borders
                borders_layout = "NONE"
            align = attrs.get("align", "center").upper()
            padding = float(attrs["cellpadding"]) if "cellpadding" in attrs else None
            spacing = float(attrs.get("cellspacing", 0))
            self.table = Table(
                self.pdf,
                align=align,
                borders_layout=borders_layout,
                line_height=self.h * 1.30,
                width=width,
                padding=padding,
                gutter_width=spacing,
                gutter_height=spacing,
            )
            self._ln()
        if tag == "tr":
            if not self.table:
                raise FPDFException("Invalid HTML: <tr> used outside any <table>")
            self.tr = {k.lower(): v for k, v in attrs.items()}
            self.table_row = self.table.row()
        if tag in ("td", "th"):
            if not self.table_row:
                raise FPDFException(f"Invalid HTML: <{tag}> used outside any <tr>")
            self.td_th = {k.lower(): v for k, v in attrs.items()}
            self.td_th["tag"] = tag
            if tag == "th":
                if "align" not in self.td_th:
                    self.td_th["align"] = "CENTER"
                self.td_th["b"] = True
            elif len(self.table.rows) == 1 and not self.table_row.cells:
                # => we are in the 1st <tr>, and the 1st cell is a <td>
                # => we do not treat the first row as a header
                # pylint: disable=protected-access
                self.table._first_row_as_headings = False
                self.table._num_heading_rows = 0
            if "height" in attrs:
                LOGGER.warning(
                    'Ignoring unsupported height="%s" specified on a <%s>',
                    attrs["height"],
                    tag,
                )
            if "width" in attrs:
                width = attrs["width"]
                # pylint: disable=protected-access
                if len(self.table.rows) == 1:  # => first table row
                    if width[-1] == "%":
                        width = width[:-1]
                    if not self.table._col_widths:
                        self.table._col_widths = []
                    self.table._col_widths.append(int(width))
                else:
                    LOGGER.warning(
                        'Ignoring width="%s" specified on a <%s> that is not in the first <tr>',
                        width,
                        tag,
                    )
        if tag == "img" and "src" in attrs:
            width = int(attrs.get("width", 0)) / self.pdf.k
            height = int(attrs.get("height", 0)) / self.pdf.k
            if self.table_row:  # => <img> in a <table>
                if width or height:
                    LOGGER.warning(
                        'Ignoring unsupported "width" / "height" set on <img> element'
                    )
                if self.align:
                    LOGGER.warning("Ignoring unsupported <img> alignment")
                self.table_row.cell(img=attrs["src"], img_fill_width=True)
                self.td_th["inserted"] = True
                return
            if self.pdf.y + height > self.pdf.page_break_trigger:
                self.pdf.add_page(same=True)
            x, y = self.pdf.get_x(), self.pdf.get_y()
            if self.align and self.align[0].upper() == "C":
                x = self.pdf.w / 2 - width / 2
            LOGGER.debug(
                'image "%s" x=%d y=%d width=%d height=%d',
                attrs["src"],
                x,
                y,
                width,
                height,
            )
            info = self.pdf.image(
                self.image_map(attrs["src"]), x, y, width, height, link=self.href
            )
            self.pdf.set_y(y + info.rendered_height)
        if tag == "center":
            self._new_paragraph(align="C")
        if tag == "toc":
            self._end_paragraph()
            self.pdf.insert_toc_placeholder(
                self.render_toc, pages=int(attrs.get("pages", 1))
            )
        if tag == "sup":
            self.pdf.char_vpos = "SUP"
        if tag == "sub":
            self.pdf.char_vpos = "SUB"

    def handle_endtag(self, tag):
        LOGGER.debug("ENDTAG %s", tag)
        while (
            self._tags_stack
            and tag != self._tags_stack[-1]
            and self._tags_stack[-1] in self.HTML_UNCLOSED_TAGS
        ):
            self._tags_stack.pop()
        if not self._tags_stack:
            if self.warn_on_tags_not_matching:
                LOGGER.warning(
                    "Unexpected HTML end tag </%s>, start tag may be missing?", tag
                )
        elif tag == self._tags_stack[-1]:
            self._tags_stack.pop()
        elif self.warn_on_tags_not_matching:
            LOGGER.warning(
                "Unexpected HTML end tag </%s>, start tag was <%s>",
                tag,
                self._tags_stack[-1],
            )
        if tag in HEADING_TAGS:
            self.heading_level = None
            font_face = self.style_stack.pop()
            self.set_font(font_face.family, font_face.size_pt)
            self.set_text_color(*font_face.color.colors255)
            self._end_paragraph()
            self.follows_heading = True  # We don't want extra space below a heading.
        if tag == "code":
            font_face = self.style_stack.pop()
            self.set_font(font_face.family, font_face.size_pt)
            self.set_text_color(*font_face.color.colors255)
        if tag == "pre":
            self._end_paragraph()
            font_face = self.style_stack.pop()
            self.set_font(font_face.family, font_face.size_pt)
            self.set_text_color(*font_face.color.colors255)
            self._pre_formatted = False
            self._pre_started = False
        if tag == "blockquote":
            self._end_paragraph()
            self.set_text_color(*self.font_color)
            self.indent -= 1
        if tag in ("strong", "dt"):
            tag = "b"
        if tag == "em":
            tag = "i"
        if tag in ("b", "i", "u"):
            if not self.td_th is not None:
                self.set_style(tag, False)
        if tag == "a":
            self.href = ""
        if tag == "p":
            self._end_paragraph()
            self.align = ""
        if tag in ("ul", "ol"):
            self._end_paragraph()
            self.indent -= 1
            if tag == "ol":
                self.ol_type.pop()
            self.bullet.pop()
        if tag == "table":
            self.table.render()
            self.table = None
            self._ln(self.h)
        if tag == "tr":
            self.tr = None
            self.table_row = None
        if tag in ("td", "th"):
            if "inserted" not in self.td_th:
                # handle_data() was not called => we call it to produce an empty cell:
                bgcolor = color_as_decimal(
                    self.td_th.get("bgcolor", self.tr.get("bgcolor", None))
                )
                style = FontFace(fill_color=bgcolor) if bgcolor else None
                self.table_row.cell(text="", style=style)
            self.td_th = None
        if tag == "font":
            # recover last font state
            font_face = self.style_stack.pop()
            self.font_color = font_face.color.colors255
            self.set_font(font_face.family, font_face.size_pt)
            self.set_text_color(*font_face.color.colors255)
        if tag == "center":
            self._end_paragraph()
        if tag == "sup":
            self.pdf.char_vpos = "LINE"
        if tag == "sub":
            self.pdf.char_vpos = "LINE"

    def feed(self, data):
        super().feed(data)
        while self._tags_stack and self._tags_stack[-1] in self.HTML_UNCLOSED_TAGS:
            self._tags_stack.pop()
        self._end_paragraph()  # render the final chunk of text and clean up our local context.
        self.pdf._pop_local_stack()  # pylint: disable=protected-access
        if self._prev_font[0]:  # restore previously defined font settings
            self.emphasis = self._prev_font[2]
            self.set_font(self._prev_font[0], size=self._prev_font[1], set_default=True)
        if self._tags_stack and self.warn_on_tags_not_matching:
            LOGGER.warning("Missing HTML end tag for <%s>", self._tags_stack[-1])

    def set_font(self, family=None, size=None, set_default=False):
        if family:
            self.font_family = family
        if size:
            self.font_size = size
            self.h = size / self.pdf.k
        style = "".join(s for s in ("b", "i", "u") if self.emphasis.get(s)).upper()
        LOGGER.debug(f"set_font: %s style=%s h={self.h:.2f}", self.font_family, style)
        prev_page = self.pdf.page
        if not set_default:  # make sure there's at least one font defined in the PDF.
            self.pdf.page = 0
        if (self.font_family, style) != (self.pdf.font_family, self.pdf.font_style):
            self.pdf.set_font(self.font_family, style, self.font_size)
        if self.font_size != self.pdf.font_size:
            self.pdf.set_font_size(self.font_size)
        self.pdf.page = prev_page

    def set_style(self, tag=None, enable=False):
        # Modify style and select corresponding font
        if tag:
            self.emphasis[tag.lower()] = enable
        style = "".join(s for s in ("b", "i", "u") if self.emphasis.get(s))
        LOGGER.debug("SET_FONT_STYLE %s", style)
        prev_page = self.pdf.page
        self.pdf.page = 0
        self.pdf.set_font(style=style)
        self.pdf.page = prev_page

    def set_text_color(self, r=None, g=0, b=0):
        prev_page = self.pdf.page
        self.pdf.page = 0
        self.pdf.set_text_color(r, g, b)
        self.pdf.page = prev_page

    def put_link(self, text):
        # Put a hyperlink
        tag_style = self.tag_styles["a"]
        if tag_style.color:
            self.set_text_color(*tag_style.color.colors255)
        self.set_font(
            family=tag_style.family or self.font_family,
            size=tag_style.size_pt or self.font_size,
        )
        self.set_style("u", True)
        self._write_paragraph(text, link=self.href)
        self.set_style("u", False)
        self.set_text_color(*self.font_color)

    # pylint: disable=no-self-use
    def render_toc(self, pdf, outline):
        "This method can be overriden by subclasses to customize the Table of Contents style."
        pdf.ln()
        for section in outline:
            link = pdf.add_link(page=section.page_number)
            text = f'{" " * section.level * 2} {section.name}'
            text += f' {"." * (60 - section.level*2 - len(section.name))} {section.page_number}'
            pdf.multi_cell(
                w=pdf.epw,
                h=pdf.font_size,
                text=text,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                link=link,
            )

    # Subclasses of _markupbase.ParserBase must implement this:
    def error(self, message):
        raise RuntimeError(message)


def ul_prefix(ul_type):
    if ul_type == "circle":
        return DEGREE_WIN1252
    if ul_type == "disc":
        return BULLET_WIN1252
    if len(ul_type) == 1:
        return ul_type
    raise NotImplementedError(f"Unsupported type: {ul_type}")


def ol_prefix(ol_type, index):
    if ol_type == "1":
        return index
    if ol_type == "a":
        return ascii_lowercase[index - 1]
    if ol_type == "A":
        return ascii_uppercase[index - 1]
    if ol_type == "I":
        return int2roman(index)
    if ol_type == "i":
        return int2roman(index).lower()
    raise NotImplementedError(f"Unsupported type: {ol_type}")


class HTMLMixin:
    """
    [**DEPRECATED since v2.6.0**]
    You can now directly use the `FPDF.write_html()` method
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(
            (
                "The HTMLMixin class is deprecated since v2.6.0. "
                "Simply use the FPDF class as a replacement."
            ),
            DeprecationWarning,
            stacklevel=get_stack_level(),
        )

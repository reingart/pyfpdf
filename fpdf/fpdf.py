# ****************************************************************************
# * Software: FPDF for python                                                *
# * License:  LGPL v3.0+                                                     *
# *                                                                          *
# * Original Author (PHP):  Olivier PLATHEY 2004-12-31                       *
# * Ported to Python 2.4 by Max (maxpat78@yahoo.it) on 2006-05               *
# * Maintainer:  Mariano Reingart (reingart@gmail.com) et al since 2008 est. *
# * Maintainer:  David Alexander (daveankin@gmail.com) et al since 2017 est. *
# * Maintainer:  Lucas Cimon et al since 2021 est.                           *
# ****************************************************************************
import hashlib, io, logging, math, os, re, sys, warnings
from collections import defaultdict
from collections.abc import Sequence
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
from html import unescape
from math import isclose
from numbers import Number
from os.path import splitext
from pathlib import Path
from typing import Callable, NamedTuple, Optional, Union

try:
    from endesive import signer
    from cryptography.hazmat.primitives.serialization import pkcs12
except ImportError:
    pkcs12, signer = None, None

try:
    from PIL.Image import Image
except ImportError:
    warnings.warn(
        "Pillow could not be imported - fpdf2 will not be able to add any image"
    )

    class Image:
        # The class must exist for some isinstance checks below
        pass


from . import drawing
from .actions import URIAction
from .annotations import (
    AnnotationDict,
    PDFAnnotation,
    PDFEmbeddedFile,
    DEFAULT_ANNOT_FLAGS,
)
from .deprecation import WarnOnDeprecatedModuleAttributes
from .encryption import StandardSecurityHandler
from .enums import (
    AccessPermission,
    Align,
    Angle,
    AnnotationFlag,
    AnnotationName,
    CharVPos,
    Corner,
    EncryptionMethod,
    FileAttachmentAnnotationName,
    MethodReturnValue,
    PageLayout,
    PageMode,
    PathPaintRule,
    RenderStyle,
    TextEmphasis,
    TextMarkupType,
    TextMode,
    WrapMode,
    XPos,
    YPos,
)
from .errors import FPDFException, FPDFPageFormatException, FPDFUnicodeEncodingException
from .fonts import CoreFont, CORE_FONTS, FontFace, TTFFont
from .graphics_state import GraphicsStateMixin
from .html import HTML2FPDF
from .image_parsing import SUPPORTED_IMAGE_FILTERS, get_img_info, load_image
from .line_break import Fragment, MultiLineBreak, TextLine
from .linearization import LinearizedOutputProducer
from .output import OutputProducer, PDFPage, ZOOM_CONFIGS
from .outline import OutlineSection
from .recorder import FPDFRecorder
from .structure_tree import StructureTreeBuilder
from .sign import Signature
from .svg import Percent, SVGObject
from .syntax import DestinationXYZ, PDFDate
from .table import Table
from .util import (
    escape_parens,
    get_scale_factor,
)

# Public global variables:
FPDF_VERSION = "2.7.4"
PAGE_FORMATS = {
    "a3": (841.89, 1190.55),
    "a4": (595.28, 841.89),
    "a5": (420.94, 595.28),
    "letter": (612, 792),
    "legal": (612, 1008),
}
"Supported page format names & dimensions"

# Private global variables:
LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
FPDF_FONT_DIR = HERE / "font"
LAYOUT_ALIASES = {
    "default": None,
    "single": PageLayout.SINGLE_PAGE,
    "continuous": PageLayout.ONE_COLUMN,
    "two": PageLayout.TWO_COLUMN_LEFT,
}


class ImageInfo(dict):
    "Information about a raster image used in the PDF document"

    @property
    def width(self):
        "Intrinsic image width"
        return self["w"]

    @property
    def height(self):
        "Intrinsic image height"
        return self["h"]

    @property
    def rendered_width(self):
        "Only available if the image has been placed on the document"
        return self["rendered_width"]

    @property
    def rendered_height(self):
        "Only available if the image has been placed on the document"
        return self["rendered_height"]

    def __str__(self):
        d = {k: ("..." if k in ("data", "smask") else v) for k, v in self.items()}
        return f"ImageInfo({d})"


class TitleStyle(FontFace):
    def __init__(
        self,
        font_family: Optional[str] = None,
        font_style: Optional[str] = None,
        font_size_pt: Optional[int] = None,
        color: Union[int, tuple] = None,  # grey scale or (red, green, blue),
        underline: bool = False,
        t_margin: Optional[int] = None,
        l_margin: Optional[int] = None,
        b_margin: Optional[int] = None,
    ):
        super().__init__(
            font_family,
            (font_style or "") + ("U" if underline else ""),
            font_size_pt,
            color,
        )
        self.t_margin = t_margin
        self.l_margin = l_margin
        self.b_margin = b_margin


class ToCPlaceholder(NamedTuple):
    render_function: Callable
    start_page: int
    y: int
    pages: int = 1


# Disabling this check due to the "format" parameter below:
# pylint: disable=redefined-builtin
def get_page_format(format, k=None):
    """Return page width and height size in points.

    Throws FPDFPageFormatException

    `format` can be either a 2-tuple or one of 'a3', 'a4', 'a5', 'letter', or
    'legal'.

    If format is a tuple, then the return value is the tuple's values
    given in the units specified on this document in the constructor,
    multiplied by the corresponding scale factor `k`, taken from instance
    variable `self.k`.

    If format is a string, the (width, height) tuple returned is in points.
    For a width and height of 8.5 * 11, 72 dpi is assumed, so the value
    returned is (8.5 * 72, 11 * 72), or (612, 792). Additional formats can be
    added by adding fields to the `PAGE_FORMATS` dictionary with a
    case insensitive key (the name of the new format) and 2-tuple value of
    (width, height) in dots per inch with a 72 dpi resolution.
    """
    if isinstance(format, str):
        format = format.lower()
        if format in PAGE_FORMATS:
            return PAGE_FORMATS[format]
        raise FPDFPageFormatException(format, unknown=True)

    if k is None:
        raise FPDFPageFormatException(format, one=True)

    try:
        return format[0] * k, format[1] * k
    except Exception as e:
        args = f"{format}, {k}"
        raise FPDFPageFormatException(f"Arguments must be numbers: {args}") from e


def check_page(fn):
    """Decorator to protect drawing methods"""

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if not self.page and not (kwargs.get("dry_run") or kwargs.get("split_only")):
            raise FPDFException("No page open, you need to call add_page() first")
        return fn(self, *args, **kwargs)

    return wrapper


class FPDF(GraphicsStateMixin):
    "PDF Generation class"
    MARKDOWN_BOLD_MARKER = "**"
    MARKDOWN_ITALICS_MARKER = "__"
    MARKDOWN_UNDERLINE_MARKER = "--"
    MARKDOWN_LINK_REGEX = re.compile(r"^\[([^][]+)\]\(([^()]+)\)(.*)$")
    MARKDOWN_LINK_COLOR = None

    HTML2FPDF_CLASS = HTML2FPDF

    def __init__(
        self,
        orientation="portrait",
        unit="mm",
        format="A4",
        font_cache_dir="DEPRECATED",
    ):
        """
        Args:
            orientation (str): possible values are "portrait" (can be abbreviated "P")
                or "landscape" (can be abbreviated "L"). Default to "portrait".
            unit (str, int, float): possible values are "pt", "mm", "cm", "in", or a number.
                A point equals 1/72 of an inch, that is to say about 0.35 mm (an inch being 2.54 cm).
                This is a very common unit in typography; font sizes are expressed in this unit.
                If given a number, then it will be treated as the number of points per unit.  (eg. 72 = 1 in)
                Default to "mm".
            format (str): possible values are "a3", "a4", "a5", "letter", "legal" or a tuple
                (width, height) expressed in the given unit. Default to "a4".
            font_cache_dir (Path or str): [**DEPRECATED since v2.5.1**] unused
        """
        if font_cache_dir != "DEPRECATED":
            warnings.warn(
                '"font_cache_dir" parameter is deprecated, unused and will soon be removed',
                DeprecationWarning,
                stacklevel=2,
            )
        super().__init__()
        self.page = 0  # current page number
        self.pages = {}  # array of PDFPage objects starting at index 1
        self.fonts = {}  # map font string keys to an instance of CoreFont or TTFFont
        self.images = {}  # map image identifiers to dicts describing the raster images
        self.icc_profiles = {}  # map icc profiles (bytes) to their index (number)
        self.links = {}  # array of Destination objects starting at index 1
        self.embedded_files = []  # array of PDFEmbeddedFile

        self.in_footer = False  # flag set while rendering footer
        # indicates that we are inside an .unbreakable() code block:
        self._in_unbreakable = False
        self._lasth = 0  # height of last cell printed
        self.str_alias_nb_pages = "{nb}"

        self._angle = 0  # used by deprecated method: rotate()
        self.xmp_metadata = None
        # Define the compression algorithm used when embedding images:
        self.image_filter = "AUTO"
        self.page_duration = 0  # optional pages display duration, cf. add_page()
        self.page_transition = None  # optional pages transition, cf. add_page()
        self.allow_images_transparency = True
        # Do nothing by default. Allowed values: 'WARN', 'DOWNSCALE':
        self.oversized_images = None
        self.oversized_images_ratio = 2  # number of pixels per UserSpace point
        self.struct_builder = StructureTreeBuilder()
        self._toc_placeholder = None  # optional ToCPlaceholder instance
        self._outline = []  # list of OutlineSection
        self._sign_key = None
        self.section_title_styles = {}  # level -> TitleStyle

        self.core_fonts_encoding = "latin-1"
        "Font encoding, Latin-1 by default"
        # Replace these fonts with these core fonts
        self.font_aliases = {
            "arial": "helvetica",
            "couriernew": "courier",
            "timesnewroman": "times",
        }
        # Scale factor
        self.k = get_scale_factor(unit)

        # Graphics state variables defined as properties by GraphicsStateMixin.
        # We set their default values here.
        self.font_family = ""  # current font family
        self.font_style = ""  # current font style
        self.font_size_pt = 12  # current font size in points
        self.font_stretching = 100  # current font stretching
        self.char_spacing = 0  # current character spacing
        self.underline = False  # underlining flag
        self.current_font = (
            None  # current font, None or an instance of CoreFont or TTFFont
        )
        self.draw_color = self.DEFAULT_DRAW_COLOR
        self.fill_color = self.DEFAULT_FILL_COLOR
        self.text_color = self.DEFAULT_TEXT_COLOR
        self.page_background = None
        self.dash_pattern = dict(dash=0, gap=0, phase=0)
        self.line_width = 0.567 / self.k  # line width (0.2 mm)
        self.text_mode = TextMode.FILL
        # end of grapics state variables

        self.dw_pt, self.dh_pt = get_page_format(format, self.k)
        self._set_orientation(orientation, self.dw_pt, self.dh_pt)
        self.def_orientation = self.cur_orientation
        # Page spacing
        # Page margins (1 cm)
        margin = (7200 / 254) / self.k
        self.x, self.y, self.l_margin, self.t_margin = 0, 0, 0, 0
        self.set_margins(margin, margin)
        self.x, self.y = self.l_margin, self.t_margin
        self.c_margin = margin / 10.0  # Interior cell margin (1 mm)
        # sets self.auto_page_break, self.b_margin & self.page_break_trigger:
        self.set_auto_page_break(True, 2 * margin)
        self.set_display_mode("fullwidth")  # Full width display mode
        self._page_mode = None
        self.viewer_preferences = None  # optional instance of ViewerPreferences
        self.compress = True  # switch enabling pages content compression
        self.pdf_version = "1.3"  # Set default PDF version No.
        self.creation_date = datetime.now(timezone.utc)
        self._security_handler = None
        self._fallback_font_ids = []
        self._fallback_font_exact_match = False

        self._current_draw_context = None
        self._drawing_graphics_state_registry = drawing.GraphicsStateDictRegistry()

        self._record_text_quad_points = False

        # page number -> array of 8 × n numbers:
        self._text_quad_points = defaultdict(list)

        # final buffer holding the PDF document in-memory - defined only after calling output():
        self.buffer = None

    def set_encryption(
        self,
        owner_password,
        user_password=None,
        encryption_method=EncryptionMethod.RC4,
        permissions=AccessPermission.all(),
        encrypt_metadata=False,
    ):
        """ "
        Activate encryption of the document content.

        Args:
            owner_password (str): mandatory. The owner password allows to perform any change on the document,
                including removing all encryption and access permissions.
            user_password (str): optional. If a user password is set, the content of the document will be encrypted
                and a password prompt displayed when a user opens the document.
                The document will only be displayed after either the user or owner password is entered.
            encryption_method (fpdf.enums.EncryptionMethod, str): algorithm to be used to encrypt the document.
                Defaults to RC4.
            permissions (fpdf.enums.AccessPermission): specify access permissions granted
                when the document is opened with user access. Defaults to ALL.
            encrypt_metadata (bool): whether to also encrypt document metadata (author, creation date, etc.).
                Defaults to False.
        """
        self._security_handler = StandardSecurityHandler(
            self,
            owner_password=owner_password,
            user_password=user_password,
            permission=permissions,
            encryption_method=encryption_method,
            encrypt_metadata=encrypt_metadata,
        )

    def write_html(self, text, *args, **kwargs):
        """
        Parse HTML and convert it to PDF.
        cf. https://pyfpdf.github.io/fpdf2/HTML.html
        """
        kwargs2 = vars(self)
        # Method arguments must override class & instance attributes:
        kwargs2.update(kwargs)
        html2pdf = self.HTML2FPDF_CLASS(self, *args, **kwargs2)
        text = unescape(text)  # To deal with HTML entities
        html2pdf.feed(text)

    def _set_min_pdf_version(self, version):
        self.pdf_version = max(self.pdf_version, version)

    @property
    def is_ttf_font(self):
        return self.current_font and self.current_font.type == "TTF"

    @property
    def page_mode(self):
        return self._page_mode

    @page_mode.setter
    def page_mode(self, page_mode):
        self._page_mode = PageMode.coerce(page_mode)
        if self._page_mode == PageMode.USE_ATTACHMENTS:
            self._set_min_pdf_version("1.6")
        elif self._page_mode == PageMode.USE_OC:
            self._set_min_pdf_version("1.5")

    @property
    def epw(self):
        """
        Effective page width: the page width minus its horizontal margins.
        """
        return self.w - self.l_margin - self.r_margin

    @property
    def eph(self):
        """
        Effective page height: the page height minus its vertical margins.
        """
        return self.h - self.t_margin - self.b_margin

    @property
    def pages_count(self):
        """
        Returns the total pages of the document.
        """
        return len(self.pages)

    def set_margin(self, margin):
        """
        Sets the document right, left, top & bottom margins to the same value.

        Args:
            margin (float): margin in the unit specified to FPDF constructor
        """
        self.set_margins(margin, margin)
        self.set_auto_page_break(self.auto_page_break, margin)

    def set_margins(self, left, top, right=-1):
        """
        Sets the document left, top & optionaly right margins to the same value.
        By default, they equal 1 cm.
        Also sets the current FPDF.y on the page to this minimum vertical position.

        Args:
            left (float): left margin in the unit specified to FPDF constructor
            top (float): top margin in the unit specified to FPDF constructor
            right (float): optional right margin in the unit specified to FPDF constructor
        """
        self.set_left_margin(left)
        if self.y < top or self.y == self.t_margin:
            self.y = top
        self.t_margin = top
        if right == -1:
            right = left
        self.r_margin = right

    def set_left_margin(self, margin):
        """
        Sets the document left margin.
        Also sets the current FPDF.x on the page to this minimum horizontal position.

        Args:
            margin (float): margin in the unit specified to FPDF constructor
        """
        if self.x < margin or self.x == self.l_margin:
            self.x = margin
        self.l_margin = margin

    def set_top_margin(self, margin):
        """
        Sets the document top margin.

        Args:
            margin (float): margin in the unit specified to FPDF constructor
        """
        self.t_margin = margin

    def set_right_margin(self, margin):
        """
        Sets the document right margin.

        Args:
            margin (float): margin in the unit specified to FPDF constructor
        """
        self.r_margin = margin

    def set_auto_page_break(self, auto, margin=0):
        """
        Set auto page break mode and triggering bottom margin.
        By default, the mode is on and the bottom margin is 2 cm.

        Args:
            auto (bool): enable or disable this mode
            margin (float): optional bottom margin (distance from the bottom of the page)
                in the unit specified to FPDF constructor
        """
        self.auto_page_break = auto
        self.b_margin = margin
        self.page_break_trigger = self.h - self.b_margin

    @property
    def default_page_dimensions(self):
        "Return a pair (width, height) in the unit specified to FPDF constructor"
        return (
            (self.dw_pt, self.dh_pt)
            if self.def_orientation == "P"
            else (self.dh_pt, self.dw_pt)
        )

    def _set_orientation(self, orientation, page_width_pt, page_height_pt):
        orientation = orientation.lower()
        if orientation in ("p", "portrait"):
            self.cur_orientation = "P"
            self.w_pt = page_width_pt
            self.h_pt = page_height_pt
        elif orientation in ("l", "landscape"):
            self.cur_orientation = "L"
            self.w_pt = page_height_pt
            self.h_pt = page_width_pt
        else:
            raise FPDFException(f"Incorrect orientation: {orientation}")
        self.w = self.w_pt / self.k
        self.h = self.h_pt / self.k

    def set_display_mode(self, zoom, layout="continuous"):
        """
        Defines the way the document is to be displayed by the viewer.

        It allows to set the zoom level: pages can be displayed entirely on screen,
        occupy the full width of the window, use the real size,
        be scaled by a specific zooming factor or use the viewer default (configured in its Preferences menu).

        The page layout can also be specified: single page at a time, continuous display, two columns or viewer default.

        Args:
            zoom: either "fullpage", "fullwidth", "real", "default",
                or a number indicating the zooming factor to use, interpreted as a percentage.
                The zoom level set by default is "default".
            layout (fpdf.enums.PageLayout, str): allowed layout aliases are "single", "continuous", "two" or "default",
                meaning to use the viewer default mode.
                The layout set by default is "continuous".
        """
        if zoom in ZOOM_CONFIGS or not isinstance(zoom, str):
            self.zoom_mode = zoom
        elif zoom != "default":
            raise FPDFException(f"Incorrect zoom display mode: {zoom}")
        self.page_layout = LAYOUT_ALIASES.get(layout, layout)

    @property
    def page_layout(self):
        return self._page_layout

    @page_layout.setter
    def page_layout(self, page_layout):
        self._page_layout = PageLayout.coerce(page_layout) if page_layout else None
        if self._page_layout in (PageLayout.TWO_PAGE_LEFT, PageLayout.TWO_PAGE_RIGHT):
            self._set_min_pdf_version("1.5")

    def set_compression(self, compress):
        """
        Activates or deactivates page compression.

        When activated, the internal representation of each page is compressed
        using the zlib/deflate method (FlateDecode), which leads to a compression ratio
        of about 2 for the resulting document.

        Page compression is enabled by default.

        Args:
            compress (bool): indicates if compression should be enabled
        """
        self.compress = compress

    def set_title(self, title):
        """
        Defines the title of the document.

        Args:
            title (str): the title
        """
        self.title = title

    def set_lang(self, lang):
        """
        A language identifier specifying the natural language for all text in the document
        except where overridden by language specifications for structure elements or marked content.
        A language identifier can either be the empty text string, to indicate that the language is unknown,
        or a Language-Tag as defined in RFC 3066, "Tags for the Identification of Languages".

        Args:
            lang (str): the document main language
        """
        self.lang = lang
        if lang:
            self._set_min_pdf_version("1.4")

    def set_subject(self, subject):
        """
        Defines the subject of the document.

        Args:
            subject (str): the document main subject
        """
        self.subject = subject

    def set_author(self, author):
        """
        Defines the author of the document.

        Args:
            author(str): the name of the author
        """
        self.author = author

    def set_keywords(self, keywords):
        """
        Associate keywords with the document

        Args:
            keywords (str): a space-separated list of words
        """
        self.keywords = keywords

    def set_creator(self, creator):
        """
        Defines the creator of the document.
        This is typically the name of the application that generates the PDF.

        Args:
            creator (str): name of the PDF creator
        """
        self.creator = creator

    def set_producer(self, producer):
        """Producer of document"""
        self.producer = producer

    def set_creation_date(self, date=None):
        """Sets Creation of Date time, or current time if None given."""
        if self._sign_key:
            raise FPDFException(
                ".set_creation_date() must always be called before .sign*() methods"
            )
        if not isinstance(date, datetime):
            raise TypeError(f"date should be a datetime but is a {type(date)}")
        if not date.tzinfo:
            date = date.astimezone()
        self.creation_date = date

    def set_xmp_metadata(self, xmp_metadata):
        if "<?xpacket" in xmp_metadata[:50]:
            raise ValueError(
                "fpdf2 already performs XMP metadata wrapping in a <?xpacket> tag"
            )
        self.xmp_metadata = xmp_metadata
        if xmp_metadata:
            self._set_min_pdf_version("1.4")

    def set_doc_option(self, opt, value):
        """
        Defines a document option.

        Args:
            opt (str): name of the option to set
            value (str) option value

        .. deprecated:: 2.4.0
            Simply set the `FPDF.core_fonts_encoding` property as a replacement.
        """
        warnings.warn(
            # pylint: disable=implicit-str-concat
            "set_doc_option() is deprecated and will be removed in a future release. "
            "Simply set the `.core_fonts_encoding` property as a replacement.",
            DeprecationWarning,
            stacklevel=2,
        )
        if opt != "core_fonts_encoding":
            raise FPDFException(f'Unknown document option "{opt}"')
        self.core_fonts_encoding = value

    def set_image_filter(self, image_filter):
        """
        Args:
            image_filter (str): name of a the image filter to use
                when embedding images in the document, or "AUTO",
                meaning to use the best image filter given the images provided.
                Allowed values: `FlateDecode` (lossless zlib/deflate compression),
                `DCTDecode` (lossy compression with JPEG)
                and `JPXDecode` (lossy compression with JPEG2000).
        """
        if image_filter not in SUPPORTED_IMAGE_FILTERS:
            raise ValueError(
                f"'{image_filter}' is not a supported image filter"
                f" - Allowed values: {''.join(SUPPORTED_IMAGE_FILTERS)}"
            )
        self.image_filter = image_filter
        if image_filter == "JPXDecode":
            self._set_min_pdf_version("1.5")

    def alias_nb_pages(self, alias="{nb}"):
        """
        Defines an alias for the total number of pages.
        It will be substituted as the document is closed.

        This is useful to insert the number of pages of the document
        at a time when this number is not known by the program.

        This substitution can be disabled for performances reasons, by calling `alias_nb_pages(None)`.

        Args:
            alias (str): the alias. Defaults to "{nb}".

        Notes
        -----

        When using this feature with the `FPDF.cell` / `FPDF.multi_cell` methods,
        or the `.underline` attribute of `FPDF` class,
        the width of the text rendered will take into account the alias length,
        not the length of the "actual number of pages" string,
        which can causes slight positioning differences.
        """
        self.str_alias_nb_pages = alias

    def add_page(
        self, orientation="", format="", same=False, duration=0, transition=None
    ):
        """
        Adds a new page to the document.
        If a page is already present, the `FPDF.footer()` method is called first.
        Then the page  is added, the current position is set to the top-left corner,
        with respect to the left and top margins, and the `FPDF.header()` method is called.

        Args:
            orientation (str): "portrait" (can be abbreviated "P")
                or "landscape" (can be abbreviated "L"). Default to "portrait".
            format (str): "a3", "a4", "a5", "letter", "legal" or a tuple
                (width, height). Default to "a4".
            same (bool): indicates to use the same page format as the previous page.
                Default to False.
            duration (float): optional page’s display duration, i.e. the maximum length of time,
                in seconds, that the page is displayed in presentation mode,
                before the viewer application automatically advances to the next page.
                Can be configured globally through the `.page_duration` FPDF property.
                As of june 2021, onored by Adobe Acrobat reader, but ignored by Sumatra PDF reader.
            transition (Transition child class): optional visual transition to use when moving
                from another page to the given page during a presentation.
                Can be configured globally through the `.page_transition` FPDF property.
                As of june 2021, onored by Adobe Acrobat reader, but ignored by Sumatra PDF reader.
        """
        if self.buffer:
            raise FPDFException(
                "A page cannot be added on a closed document, after calling output()"
            )
        family = self.font_family
        style = f"{self.font_style}U" if self.underline else self.font_style
        size = self.font_size_pt
        lw = self.line_width
        dc = self.draw_color
        fc = self.fill_color
        tc = self.text_color
        stretching = self.font_stretching
        char_spacing = self.char_spacing

        if self.page > 0:
            # Page footer
            self.in_footer = True
            self.footer()
            self.in_footer = False

        # Start new page
        self._beginpage(
            orientation,
            format,
            same,
            duration or self.page_duration,
            transition or self.page_transition,
            new_page=not self._has_next_page(),
        )

        if self.page_background:
            if isinstance(self.page_background, tuple):
                self.set_fill_color(*self.page_background)
                self.rect(0, 0, self.w, self.h, style="F")
                self.set_fill_color(*(255 * v for v in fc.colors))
            else:
                self.image(self.page_background, 0, 0, self.w, self.h)

        self._out("2 J")  # Set line cap style to square
        self.line_width = lw  # Set line width
        self._out(f"{lw * self.k:.2f} w")

        # Set font
        if family:
            self.set_font(family, style, size)

        # Set colors
        self.draw_color = dc
        if dc != self.DEFAULT_DRAW_COLOR:
            self._out(dc.serialize().upper())
        self.fill_color = fc
        if fc != self.DEFAULT_FILL_COLOR:
            self._out(fc.serialize().lower())
        self.text_color = tc

        # BEGIN Page header
        self.header()

        if self.line_width != lw:  # Restore line width
            self.line_width = lw
            self._out(f"{lw * self.k:.2f} w")

        if family:
            self.set_font(family, style, size)  # Restore font

        if self.draw_color != dc:  # Restore colors
            self.draw_color = dc
            self._out(dc.serialize().upper())
        if self.fill_color != fc:
            self.fill_color = fc
            self._out(fc.serialize().lower())
        self.text_color = tc

        if stretching != 100:  # Restore stretching
            self.set_stretching(stretching)
        if char_spacing != 0:
            self.set_char_spacing(char_spacing)
        # END Page header

    def _beginpage(
        self, orientation, format, same, duration, transition, new_page=True
    ):
        self.page += 1
        if new_page:
            page = PDFPage(
                contents=bytearray(),
                duration=duration,
                transition=transition,
                index=self.page,
            )
            self.pages[self.page] = page
            if transition:
                self._set_min_pdf_version("1.5")
        else:
            page = self.pages[self.page]
        self.x = self.l_margin
        self.y = self.t_margin
        self.font_family = ""
        self.font_stretching = 100
        self.char_spacing = 0
        if same:
            if orientation or format:
                raise ValueError(
                    f"Inconsistent parameters: same={same} but orientation={orientation} format={format}"
                )
        else:
            # Set page format if provided, else use default value:
            page_width_pt, page_height_pt = (
                get_page_format(format, self.k) if format else (self.dw_pt, self.dh_pt)
            )
            self._set_orientation(
                orientation or self.def_orientation, page_width_pt, page_height_pt
            )
            self.page_break_trigger = self.h - self.b_margin
        page.set_dimensions(self.w_pt, self.h_pt)

    def header(self):
        """
        Header to be implemented in your own inherited class

        This is automatically called by `FPDF.add_page()`
        and should not be called directly by the user application.
        The default implementation performs nothing: you have to override this method
        in a subclass to implement your own rendering logic.
        """

    def footer(self):
        """
        Footer to be implemented in your own inherited class.

        This is automatically called by `FPDF.add_page()` and `FPDF.output()`
        and should not be called directly by the user application.
        The default implementation performs nothing: you have to override this method
        in a subclass to implement your own rendering logic.
        """

    def page_no(self):
        """Get the current page number"""
        return self.page

    def set_draw_color(self, r, g=-1, b=-1):
        """
        Defines the color used for all stroking operations (lines, rectangles and cell borders).
        It can be expressed in RGB components or grey scale.
        The method can be called before the first page is created and the value is retained from page to page.

        Args:
            r (int, tuple, fpdf.drawing.DeviceGray, fpdf.drawing.DeviceRGB): if `g` and `b` are given, this indicates the red component.
                Else, this indicates the grey level. The value must be between 0 and 255.
            g (int): green component (between 0 and 255)
            b (int): blue component (between 0 and 255)
        """
        self.draw_color = _convert_to_drawing_color(r, g, b)
        if self.page > 0:
            self._out(self.draw_color.serialize().upper())

    def set_fill_color(self, r, g=-1, b=-1):
        """
        Defines the color used for all filling operations (filled rectangles and cell backgrounds).
        It can be expressed in RGB components or grey scale.
        The method can be called before the first page is created and the value is retained from page to page.

        Args:
            r (int, tuple, fpdf.drawing.DeviceGray, fpdf.drawing.DeviceRGB): if `g` and `b` are given, this indicates the red component.
                Else, this indicates the grey level. The value must be between 0 and 255.
            g (int): green component (between 0 and 255)
            b (int): blue component (between 0 and 255)
        """
        self.fill_color = _convert_to_drawing_color(r, g, b)
        if self.page > 0:
            self._out(self.fill_color.serialize().lower())

    def set_text_color(self, r, g=-1, b=-1):
        """
        Defines the color used for text.
        It can be expressed in RGB components or grey scale.
        The method can be called before the first page is created and the value is retained from page to page.

        Args:
            r (int, tuple, fpdf.drawing.DeviceGray, fpdf.drawing.DeviceRGB): if `g` and `b` are given, this indicates the red component.
                Else, this indicates the grey level. The value must be between 0 and 255.
            g (int): green component (between 0 and 255)
            b (int): blue component (between 0 and 255)
        """
        self.text_color = _convert_to_drawing_color(r, g, b)

    def get_string_width(self, s, normalized=False, markdown=False):
        """
        Returns the length of a string in user unit. A font must be selected.
        The value is calculated with stretching and spacing.

        Args:
            s (str): the string whose length is to be computed.
            normalized (bool): whether normalization needs to be performed on the input string.
            markdown (bool): indicates if basic markdown support is enabled
        """
        # normalized is parameter for internal use
        s = s if normalized else self.normalize_text(s)
        w = 0
        for frag in (
            self._markdown_parse(s)
            if markdown
            else (Fragment(s, self._get_current_graphics_state(), self.k),)
        ):
            w += frag.get_width()
        return w

    def set_line_width(self, width):
        """
        Defines the line width of all stroking operations (lines, rectangles and cell borders).
        By default, the value equals 0.2 mm.
        The method can be called before the first page is created and the value is retained from page to page.

        Args:
            width (float): the width in user unit
        """
        self.line_width = width
        if self.page > 0:
            self._out(f"{width * self.k:.2f} w")

    def set_page_background(self, background):
        """
        Sets a background color or image to be drawn every time `FPDF.add_page()` is called, or removes a previously set background.
        The method can be called before the first page is created and the value is retained from page to page.

        Args:
            background: either a string representing a file path or URL to an image,
                an io.BytesIO containg an image as bytes, an instance of `PIL.Image.Image`, drawing.DeviceRGB
                or a RGB tuple representing a color to fill the background with or `None` to remove the background
        """

        if isinstance(
            background, (str, io.BytesIO, Image, drawing.DeviceRGB, tuple, type(None))
        ):
            if isinstance(background, drawing.DeviceRGB):
                self.page_background = tuple(255 * v for v in background.colors)
            else:
                self.page_background = background
        else:
            raise TypeError(
                f"""background must be of type str, io.BytesIO, PIL.Image.Image, drawing.DeviceRGB, tuple or None
        got: {type(background)}"""
            )

    @contextmanager
    @check_page
    def drawing_context(self, debug_stream=None):
        """
        Create a context for drawing paths on the current page.

        If this context manager is called again inside of an active context, it will
        raise an exception, as base drawing contexts cannot be nested.

        Args:
            debug_stream (TextIO): print a pretty tree of all items to be rendered
                to the provided stream. To store the output in a string, use
                `io.StringIO`.
        """

        if self._current_draw_context is not None:
            raise FPDFException(
                "cannot create a drawing context while one is already open"
            )

        context = drawing.DrawingContext()
        self._current_draw_context = context
        try:
            yield context
        finally:
            self._current_draw_context = None

        starting_style = self._current_graphic_style()
        render_args = (
            self._drawing_graphics_state_registry,
            drawing.Point(self.x, self.y),
            self.k,
            self.h,
            starting_style,
        )

        if debug_stream:
            rendered = context.render_debug(*render_args, debug_stream)
        else:
            rendered = context.render(*render_args)

        self._out(rendered)
        # The drawing API makes use of features (notably transparency and blending modes) that were introduced in PDF 1.4:
        self._set_min_pdf_version("1.4")

    def _current_graphic_style(self):
        gs = drawing.GraphicsStyle()
        gs.allow_transparency = self.allow_images_transparency

        # This initial stroke_width is ignored when embedding SVGs,
        # as the value in SVGObject.convert_graphics() takes precedence,
        # so this probably creates an unnecessary PDF dict entry:
        gs.stroke_width = self.line_width

        if self.draw_color != self.DEFAULT_DRAW_COLOR:
            gs.stroke_color = self.draw_color
        if self.fill_color != self.DEFAULT_FILL_COLOR:
            gs.fill_color = self.fill_color

        dash_info = self.dash_pattern
        dash_pattern = (dash_info["dash"], dash_info["gap"])
        if (dash_pattern[0] == 0) or (dash_pattern[1] == 0):
            dash_pattern = None

        gs.stroke_dash_pattern = dash_pattern
        gs.stroke_dash_phase = dash_info["phase"]

        return gs

    @contextmanager
    def new_path(self, x=0, y=0, paint_rule=PathPaintRule.AUTO, debug_stream=None):
        """
        Create a path for appending lines and curves to.

        Args:
            x (float): Abscissa of the path starting point
            y (float): Ordinate of the path starting point
            paint_rule (PathPaintRule): Optional choice of how the path should
                be painted. The default (AUTO) automatically selects stroke/fill based
                on the path style settings.
            debug_stream (TextIO): print a pretty tree of all items to be rendered
                to the provided stream. To store the output in a string, use
                `io.StringIO`.

        """
        with self.drawing_context(debug_stream=debug_stream) as ctxt:
            path = drawing.PaintedPath(x=x, y=y)
            path.style.paint_rule = paint_rule
            yield path
            ctxt.add_item(path)

    def draw_path(self, path, debug_stream=None):
        """
        Add a pre-constructed path to the document.

        Args:
            path (drawing.PaintedPath): the path to be drawn.
            debug_stream (TextIO): print a pretty tree of all items to be rendered
                to the provided stream. To store the output in a string, use
                `io.StringIO`.
        """
        with self.drawing_context(debug_stream=debug_stream) as ctxt:
            ctxt.add_item(path)

    def set_dash_pattern(self, dash=0, gap=0, phase=0):
        """
        Set the current dash pattern for lines and curves.

        Args:
            dash (float >= 0):
                The length of the dashes in current units.

            gap (float >= 0):
                The length of the gaps between dashes in current units.
                If omitted, the dash length will be used.

            phase (float >= 0):
                Where in the sequence to start drawing.

        Omitting 'dash' (= 0) resets the pattern to a solid line.
        """
        if not (isinstance(dash, (int, float)) and dash >= 0):
            raise ValueError("Dash length must be zero or a positive number.")
        if not (isinstance(gap, (int, float)) and gap >= 0):
            raise ValueError("gap length must be zero or a positive number.")
        if not (isinstance(phase, (int, float)) and phase >= 0):
            raise ValueError("Phase must be zero or a positive number.")

        pattern = dict(dash=dash, gap=gap, phase=phase)

        if pattern != self.dash_pattern:
            self.dash_pattern = pattern

            if dash:
                if gap:
                    dstr = f"[{dash * self.k:.3f} {gap * self.k:.3f}] {phase *self.k:.3f} d"
                else:
                    dstr = f"[{dash * self.k:.3f}] {phase *self.k:.3f} d"
            else:
                dstr = "[] 0 d"

            self._out(dstr)

    @check_page
    def line(self, x1, y1, x2, y2):
        """
        Draw a line between two points.

        Args:
            x1 (float): Abscissa of first point
            y1 (float): Ordinate of first point
            x2 (float): Abscissa of second point
            y2 (float): Ordinate of second point
        """
        self._out(
            f"{x1 * self.k:.2f} {(self.h - y1) * self.k:.2f} m {x2 * self.k:.2f} "
            f"{(self.h - y2) * self.k:.2f} l S"
        )

    @check_page
    def polyline(self, point_list, fill=False, polygon=False, style=None):
        """
        Draws lines between two or more points.

        Args:
            point_list (list of tuples): List of Abscissa and Ordinate of
                                        segments that should be drawn
            fill (bool): [**DEPRECATED since v2.5.4**] Use `style="F"` or `style="DF"` instead
            polygon (bool): If true, close path before stroking, to fill the inside of the polyline
            style (fpdf.enums.RenderStyle, str): Optional style of rendering. Possible values are:

            * `D` or None: draw border. This is the default value.
            * `F`: fill
            * `DF` or `FD`: draw and fill
        """
        if fill:
            warnings.warn(
                '"fill" parameter is deprecated, use style="F" or style="DF" instead',
                DeprecationWarning,
                stacklevel=5 if polygon else 3,
            )
        if fill and style is None:
            style = RenderStyle.DF
        else:
            style = RenderStyle.coerce(style)
            if fill and style == RenderStyle.D:
                raise ValueError(
                    f"Conflicting values provided: fill={fill} & style={style}"
                )
        operator = "m"
        for point in point_list:
            self._out(
                f"{point[0] * self.k:.2f} {(self.h - point[1]) * self.k:.2f} {operator}"
            )
            operator = "l"
        if polygon:
            self._out(" h")
        self._out(f" {style.operator}")

    @check_page
    def polygon(self, point_list, fill=False, style=None):
        """
        Outputs a polygon defined by three or more points.

        Args:
            point_list (list of tuples): List of coordinates defining the polygon to draw
            fill (bool): [**DEPRECATED since v2.5.4**] Use `style="F"` or `style="DF"` instead
            style (fpdf.enums.RenderStyle, str): Optional style of rendering. Possible values are:

            * `D` or None: draw border. This is the default value.
            * `F`: fill
            * `DF` or `FD`: draw and fill
        """
        self.polyline(point_list, fill=fill, polygon=True, style=style)

    @check_page
    def dashed_line(self, x1, y1, x2, y2, dash_length=1, space_length=1):
        """
        Draw a dashed line between two points.

        Args:
            x1 (float): Abscissa of first point
            y1 (float): Ordinate of first point
            x2 (float): Abscissa of second point
            y2 (float): Ordinate of second point
            dash_length (float): Length of the dash
            space_length (float): Length of the space between 2 dashes

        .. deprecated:: 2.4.6
            Use `FPDF.set_dash_pattern()` and the normal drawing operations instead.
        """
        warnings.warn(
            # pylint: disable=implicit-str-concat
            "dashed_line() is deprecated, and will be removed in a future release. "
            "Use set_dash_pattern() and the normal drawing operations instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        self.set_dash_pattern(dash_length, space_length)
        self.line(x1, y1, x2, y2)
        self.set_dash_pattern()

    @check_page
    def rect(self, x, y, w, h, style=None, round_corners=False, corner_radius=0):
        """
        Outputs a rectangle.
        It can be drawn (border only), filled (with no border) or both.

        Args:
            x (float): Abscissa of upper-left bounding box.
            y (float): Ordinate of upper-left bounding box.
            w (float): Width.
            h (float): Height.

            style (fpdf.enums.RenderStyle, str): Optional style of rendering. Possible values are:

            * `D` or empty string: draw border. This is the default value.
            * `F`: fill
            * `DF` or `FD`: draw and fill

            round_corners (tuple of str, tuple of fpdf.enums.Corner, bool): Optional draw a rectangle with round corners.
            Possible values are:

            *`TOP_LEFT`: a rectangle with round top left corner
            *`TOP_RIGHT`: a rectangle with round top right corner
            *`BOTTOM_LEFT`: a rectangle with round bottom left corner
            *`BOTTOM_RIGHT`: a rectangle with round bottom right corner
            *`True`: a rectangle with all round corners
            *`False`: a rectangle with no round corners

            corner_radius: Optional radius of the corners
        """

        style = RenderStyle.coerce(style)
        if round_corners is not False:
            self._draw_rounded_rect(x, y, w, h, style, round_corners, corner_radius)
        else:
            self._out(
                f"{x * self.k:.2f} {(self.h - y) * self.k:.2f} {w * self.k:.2f} "
                f"{-h * self.k:.2f} re {style.operator}"
            )

    def _draw_rounded_rect(self, x, y, w, h, style, round_corners, r):
        min = h
        if w < h:
            min = w

        if r == 0:
            r = min / 5

        if r >= min / 2:
            r /= min

        point_1 = point_8 = (x, y)
        point_2 = point_3 = (x + w, y)
        point_4 = point_5 = (x + w, y + h)
        point_6 = point_7 = (x, y + h)
        coor_x = [x, x + w, x, x + w]
        coor_y = [y, y, y + h, y + h]

        if round_corners is True:
            round_corners = (
                Corner.TOP_RIGHT.value,
                Corner.TOP_LEFT.value,
                Corner.BOTTOM_RIGHT.value,
                Corner.BOTTOM_LEFT.value,
            )
        round_corners = tuple(Corner.coerce(rc) for rc in round_corners)

        if Corner.TOP_RIGHT in round_corners:
            self.arc(coor_x[0], coor_y[0], 2 * r, 180, 270, style=style)
            point_1 = (x + r, y)
            point_8 = (x, y + r)

        if Corner.TOP_LEFT in round_corners:
            self.arc(coor_x[1] - 2 * r, coor_y[1], 2 * r, 270, 0, style=style)
            point_2 = (x + w - r, y)
            point_3 = (x + w, y + r)

        if Corner.BOTTOM_LEFT in round_corners:
            self.arc(coor_x[3] - 2 * r, coor_y[3] - 2 * r, 2 * r, 0, 90, style=style)
            point_4 = (x + w, y + h - r)
            point_5 = (x + w - r, y + h)

        if Corner.BOTTOM_RIGHT in round_corners:
            self.arc(coor_x[2], coor_y[2] - 2 * r, 2 * r, 90, 180, style=style)
            point_6 = (x + r, y + h)
            point_7 = (x, y + h - r)

        if style.is_fill:
            self.polyline(
                [
                    point_1,
                    point_2,
                    point_3,
                    point_4,
                    point_5,
                    point_6,
                    point_7,
                    point_8,
                    point_1,
                ],
                style="F",
            )

        if style.is_draw:
            self.line(point_1[0], point_1[1], point_2[0], point_2[1])
            self.line(point_3[0], point_3[1], point_4[0], point_4[1])
            self.line(point_5[0], point_5[1], point_6[0], point_6[1])
            self.line(point_7[0], point_7[1], point_8[0], point_8[1])

    @check_page
    def ellipse(self, x, y, w, h, style=None):
        """
        Outputs an ellipse.
        It can be drawn (border only), filled (with no border) or both.

        Args:
            x (float): Abscissa of upper-left bounding box.
            y (float): Ordinate of upper-left bounding box.
            w (float): Width
            h (float): Height
            style (fpdf.enums.RenderStyle, str): Optional style of rendering. Possible values are:

            * `D` or empty string: draw border. This is the default value.
            * `F`: fill
            * `DF` or `FD`: draw and fill
        """
        style = RenderStyle.coerce(style)
        self._draw_ellipse(x, y, w, h, style.operator)

    def _draw_ellipse(self, x, y, w, h, operator):
        cx = x + w / 2
        cy = y + h / 2
        rx = w / 2
        ry = h / 2

        lx = 4 / 3 * (math.sqrt(2) - 1) * rx
        ly = 4 / 3 * (math.sqrt(2) - 1) * ry

        self._out(
            (
                f"{(cx + rx) * self.k:.2f} {(self.h - cy) * self.k:.2f} m "
                f"{(cx + rx) * self.k:.2f} {(self.h - cy + ly) * self.k:.2f} "
                f"{(cx + lx) * self.k:.2f} {(self.h - cy + ry) * self.k:.2f} "
                f"{cx * self.k:.2f} {(self.h - cy + ry) * self.k:.2f} c"
            )
        )
        self._out(
            (
                f"{(cx - lx) * self.k:.2f} {(self.h - cy + ry) * self.k:.2f} "
                f"{(cx - rx) * self.k:.2f} {(self.h - cy + ly) * self.k:.2f} "
                f"{(cx - rx) * self.k:.2f} {(self.h - cy) * self.k:.2f} c"
            )
        )
        self._out(
            (
                f"{(cx - rx) * self.k:.2f} {(self.h - cy - ly) * self.k:.2f} "
                f"{(cx - lx) * self.k:.2f} {(self.h - cy - ry) * self.k:.2f} "
                f"{cx * self.k:.2f} {(self.h - cy - ry) * self.k:.2f} c"
            )
        )
        self._out(
            (
                f"{(cx + lx) * self.k:.2f} {(self.h - cy - ry) * self.k:.2f} "
                f"{(cx + rx) * self.k:.2f} {(self.h - cy - ly) * self.k:.2f} "
                f"{(cx + rx) * self.k:.2f} {(self.h - cy) * self.k:.2f} c {operator}"
            )
        )

    @check_page
    def circle(self, x, y, r, style=None):
        """
        Outputs a circle.
        It can be drawn (border only), filled (with no border) or both.

        Args:
            x (float): Abscissa of upper-left bounding box.
            y (float): Ordinate of upper-left bounding box.
            r (float): Radius of the circle.
            style (str): Style of rendering. Possible values are:

            * `D` or None: draw border. This is the default value.
            * `F`: fill
            * `DF` or `FD`: draw and fill
        """
        self.ellipse(x, y, r, r, style)

    @check_page
    def regular_polygon(self, x, y, numSides, polyWidth, rotateDegrees=0, style=None):
        """
        Outputs a regular polygon with n sides
        It can be rotated
        Style can also be applied (fill, border...)

        Args:
            x (float): Abscissa of upper-left bounding box.
            y (float): Ordinate of upper-left bounding box.
            numSides (int): Number of sides for polygon.
            polyWidth (float): Width of the polygon.
            rotateDegrees (float): Optional degree amount to rotate polygon.
            style (fpdf.enums.RenderStyle, str): Optional style of rendering. Possible values are:

            * `D` or None: draw border. This is the default value.
            * `F`: fill
            * `DF` or `FD`: draw and fill
        """
        radius = polyWidth / 2
        centerX = x + radius
        centerY = y - radius
        # center point is (centerX, centerY)
        points = []
        for i in range(1, numSides + 1):
            point = centerX + radius * math.cos(
                math.radians((360 / numSides) * i) + math.radians(rotateDegrees)
            ), centerY + radius * math.sin(
                math.radians((360 / numSides) * i) + math.radians(rotateDegrees)
            )
            points.append(point)
        # creates list of touples containing cordinate points of vertices

        self.polygon(points, style=style)
        # passes points through polygon function

    @check_page
    def star(self, x, y, r_in, r_out, corners, rotate_degrees=0, style=None):
        """
        Outputs a regular star with n corners.
        It can be rotated.
        It can be drawn (border only), filled (with no border) or both.

        Args:
            x (float): Abscissa of star's centre.
            y (float): Ordinate of star's centre.
            r_in (float): radius of internal circle.
            r_out (float): radius of external circle.
            corners (int): number of star's corners.
            rotate_degrees (float): Optional degree amount to rotate star clockwise.

            style (fpdf.enums.RenderStyle, str): Optional style of rendering. Possible values are:
            * `D`: draw border. This is the default value.
            * `F`: fill.
            * `DF` or `FD`: draw and fill.
        """
        th = math.radians(rotate_degrees)
        point_list = []
        for i in range(0, (corners * 2) + 1):
            corner_x = x + (r_out if i % 2 == 0 else r_in) * math.sin(th)
            corner_y = y + (r_out if i % 2 == 0 else r_in) * math.cos(th)
            point_list.append((corner_x, corner_y))

            th += math.radians(180 / corners)

        self.polyline(point_list, polygon=True, style=style)

    @check_page
    def arc(
        self,
        x,
        y,
        a,
        start_angle,
        end_angle,
        b=None,
        inclination=0,
        clockwise=False,
        start_from_center=False,
        end_at_center=False,
        style=None,
    ):
        """
        Outputs an arc.
        It can be drawn (border only), filled (with no border) or both.

        Args:
            a (float): Semi-major axis diameter.
            b (float): Semi-minor axis diameter, if None, equals to a (default: None).
            start_angle (float): Start angle of the arc (in degrees).
            end_angle (float): End angle of the arc (in degrees).
            inclination (float): Inclination of the arc in respect of the x-axis (default: 0).
            clockwise (bool): Way of drawing the arc (True: clockwise, False: counterclockwise) (default: False).
            start_from_center (bool): Start drawing from the center of the circle (default: False).
            end_at_center (bool): End drawing at the center of the circle (default: False).
            style (fpdf.enums.RenderStyle, str): Optional style of rendering. Allowed values are:

            * `D` or None: draw border. This is the default value.
            * `F`: fill
            * `DF` or `FD`: draw and fill
        """
        style = RenderStyle.coerce(style)

        if b is None:
            b = a

        a /= 2
        b /= 2

        cx = x + a
        cy = y + b

        # Functions used only to construct other points of the bezier curve
        def deg_to_rad(deg):
            return deg * math.pi / 180

        def angle_to_param(angle):
            angle = deg_to_rad(angle % 360)
            eta = math.atan2(math.sin(angle) / b, math.cos(angle) / a)

            if eta < 0:
                eta += 2 * math.pi
            return eta

        theta = deg_to_rad(inclination)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        def evaluate(eta):
            a_cos_eta = a * math.cos(eta)
            b_sin_eta = b * math.sin(eta)

            return [
                cx + a_cos_eta * cos_theta - b_sin_eta * sin_theta,
                cy + a_cos_eta * sin_theta + b_sin_eta * cos_theta,
            ]

        def derivative_evaluate(eta):
            a_sin_eta = a * math.sin(eta)
            b_cos_eta = b * math.cos(eta)

            return [
                -a_sin_eta * cos_theta - b_cos_eta * sin_theta,
                -a_sin_eta * sin_theta + b_cos_eta * cos_theta,
            ]

        # Calculating start_eta and end_eta so that
        #   start_eta < end_eta   <= start_eta + 2*PI if counterclockwise
        #   end_eta   < start_eta <= end_eta + 2*PI   if clockwise
        start_eta = angle_to_param(start_angle)
        end_eta = angle_to_param(end_angle)

        if not clockwise and end_eta <= start_eta:
            end_eta += 2 * math.pi
        elif clockwise and end_eta >= start_eta:
            start_eta += 2 * math.pi

        start_point = evaluate(start_eta)

        # Move to the start point
        if start_from_center:
            self._out(f"{cx * self.k:.2f} {(self.h - cy) * self.k:.2f} m")
            self._out(
                f"{start_point[0] * self.k:.2f} {(self.h - start_point[1]) * self.k:.2f} l"
            )
        else:
            self._out(
                f"{start_point[0] * self.k:.2f} {(self.h - start_point[1]) * self.k:.2f} m"
            )

        # Number of curves to use, maximal segment angle is 2*PI/max_curves
        max_curves = 4
        n = min(
            max_curves, math.ceil(abs(end_eta - start_eta) / (2 * math.pi / max_curves))
        )
        d_eta = (end_eta - start_eta) / n

        alpha = math.sin(d_eta) * (math.sqrt(4 + 3 * math.tan(d_eta / 2) ** 2) - 1) / 3

        eta2 = start_eta
        p2 = evaluate(eta2)
        p2_prime = derivative_evaluate(eta2)

        for i in range(n):
            p1 = p2
            p1_prime = p2_prime

            eta2 += d_eta
            p2 = evaluate(eta2)
            p2_prime = derivative_evaluate(eta2)

            control_point_1 = [p1[0] + alpha * p1_prime[0], p1[1] + alpha * p1_prime[1]]
            control_point_2 = [p2[0] - alpha * p2_prime[0], p2[1] - alpha * p2_prime[1]]

            end = ""
            if i == n - 1 and not end_at_center:
                end = f" {style.operator}"

            self._out(
                (
                    f"{control_point_1[0] * self.k:.2f} {(self.h - control_point_1[1]) * self.k:.2f} "
                    f"{control_point_2[0] * self.k:.2f} {(self.h - control_point_2[1]) * self.k:.2f} "
                    f"{p2[0] * self.k:.2f} {(self.h - p2[1]) * self.k:.2f} c" + end
                )
            )

        if end_at_center:
            if start_from_center:
                self._out(f"h {style.operator}")
            else:
                self._out(
                    f"{cx * self.k:.2f} {(self.h - cy) * self.k:.2f} l {style.operator}"
                )

    def solid_arc(
        self,
        x,
        y,
        a,
        start_angle,
        end_angle,
        b=None,
        inclination=0,
        clockwise=False,
        style=None,
    ):
        """
        Outputs a solid arc. A solid arc combines an arc and a triangle to form a pie slice
        It can be drawn (border only), filled (with no border) or both.

        Args:
            x (float): Abscissa of upper-left bounding box.
            y (float): Ordinate of upper-left bounding box.
            a (float): Semi-major axis.
            b (float): Semi-minor axis, if None, equals to a (default: None).
            start_angle (float): Start angle of the arc (in degrees).
            end_angle (float): End angle of the arc (in degrees).
            inclination (float): Inclination of the arc in respect of the x-axis (default: 0).
            clockwise (bool): Way of drawing the arc (True: clockwise, False: counterclockwise) (default: False).
            style (str): Style of rendering. Possible values are:

            * `D` or None: draw border. This is the default value.
            * `F`: fill
            * `DF` or `FD`: draw and fill
        """
        self.arc(
            x,
            y,
            a,
            start_angle,
            end_angle,
            b,
            inclination,
            clockwise,
            True,
            True,
            style,
        )

    def add_font(self, family=None, style="", fname=None, uni="DEPRECATED"):
        """
        Imports a TrueType or OpenType font and makes it available
        for later calls to the `FPDF.set_font()` method.

        You will find more information on the "Unicode" documentation page.

        Args:
            family (str): optional name of the font family. Used as a reference for `FPDF.set_font()`.
                If not provided, use the base name of the `fname` font path, without extension.
            style (str): font style. "B" for bold, "I" for italic.
            fname (str): font file name. You can specify a relative or full path.
                If the file is not found, it will be searched in `FPDF_FONT_DIR`.
            uni (bool): [**DEPRECATED since 2.5.1**] unused
        """
        if not fname:
            raise ValueError('"fname" parameter is required')

        ext = splitext(str(fname))[1].lower()
        if ext not in (".otf", ".otc", ".ttf", ".ttc"):
            raise ValueError(
                f"Unsupported font file extension: {ext}."
                " add_font() used to accept .pkl file as input, but for security reasons"
                " this feature is deprecated since v2.5.1 and has been removed in v2.5.3."
            )

        if uni != "DEPRECATED":
            warnings.warn(
                '"uni" parameter is deprecated, unused and will soon be removed',
                DeprecationWarning,
                stacklevel=2,
            )

        style = "".join(sorted(style.upper()))
        if any(letter not in "BI" for letter in style):
            raise ValueError(
                f"Unknown style provided (only B & I letters are allowed): {style}"
            )

        for parent in (".", FPDF_FONT_DIR):
            if not parent:
                continue

            if (Path(parent) / fname).exists():
                font_file_path = Path(parent) / fname
                break
        else:
            raise FileNotFoundError(f"TTF Font file not found: {fname}")

        if family is None:
            family = font_file_path.stem

        fontkey = f"{family.lower()}{style}"
        # Check if font already added or one of the core fonts
        if fontkey in self.fonts or fontkey in CORE_FONTS:
            warnings.warn(f"Core font or font already added '{fontkey}': doing nothing")
            return

        self.fonts[fontkey] = TTFFont(self, font_file_path, fontkey, style)

    def set_font(self, family=None, style="", size=0):
        """
        Sets the font used to print character strings.
        It is mandatory to call this method at least once before printing text.

        Default encoding is not specified, but all text writing methods accept only
        unicode for external fonts and one byte encoding for standard.

        Standard fonts use `Latin-1` encoding by default, but Windows
        encoding `cp1252` (Western Europe) can be used with
        `self.core_fonts_encoding = encoding`.

        The font specified is retained from page to page.
        The method can be called before the first page is created.

        Args:
            family (str): name of a font added with `FPDF.add_font`,
                or name of one of the 14 standard "PostScript" fonts:
                Courier (fixed-width), Helvetica (sans serif), Times (serif),
                Symbol (symbolic) or ZapfDingbats (symbolic)
                If an empty string is provided, the current family is retained.
            style (str): empty string (by default) or a combination
                of one or several letters among B (bold), I (italic) and U (underline).
                Bold and italic styles do not apply to Symbol and ZapfDingbats fonts.
            size (float): in points. The default value is the current size.
        """
        if not family:
            family = self.font_family

        family = family.lower()
        style = "".join(sorted(style.upper()))
        if any(letter not in "BIU" for letter in style):
            raise ValueError(
                f"Unknown style provided (only B/I/U letters are allowed): {style}"
            )
        if "U" in style:
            self.underline = True
            style = style.replace("U", "")
        else:
            self.underline = False

        if family in self.font_aliases and family + style not in self.fonts:
            warnings.warn(
                f"Substituting font {family} by core font "
                f"{self.font_aliases[family]}"
            )
            family = self.font_aliases[family]
        elif family in ("symbol", "zapfdingbats") and style:
            warnings.warn(
                f"Built-in font {family} only has a single 'style' and can't be bold "
                f"or italic"
            )
            style = ""

        if size == 0:
            size = self.font_size_pt

        # Test if font is already selected
        if (
            self.font_family == family
            and self.font_style == style
            and isclose(self.font_size_pt, size)
        ):
            return

        # Test if used for the first time
        fontkey = family + style
        if fontkey not in self.fonts:
            if fontkey not in CORE_FONTS:
                raise FPDFException(
                    f"Undefined font: {fontkey} - "
                    f"Use built-in fonts or FPDF.add_font() beforehand"
                )
            # If it's one of the core fonts, add it to self.fonts
            self.fonts[fontkey] = CoreFont(self, fontkey, style)

        # Select it
        self.font_family = family
        self.font_style = style
        self.font_size_pt = size
        self.current_font = self.fonts[fontkey]
        if self.page > 0:
            self._out(f"BT /F{self.current_font.i} {self.font_size_pt:.2f} Tf ET")

    def set_font_size(self, size):
        """
        Configure the font size in points

        Args:
            size (float): font size in points
        """
        if isclose(self.font_size_pt, size):
            return
        self.font_size_pt = size
        if self.page > 0:
            if not self.current_font:
                raise FPDFException(
                    "Cannot set font size: a font must be selected first"
                )
            self._out(f"BT /F{self.current_font.i} {self.font_size_pt:.2f} Tf ET")

    def set_char_spacing(self, spacing):
        """
        Sets horizontal character spacing.
        A positive value increases the space between characters, a negative value
        reduces it (which may result in glyph overlap).
        By default, no spacing is set (which is equivalent to a value of 0).

        Args:
            spacing (float): horizontal spacing in document units
        """
        if self.char_spacing == spacing:
            return
        self.char_spacing = spacing
        if self.page > 0:
            self._out(f"BT {spacing:.2f} Tc ET")

    def set_stretching(self, stretching):
        """
        Sets horizontal font stretching.
        By default, no stretching is set (which is equivalent to a value of 100).

        Args:
            stretching (float): horizontal stretching (scaling) in percents.
        """
        if self.font_stretching == stretching:
            return
        self.font_stretching = stretching
        if self.page > 0:
            self._out(f"BT {stretching:.2f} Tz ET")

    def set_fallback_fonts(self, fallback_fonts, exact_match=True):
        """
        Allows you to specify a list of fonts to be used if any character is not available on the font currently set.
        Detailed documentation: https://pyfpdf.github.io/fpdf2/Unicode.html#fallback-fonts

        Args:
            fallback_fonts: sequence of fallback font IDs
            exact_match (bool): when a glyph cannot be rendered uing the current font,
                fpdf2 will look for a fallback font matching the current character emphasis (bold/italics).
                If it does not find such matching font, and `exact_match` is True, no fallback font will be used.
                If it does not find such matching font, and `exact_match` is False, a fallback font will still be used.
                To get even more control over this logic, you can also override `FPDF.get_fallback_font()`
        """
        fallback_font_ids = []
        for fallback_font in fallback_fonts:
            found = False
            for fontkey in self.fonts:
                # will add all font styles on the same family
                if fontkey.replace("B", "").replace("I", "") == fallback_font.lower():
                    fallback_font_ids.append(fontkey)
                    found = True
            if not found:
                raise FPDFException(
                    f"Undefined fallback font: {fallback_font} - Use FPDF.add_font() beforehand"
                )
        self._fallback_font_ids = tuple(fallback_font_ids)
        self._fallback_font_exact_match = exact_match

    def add_link(self, y=0, x=0, page=-1, zoom="null"):
        """
        Creates a new internal link and returns its identifier.
        An internal link is a clickable area which directs to another place within the document.

        The identifier can then be passed to the `FPDF.cell()`, `FPDF.write()`, `FPDF.image()`
        or `FPDF.link()` methods.

        Args:
            y (float): optional ordinate of target position.
                The default value is 0 (top of page).
            x (float): optional abscissa of target position.
                The default value is 0 (top of page).
            page (int): optional number of target page.
                -1 indicates the current page, which is the default value.
            zoom (float): optional new zoom level after following the link.
                Currently ignored by Sumatra PDF Reader, but observed by Adobe Acrobat reader.
        """
        link = DestinationXYZ(
            self.page if page == -1 else page,
            top=self.h_pt - y * self.k,
            left=x * self.k,
            zoom=zoom,
        )
        link_index = len(self.links) + 1
        self.links[link_index] = link
        return link_index

    def set_link(self, link, y=0, x=0, page=-1, zoom="null"):
        """
        Defines the page and position a link points to.

        Args:
            link (int): a link identifier returned by `FPDF.add_link()`.
            y (float): optional ordinate of target position.
                The default value is 0 (top of page).
            x (float): optional abscissa of target position.
                The default value is 0 (top of page).
            page (int): optional number of target page.
                -1 indicates the current page, which is the default value.
            zoom (float): optional new zoom level after following the link.
                Currently ignored by Sumatra PDF Reader, but observed by Adobe Acrobat reader.
        """
        # We must take care to update the existing DestinationXYZ,
        # and NOT re-assign self.links[link] to a new instance,
        # as a reference to self.links[link] is kept in self.pages[].annots:
        link = self.links[link]
        link.page_number = self.page if page == -1 else page
        link.top = self.h_pt - y * self.k
        link.left = x * self.k
        link.zoom = zoom

    @check_page
    def link(self, x, y, w, h, link, alt_text=None, border_width=0):
        """
        Puts a link annotation on a rectangular area of the page.
        Text or image links are generally put via `FPDF.cell`,
        `FPDF.write` or `FPDF.image`,
        but this method can be useful for instance to define a clickable area inside an image.

        Args:
            x (float): horizontal position (from the left) to the left side of the link rectangle
            y (float): vertical position (from the top) to the bottom side of the link rectangle
            w (float): width of the link rectangle
            h (float): height of the link rectangle
            link: either an URL or an integer returned by `FPDF.add_link`, defining an internal link to a page
            alt_text (str): optional textual description of the link, for accessibility purposes
            border_width (int): thickness of an optional black border surrounding the link.
                Not all PDF readers honor this: Acrobat renders it but not Sumatra.
        """
        action, dest = None, None
        if link:
            if isinstance(link, str):
                action = URIAction(link)
            else:  # Dest type ending of annotation entry
                assert (
                    link in self.links
                ), f"Link with an invalid index: {link} (doc #links={len(self.links)})"
                dest = self.links[link]
                if not dest.page_number:
                    raise ValueError(
                        f"Cannot insert link {link} with no page number assigned"
                    )
        link_annot = AnnotationDict(
            "Link",
            x=x * self.k,
            y=self.h_pt - y * self.k,
            width=w * self.k,
            height=h * self.k,
            action=action,
            dest=dest,
            border_width=border_width,
        )
        self.pages[self.page].annots.append(link_annot)
        if alt_text is not None:
            # Note: the spec indicates that a /StructParent could be added **inside* this /Annot,
            # but tests with Adobe Acrobat Reader reveal that the page /StructParents inserted below
            # is enough to link the marked content in the hierarchy tree with this annotation link.
            self._add_marked_content(struct_type="/Link", alt_text=alt_text)
        return link_annot

    def embed_file(
        self,
        file_path=None,
        bytes=None,
        basename=None,
        modification_date=None,
        **kwargs,
    ):
        """
        Embed a file into the PDF document

        Args:
            file_path (str or Path): filesystem path to the existing file to embed
            bytes (bytes): optional, as an alternative to file_path, bytes content of the file to embed
            basename (str): optional, required if bytes is provided, file base name
            creation_date (datetime): date and time when the file was created
            modification_date (datetime): date and time when the file was last modified
            desc (str): optional description of the file
            compress (bool): enabled zlib compression of the file - False by default
            checksum (bool): insert a MD5 checksum of the file content - False by default

        Returns: a PDFEmbeddedFile instance, with a .basename string attribute representing the internal file name
        """
        if file_path:
            if bytes:
                raise ValueError("'bytes' cannot be provided with 'file_path'")
            if basename:
                raise ValueError("'basename' cannot be provided with 'file_path'")
            file_path = Path(file_path)
            with file_path.open("rb") as input_file:
                bytes = input_file.read()
            basename = file_path.name
            stats = file_path.stat()
            if modification_date is None:
                modification_date = datetime.fromtimestamp(stats.st_mtime).astimezone()
        else:
            if not bytes:
                raise ValueError("'bytes' is required if 'file_path' is not provided")
            if not basename:
                raise ValueError(
                    "'basename' is required if 'file_path' is not provided"
                )
        already_embedded_basenames = set(
            file.basename() for file in self.embedded_files
        )
        if basename in already_embedded_basenames:
            raise ValueError(f"{basename} has already been embedded in this file")
        embedded_file = PDFEmbeddedFile(
            basename=basename,
            contents=bytes,
            modification_date=modification_date,
            **kwargs,
        )
        self.embedded_files.append(embedded_file)
        self._set_min_pdf_version("1.4")
        return embedded_file

    @check_page
    def file_attachment_annotation(
        self, file_path, x, y, w=1, h=1, name=None, flags=DEFAULT_ANNOT_FLAGS, **kwargs
    ):
        """
        Puts a file attachment annotation on a rectangular area of the page.

        Args:
            file_path (str or Path): filesystem path to the existing file to embed
            x (float): horizontal position (from the left) to the left side of the link rectangle
            y (float): vertical position (from the top) to the bottom side of the link rectangle
            w (float): optional width of the link rectangle
            h (float): optional height of the link rectangle
            name (fpdf.enums.FileAttachmentAnnotationName, str): optional icon that shall be used in displaying the annotation
            flags (Tuple[fpdf.enums.AnnotationFlag], Tuple[str]): optional list of flags defining annotation properties
            bytes (bytes): optional, as an alternative to file_path, bytes content of the file to embed
            basename (str): optional, required if bytes is provided, file base name
            creation_date (datetime): date and time when the file was created
            modification_date (datetime): date and time when the file was last modified
            desc (str): optional description of the file
            compress (bool): enabled zlib compression of the file - False by default
            checksum (bool): insert a MD5 checksum of the file content - False by default
        """
        embedded_file = self.embed_file(file_path, **kwargs)
        embedded_file.set_globally_enclosed(False)
        annotation = AnnotationDict(
            "FileAttachment",
            x * self.k,
            self.h_pt - y * self.k,
            w * self.k,
            h * self.k,
            file_spec=embedded_file.file_spec(),
            name=FileAttachmentAnnotationName.coerce(name) if name else None,
            flags=tuple(AnnotationFlag.coerce(flag) for flag in flags),
        )
        self.pages[self.page].annots.append(annotation)
        return annotation

    @check_page
    def text_annotation(
        self, x, y, text, w=1, h=1, name=None, flags=DEFAULT_ANNOT_FLAGS
    ):
        """
        Puts a text annotation on a rectangular area of the page.

        Args:
            x (float): horizontal position (from the left) to the left side of the link rectangle
            y (float): vertical position (from the top) to the bottom side of the link rectangle
            text (str): text to display
            w (float): optional width of the link rectangle
            h (float): optional height of the link rectangle
            name (fpdf.enums.AnnotationName, str): optional icon that shall be used in displaying the annotation
            flags (Tuple[fpdf.enums.AnnotationFlag], Tuple[str]): optional list of flags defining annotation properties
        """
        annotation = AnnotationDict(
            "Text",
            x * self.k,
            self.h_pt - y * self.k,
            w * self.k,
            h * self.k,
            contents=text,
            name=AnnotationName.coerce(name) if name else None,
            flags=tuple(AnnotationFlag.coerce(flag) for flag in flags),
        )
        self.pages[self.page].annots.append(annotation)
        return annotation

    @check_page
    def add_action(self, action, x, y, w, h):
        """
        Puts an Action annotation on a rectangular area of the page.

        Args:
            action (fpdf.actions.Action): the action to add
            x (float): horizontal position (from the left) to the left side of the link rectangle
            y (float): vertical position (from the top) to the bottom side of the link rectangle
            w (float): width of the link rectangle
            h (float): height of the link rectangle
        """
        annotation = AnnotationDict(
            "Action",
            x * self.k,
            self.h_pt - y * self.k,
            w * self.k,
            h * self.k,
            action=action,
        )
        self.pages[self.page].annots.append(annotation)
        return annotation

    @contextmanager
    def highlight(
        self, text, title="", type="Highlight", color=(1, 1, 0), modification_time=None
    ):
        """
        Context manager that adds a single highlight annotation based on the text lines inserted
        inside its indented block.

        Args:
            text (str): text of the annotation
            title (str): the text label that shall be displayed in the title bar of the annotation’s
                pop-up window when open and active. This entry shall identify the user who added the annotation.
            type (fpdf.enums.TextMarkupType, str): "Highlight", "Underline", "Squiggly" or "StrikeOut".
            color (tuple): a tuple of numbers in the range 0.0 to 1.0, representing a colour used for
                the title bar of the annotation’s pop-up window. Defaults to yellow.
            modification_time (datetime): date and time when the annotation was most recently modified
        """
        if self._record_text_quad_points:
            raise FPDFException("highlight() cannot be nested")
        self._record_text_quad_points = True
        yield
        for page, quad_points in self._text_quad_points.items():
            self.add_text_markup_annotation(
                type,
                text,
                quad_points=quad_points,
                title=title,
                color=color,
                modification_time=modification_time,
                page=page,
            )
        self._text_quad_points = defaultdict(list)
        self._record_text_quad_points = False

    add_highlight = highlight  # For backward compatibilty

    @check_page
    def add_text_markup_annotation(
        self,
        type,
        text,
        quad_points,
        title="",
        color=(1, 1, 0),
        modification_time=None,
        page=None,
    ):
        """
        Adds a text markup annotation on some quadrilateral areas of the page.

        Args:
            type (fpdf.enums.TextMarkupType, str): "Highlight", "Underline", "Squiggly" or "StrikeOut"
            text (str): text of the annotation
            quad_points (tuple): array of 8 × n numbers specifying the coordinates of n quadrilaterals
                in default user space that comprise the region in which the link should be activated.
                The coordinates for each quadrilateral are given in the order: x1 y1 x2 y2 x3 y3 x4 y4
                specifying the four vertices of the quadrilateral in counterclockwise order
            title (str): the text label that shall be displayed in the title bar of the annotation’s
                pop-up window when open and active. This entry shall identify the user who added the annotation.
            color (tuple): a tuple of numbers in the range 0.0 to 1.0, representing a colour used for
                the title bar of the annotation’s pop-up window. Defaults to yellow.
            modification_time (datetime): date and time when the annotation was most recently modified
            page (int): index of the page where this annotation is added
        """
        self._set_min_pdf_version("1.6")
        type = TextMarkupType.coerce(type).value
        if modification_time is None:
            modification_time = self.creation_date
        if page is None:
            page = self.page
        x_min = min(quad_points[0::2])
        y_min = min(quad_points[1::2])
        x_max = max(quad_points[0::2])
        y_max = max(quad_points[1::2])
        annotation = AnnotationDict(
            type,
            contents=text,
            x=y_min,
            y=y_max,
            width=x_max - x_min,
            height=y_max - y_min,
            color=color,
            modification_time=modification_time,
            title=title,
            quad_points=quad_points,
        )
        self.pages[page].annots.append(annotation)
        return annotation

    @check_page
    def ink_annotation(
        self, coords, contents="", title="", color=(1, 1, 0), border_width=1
    ):
        """
        Adds add an ink annotation on the page.

        Args:
            coords (tuple): an iterable of coordinates (pairs of numbers) defining a path
            contents (str): textual description
            title (str): the text label that shall be displayed in the title bar of the annotation’s
                pop-up window when open and active. This entry shall identify the user who added the annotation.
            color (tuple): a tuple of numbers in the range 0.0 to 1.0, representing a colour used for
                the title bar of the annotation’s pop-up window. Defaults to yellow.
            border_width (int): thickness of the path stroke.
        """
        ink_list = sum(((x * self.k, (self.h - y) * self.k) for (x, y) in coords), ())
        x_min = min(ink_list[0::2])
        y_min = min(ink_list[1::2])
        x_max = max(ink_list[0::2])
        y_max = max(ink_list[1::2])
        annotation = AnnotationDict(
            "Ink",
            x=y_min,
            y=y_max,
            width=x_max - x_min,
            height=y_max - y_min,
            ink_list=ink_list,
            color=color,
            border_width=border_width,
            contents=contents,
            title=title,
        )
        self.pages[self.page].annots.append(annotation)
        return annotation

    @check_page
    def text(self, x, y, txt=""):
        """
        Prints a character string. The origin is on the left of the first character,
        on the baseline. This method allows placing a string precisely on the page,
        but it is usually easier to use the `FPDF.cell()`, `FPDF.multi_cell() or `FPDF.write()` methods.

        Args:
            x (float): abscissa of the origin
            y (float): ordinate of the origin
            txt (str): string to print
        """
        if not self.font_family:
            raise FPDFException("No font set, you need to call set_font() beforehand")
        txt = self.normalize_text(txt)
        if self.is_ttf_font:
            txt_mapped = ""
            for char in txt:
                uni = ord(char)
                # Instead of adding the actual character to the stream its code is
                # mapped to a position in the font's subset
                txt_mapped += chr(self.current_font.subset.pick(uni))
            txt2 = escape_parens(txt_mapped.encode("utf-16-be").decode("latin-1"))
        else:
            txt2 = escape_parens(txt)
        sl = [f"BT {x * self.k:.2f} {(self.h - y) * self.k:.2f} Td"]
        if self.text_mode != TextMode.FILL:
            sl.append(f" {self.text_mode} Tr {self.line_width:.2f} w")
        sl.append(f"({txt2}) Tj ET")
        if (self.underline and txt != "") or self._record_text_quad_points:
            w = self.get_string_width(txt, normalized=True, markdown=False)
            if self.underline and txt != "":
                sl.append(self._do_underline(x, y, w))
            if self._record_text_quad_points:
                h = self.font_size
                y -= 0.8 * h  # same coefficient as in _render_styled_text_line()
                self._add_quad_points(x, y, w, h)
        attr_l = []
        if self.fill_color != self.text_color:
            attr_l.append(f"{self.text_color.serialize().lower()}")
        if attr_l:
            sl = ["q"] + attr_l + sl + ["Q"]
        self._out(" ".join(sl))

    @check_page
    def rotate(self, angle, x=None, y=None):
        """
        .. deprecated:: 2.1.0
            Use `FPDF.rotation()` instead.
        """
        warnings.warn(
            # pylint: disable=implicit-str-concat
            "rotate() can produces malformed PDFs and is deprecated. "
            "It will be removed in a future release. "
            "Use the rotation() context manager instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        if self._angle != 0:
            self._out("Q")
        self._angle = angle
        if angle != 0:
            angle *= math.pi / 180
            c = math.cos(angle)
            s = math.sin(angle)
            cx = x * self.k
            cy = (self.h - y) * self.k
            s = (
                f"q {c:.5F} {s:.5F} {-s:.5F} {c:.5F} {cx:.2F} {cy:.2F} cm "
                f"1 0 0 1 {-cx:.2F} {-cy:.2F} cm"
            )
            self._out(s)

    @check_page
    @contextmanager
    def rotation(self, angle, x=None, y=None):
        """
        Method to perform a rotation around a given center.
        It must be used as a context-manager using `with`:

            with rotation(angle=90, x=x, y=y):
                pdf.something()

        The rotation affects all elements which are printed inside the indented
        context (with the exception of clickable areas).

        Args:
            angle (float): angle in degrees
            x (float): abscissa of the center of the rotation
            y (float): ordinate of the center of the rotation

        Notes
        -----

        Only the rendering is altered. The `FPDF.get_x()` and `FPDF.get_y()` methods are
        not affected, nor the automatic page break mechanism.
        The rotation also establishes a local graphics state, so that any
        graphics state settings changed within will not affect the operations
        invoked after it has finished.
        """
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        angle *= math.pi / 180
        c, s = math.cos(angle), math.sin(angle)
        cx, cy = x * self.k, (self.h - y) * self.k
        with self.local_context():
            self._out(
                f"{c:.5F} {s:.5F} {-s:.5F} {c:.5F} {cx:.2F} {cy:.2F} cm "
                f"1 0 0 1 {-cx:.2F} {-cy:.2F} cm"
            )
            yield

    @check_page
    @contextmanager
    def skew(self, ax=0, ay=0, x=None, y=None):
        """
        Method to perform a skew transformation originating from a given center.
        It must be used as a context-manager using `with`:

            with skew(ax=15, ay=15, x=x, y=y):
                pdf.something()

        The skew transformation affects all elements which are printed inside the indented
        context (with the exception of clickable areas).

        Args:
            ax (float): angle of skew in the horizontal direction in degrees
            ay (float): angle of skew in the vertical direction in degrees
            x (float): abscissa of the center of the skew transformation
            y (float): ordinate of the center of the skew transformation
        """
        lim_val = 2**32
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        ax = max(min(math.tan(ax * (math.pi / 180)), lim_val), -lim_val)
        ay = max(min(math.tan(ay * (math.pi / 180)), lim_val), -lim_val)
        cx, cy = x * self.k, (self.h - y) * self.k
        with self.local_context():
            self._out(
                f"1 {ay:.5f} {ax:.5f} 1 {cx:.2f} {cy:.2f} cm "
                f"1 0 0 1 -{cx:.2f} -{cy:.2f} cm"
            )
            yield

    @check_page
    @contextmanager
    def mirror(self, origin, angle):
        """
        Method to perform a reflection transformation over a given mirror line.
        It must be used as a context-manager using `with`:

            with mirror(origin=(15,15), angle="SOUTH"):
                pdf.something()

        The mirror transformation affects all elements which are rendered inside the indented
        context (with the exception of clickable areas).

        Args:
            origin (float, Sequence(float, float)): a point on the mirror line
            angle: (fpdf.enums.Angle): the direction of the mirror line
        """
        x, y = origin
        try:
            theta = Angle.coerce(angle).value
        except ValueError:
            theta = angle

        a = math.cos(math.radians(theta * 2))
        b = math.sin(math.radians(theta * 2))
        cx, cy = x * self.k, (self.h - y) * self.k

        with self.local_context():
            self._out(
                f"{a:.5f} {b:.5f} {b:.5f} {a*-1:.5f} {cx:.2f} {cy:.2f} cm "
                f"1 0 0 1 -{cx:.2f} -{cy:.2f} cm"
            )
            yield

    @check_page
    @contextmanager
    def local_context(
        self,
        font_family=None,
        font_style=None,
        font_size=None,
        line_width=None,
        draw_color=None,
        fill_color=None,
        text_color=None,
        dash_pattern=None,
        **kwargs,
    ):
        """
        Creates a local graphics state, which won't affect the surrounding code.
        This method must be used as a context manager using `with`:

            with pdf.local_context():
                set_some_state()
                draw_some_stuff()

        The affected settings are those controlled by GraphicsStateMixin and drawing.GraphicsStyle:
            allow_transparency
            auto_close
            blend_mode
            dash_pattern
            draw_color
            fill_color
            fill_opacity
            font_family
            font_size
            font_style
            font_stretching
            intersection_rule
            line_width
            paint_rule
            stroke_cap_style
            stroke_join_style
            stroke_miter_limit
            stroke_opacity
            text_color
            text_mode
            underline
            char_vpos

        Args:
            **kwargs: key-values settings to set at the beggining of this context.
        """
        if self._in_unbreakable:
            raise FPDFException(
                "cannot create a local context inside an unbreakable() code block"
            )
        self._push_local_stack()
        gs = None
        for key, value in kwargs.items():
            if key in (
                "stroke_color",
                "stroke_dash_phase",
                "stroke_dash_pattern",
                "stroke_width",
            ):
                raise ValueError(
                    f"Unsupported setting: {key} - This can be controlled through dash_pattern / draw_color / line_width"
                )
            if key in drawing.GraphicsStyle.MERGE_PROPERTIES:
                if gs is None:
                    gs = drawing.GraphicsStyle()
                setattr(gs, key, value)
                if key == "blend_mode":
                    self._set_min_pdf_version("1.4")
            elif key in ("font_stretching", "text_mode", "underline", "char_vpos"):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unsupported setting: {key}")
        if gs:
            gs_name = self._drawing_graphics_state_registry.register_style(gs)
            self._out(f"q /{gs_name} gs")
        else:
            self._out("q")
        # All the following calls to .set*() methods invoke .out() and write to the stream buffer:
        if font_family is not None or font_style is not None or font_size is not None:
            self.set_font(
                font_family or self.font_family,
                font_style or self.font_style,
                font_size or self.font_size_pt,
            )
        if line_width is not None:
            self.set_line_width(line_width)
        if draw_color is not None:
            self.set_draw_color(draw_color)
        if fill_color is not None:
            self.set_fill_color(fill_color)
        if text_color is not None:
            self.set_text_color(text_color)
        if dash_pattern is not None:
            self.set_dash_pattern(**dash_pattern)
        yield
        self._out("Q")
        self._pop_local_stack()

    @property
    def accept_page_break(self):
        """
        Whenever a page break condition is met, this method is called,
        and the break is issued or not depending on the returned value.

        The default implementation returns a value according to the mode selected by `FPDF.set_auto_page_break()`.
        This method is called automatically and should not be called directly by the application.
        """
        return self.auto_page_break

    @check_page
    def cell(
        self,
        w=None,
        h=None,
        txt="",
        border=0,
        ln="DEPRECATED",
        align=Align.L,
        fill=False,
        link="",
        center="DEPRECATED",
        markdown=False,
        new_x=XPos.RIGHT,
        new_y=YPos.TOP,
    ):
        """
        Prints a cell (rectangular area) with optional borders, background color and
        character string. The upper-left corner of the cell corresponds to the current
        position. The text can be aligned or centered. After the call, the current
        position moves to the selected `new_x`/`new_y` position. It is possible to put a link
        on the text.

        If automatic page breaking is enabled and the cell goes beyond the limit, a
        page break is performed before outputting.

        Args:
            w (float): Cell width. Default value: None, meaning to fit text width.
                If 0, the cell extends up to the right margin.
            h (float): Cell height. Default value: None, meaning an height equal
                to the current font size.
            txt (str): String to print. Default value: empty string.
            border: Indicates if borders must be drawn around the cell.
                The value can be either a number (`0`: no border ; `1`: frame)
                or a string containing some or all of the following characters
                (in any order):
                `L`: left ; `T`: top ; `R`: right ; `B`: bottom. Default value: 0.
            new_x (fpdf.enums.XPos, str): New current position in x after the call. Default: RIGHT
            new_y (fpdf.enums.YPos, str): New current position in y after the call. Default: TOP
            ln (int): **DEPRECATED since 2.5.1**: Use `new_x` and `new_y` instead.
            align (fpdf.enums.Align, str): Allows to center or align the text inside the cell.
                Possible values are: `L` or empty string: left align (default value) ;
                `C`: center; `X`: center around current x; `R`: right align
            fill (bool): Indicates if the cell background must be painted (`True`)
                or transparent (`False`). Default value: False.
            link (str): optional link to add on the cell, internal
                (identifier returned by `FPDF.add_link`) or external URL.
            center (bool): **DEPRECATED** since 2.5.1:
                Use align="C" or align="X" instead.
            markdown (bool): enable minimal markdown-like markup to render part
                of text as bold / italics / underlined. Default to False.

        Returns: a boolean indicating if page break was triggered
        """
        if not self.font_family:
            raise FPDFException("No font set, you need to call set_font() beforehand")
        if isinstance(w, str) or isinstance(h, str):
            raise ValueError(
                # pylint: disable=implicit-str-concat
                "Parameter 'w' and 'h' must be numbers, not strings."
                " You can omit them by passing string content with txt="
            )
        if isinstance(border, int) and border not in (0, 1):
            warnings.warn(
                'Integer values for "border" parameter other than 1 are currently ignored'
            )
            border = 1
        new_x = XPos.coerce(new_x)
        new_y = YPos.coerce(new_y)
        if center == "DEPRECATED":
            center = False
        else:
            warnings.warn(
                'The parameter "center" is deprecated. Use align="C" or align="X" instead.',
                DeprecationWarning,
                stacklevel=3,
            )
        if ln != "DEPRECATED":
            # For backwards compatibility, if "ln" is used we overwrite "new_[xy]".
            if ln == 0:
                new_x = XPos.RIGHT
                new_y = YPos.TOP
            elif ln == 1:
                new_x = XPos.LMARGIN
                new_y = YPos.NEXT
            elif ln == 2:
                new_x = XPos.LEFT
                new_y = YPos.NEXT
            else:
                raise ValueError(
                    f'Invalid value for parameter "ln" ({ln}),'
                    " must be an int between 0 and 2."
                )
            warnings.warn(
                (
                    'The parameter "ln" is deprecated.'
                    f" Instead of ln={ln} use new_x=XPos.{new_x.name}, new_y=YPos.{new_y.name}."
                ),
                DeprecationWarning,
                stacklevel=3,
            )
        align = Align.coerce(align)
        if align == Align.J:
            raise ValueError(
                "cell() only produces one text line, justified alignment is not possible"
            )
        # Font styles preloading must be performed before any call to FPDF.get_string_width:
        txt = self.normalize_text(txt)
        styled_txt_frags = self._preload_font_styles(txt, markdown)
        return self._render_styled_text_line(
            TextLine(
                styled_txt_frags,
                text_width=0.0,
                number_of_spaces=0,
                justify=False,
                trailing_nl=False,
            ),
            w,
            h,
            border,
            new_x=new_x,
            new_y=new_y,
            align=align,
            fill=fill,
            link=link,
            center=center,
        )

    def _render_styled_text_line(
        self,
        text_line: TextLine,
        w: float = None,
        h: float = None,
        border: Union[str, int] = 0,
        new_x: XPos = XPos.RIGHT,
        new_y: YPos = YPos.TOP,
        align: Align = Align.L,
        fill: bool = False,
        link: str = "",
        center: bool = False,
    ):
        """
        Prints a cell (rectangular area) with optional borders, background color and
        character string. The upper-left corner of the cell corresponds to the current
        position. The text can be aligned, centered or justified. After the call, the
        current position moves to the requested new position. It is possible to put a
        link on the text.

        If automatic page breaking is enabled and the cell goes beyond the limit, a
        page break is performed before outputting.

        Args:
            text_line (TextLine instance): Contains the (possibly empty) tuple of
                fragments to render.
            w (float): Cell width. Default value: None, meaning to fit text width.
                If 0, the cell extends up to the right margin.
            h (float): Cell height. Default value: None, meaning an height equal
                to the current font size.
            border: Indicates if borders must be drawn around the cell.
                The value can be either a number (`0`: no border ; `1`: frame)
                or a string containing some or all of the following characters
                (in any order):
                `L`: left ; `T`: top ; `R`: right ; `B`: bottom. Default value: 0.
            new_x (fpdf.enums.XPos): New current position in x after the call.
            new_y (fpdf.enums.YPos): New current position in y after the call.
            align (fpdf.enums.Align): Allows to align the text inside the cell.
                Possible values are:
                `L` or empty string: left align (default value);
                `C`: center; `X`: center around current x; `R`: right align;
                `J`: justify (if more than one word)
            fill (bool): Indicates if the cell background must be painted (`True`)
                or transparent (`False`). Default value: False.
            link (str): optional link to add on the cell, internal
                (identifier returned by `FPDF.add_link`) or external URL.
            center (bool): **DEPRECATED since 2.5.1**: Use `align="C"` instead.
            markdown (bool): enable minimal markdown-like markup to render part
                of text as bold / italics / underlined. Default to False.

        Returns: a boolean indicating if page break was triggered
        """
        if not self.font_family:
            raise FPDFException("No font set, you need to call set_font() beforehand")
        if isinstance(border, int) and border not in (0, 1):
            warnings.warn(
                'Integer values for "border" parameter other than 1 are currently ignored'
            )
            border = 1
        styled_txt_width = text_line.text_width
        if not styled_txt_width:
            for i, frag in enumerate(text_line.fragments):
                unscaled_width = frag.get_width(initial_cs=i != 0)
                styled_txt_width += unscaled_width

        if w == 0:
            w = self.w - self.r_margin - self.x
        elif w is None:
            if not text_line.fragments:
                raise ValueError(
                    "A 'text_line' parameter with fragments must be provided if 'w' is None"
                )
            w = styled_txt_width + self.c_margin + self.c_margin
        max_font_size = 0  # how much height we need to accomodate.
        # currently all font sizes within a line are vertically aligned on the baseline.
        for frag in text_line.fragments:
            if frag.font_size > max_font_size:
                max_font_size = frag.font_size
        if h is None:
            h = max_font_size
        if align == Align.X:
            self.x -= w / 2
        if center:
            self.x = self.l_margin + (self.epw - w) / 2
        page_break_triggered = self._perform_page_break_if_need_be(h)
        sl = []
        k = self.k
        # pylint: disable=invalid-unary-operand-type
        # "h" can't actually be None
        if fill:
            op = "B" if border == 1 else "f"
            sl.append(
                f"{self.x * k:.2f} {(self.h - self.y) * k:.2f} "
                f"{w * k:.2f} {-h * k:.2f} re {op}"
            )
        elif border == 1:
            sl.append(
                f"{self.x * k:.2f} {(self.h - self.y) * k:.2f} "
                f"{w * k:.2f} {-h * k:.2f} re S"
            )
        # pylint: enable=invalid-unary-operand-type

        if isinstance(border, str):
            x = self.x
            y = self.y
            if "L" in border:
                sl.append(
                    f"{x * k:.2f} {(self.h - y) * k:.2f} m "
                    f"{x * k:.2f} {(self.h - (y + h)) * k:.2f} l S"
                )
            if "T" in border:
                sl.append(
                    f"{x * k:.2f} {(self.h - y) * k:.2f} m "
                    f"{(x + w) * k:.2f} {(self.h - y) * k:.2f} l S"
                )
            if "R" in border:
                sl.append(
                    f"{(x + w) * k:.2f} {(self.h - y) * k:.2f} m "
                    f"{(x + w) * k:.2f} {(self.h - (y + h)) * k:.2f} l S"
                )
            if "B" in border:
                sl.append(
                    f"{x * k:.2f} {(self.h - (y + h)) * k:.2f} m "
                    f"{(x + w) * k:.2f} {(self.h - (y + h)) * k:.2f} l S"
                )

        if self._record_text_quad_points:
            self._add_quad_points(self.x, self.y, w, h)

        s_start = self.x
        s_width, underlines = 0, []
        # We try to avoid modifying global settings for temporary changes.
        current_ws = frag_ws = 0.0
        current_char_vpos = CharVPos.LINE
        current_font = self.current_font
        current_text_mode = self.text_mode
        current_font_stretching = self.font_stretching
        current_char_spacing = self.char_spacing
        if text_line.fragments:
            if align == Align.R:
                dx = w - self.c_margin - styled_txt_width
            elif align in [Align.C, Align.X]:
                dx = (w - styled_txt_width) / 2
            else:
                dx = self.c_margin
            s_start += dx

            if self.fill_color != self.text_color:
                sl.append(self.text_color.serialize().lower())

            # do this once in advance
            u_space = escape_parens(" ".encode("utf-16-be").decode("latin-1"))
            word_spacing = 0
            if text_line.justify:
                # Don't rely on align==Align.J here.
                # If a line gets broken by an explicit '\n', then MultiLineBreak
                # will set its justify to False (end of paragraph).
                word_spacing = (
                    w - self.c_margin - self.c_margin - styled_txt_width
                ) / text_line.number_of_spaces

            sl.append(
                f"BT {(self.x + dx) * k:.2f} "
                f"{(self.h - self.y - 0.5 * h - 0.3 * max_font_size) * k:.2f} Td"
            )
            for i, frag in enumerate(text_line.fragments):
                if word_spacing and frag.font_stretching != 100:
                    # Space character is already stretched, extra spacing is absolute.
                    frag_ws = word_spacing * 100 / frag.font_stretching
                else:
                    frag_ws = word_spacing
                if current_font_stretching != frag.font_stretching:
                    current_font_stretching = frag.font_stretching
                    sl.append(f"{frag.font_stretching:.2f} Tz")
                if current_char_spacing != frag.char_spacing:
                    current_char_spacing = frag.char_spacing
                    sl.append(f"{frag.char_spacing:.2f} Tc")
                if current_font != frag.font or current_char_vpos != frag.char_vpos:
                    if current_char_vpos != frag.char_vpos:
                        current_char_vpos = frag.char_vpos
                    current_font = frag.font
                    sl.append(f"/F{frag.font.i} {frag.font_size_pt:.2f} Tf")
                lift = frag.lift
                if lift != 0.0:
                    sl.append(f"{lift:.2f} Ts")
                if (
                    frag.text_mode != TextMode.FILL
                    or frag.text_mode != current_text_mode
                ):
                    current_text_mode = frag.text_mode
                    sl.append(f"{frag.text_mode} Tr {frag.line_width:.2f} w")

                if frag.is_ttf_font:
                    mapped_text = ""
                    for char in frag.string:
                        uni = ord(char)
                        mapped_text += chr(frag.font.subset.pick(uni))
                    if word_spacing:
                        # "Tw" only has an effect on the ASCII space character and ignores
                        # space characters from unicode (TTF) fonts. As a workaround,
                        # we do word spacing using an adjustment before each space.
                        # Determine the index of the space character (" ") in the current
                        # subset and split words whenever this mapping code is found
                        words = mapped_text.split(chr(frag.font.subset.pick(ord(" "))))
                        words_strl = []
                        for word_i, word in enumerate(words):
                            # pylint: disable=redefined-loop-name
                            word = escape_parens(
                                word.encode("utf-16-be").decode("latin-1")
                            )
                            if word_i == 0:
                                words_strl.append(f"({word})")
                            else:
                                adj = -(frag_ws * frag.k) * 1000 / frag.font_size_pt
                                words_strl.append(f"{adj:.3f}({u_space}{word})")
                        escaped_text = " ".join(words_strl)
                        sl.append(f"[{escaped_text}] TJ")
                    else:
                        escaped_text = escape_parens(
                            mapped_text.encode("utf-16-be").decode("latin-1")
                        )
                        sl.append(f"({escaped_text}) Tj")
                else:  # core fonts
                    if frag_ws != current_ws:
                        sl.append(f"{frag_ws * frag.k:.3f} Tw")
                        current_ws = frag_ws
                    escaped_text = escape_parens(frag.string)
                    sl.append(f"({escaped_text}) Tj")
                frag_width = frag.get_width(
                    initial_cs=i != 0
                ) + word_spacing * frag.characters.count(" ")
                if frag.underline:
                    underlines.append(
                        (self.x + dx + s_width, frag_width, frag.font, frag.font_size)
                    )
                if frag.url:
                    self.link(
                        x=self.x + dx + s_width,
                        y=self.y + (0.5 * h) - (0.5 * frag.font_size),
                        w=frag_width,
                        h=frag.font_size,
                        link=frag.url,
                    )
                s_width += frag_width

            sl.append("ET")

            for start_x, ul_w, ul_font, ul_font_size in underlines:
                sl.append(
                    self._do_underline(
                        start_x,
                        self.y + (0.5 * h) + (0.3 * ul_font_size),
                        ul_w,
                        ul_font,
                    )
                )
            if link:
                self.link(
                    self.x + dx,
                    self.y + (0.5 * h) - (0.5 * frag.font_size),
                    styled_txt_width,
                    frag.font_size,
                    link,
                )

        if sl:
            # If any PDF settings have been left modified, wrap the line
            # in a local context.
            # pylint: disable=too-many-boolean-expressions
            if (
                current_ws != 0.0
                or current_char_vpos != CharVPos.LINE
                or current_font != self.current_font
                or current_text_mode != self.text_mode
                or self.fill_color != self.text_color
                or current_font_stretching != self.font_stretching
                or current_char_spacing != self.char_spacing
            ):
                s = f"q {' '.join(sl)} Q"
            else:
                s = " ".join(sl)
            # pylint: enable=too-many-boolean-expressions
            self._out(s)
        # If the text is empty, h = max_font_size ends up as 0.
        # We still need a valid default height for self.ln() (issue #601).
        self._lasth = h or self.font_size

        # XPos.LEFT -> self.x stays the same
        if new_x == XPos.RIGHT:
            self.x += w
        elif new_x == XPos.START:
            self.x = s_start
        elif new_x == XPos.END:
            self.x = s_start + s_width
        elif new_x == XPos.WCONT:
            self.x = s_start + s_width - self.c_margin
        elif new_x == XPos.CENTER:
            self.x = s_start + s_width / 2.0
        elif new_x == XPos.LMARGIN:
            self.x = self.l_margin
        elif new_x == XPos.RMARGIN:
            self.x = self.w - self.r_margin

        # YPos.TOP:  -> self.y stays the same
        # YPos.LAST: -> self.y stays the same (single line)
        if new_y == YPos.NEXT:
            self.y += h
        if new_y == YPos.TMARGIN:
            self.y = self.t_margin
        if new_y == YPos.BMARGIN:
            self.y = self.h - self.b_margin

        return page_break_triggered

    def _add_quad_points(self, x, y, w, h):
        self._text_quad_points[self.page].extend(
            [
                x * self.k,
                (self.h - y) * self.k,
                (x + w) * self.k,
                (self.h - y) * self.k,
                x * self.k,
                (self.h - y - h) * self.k,
                (x + w) * self.k,
                (self.h - y - h) * self.k,
            ]
        )

    def _preload_font_styles(self, txt, markdown):
        """
        When Markdown styling is enabled, we require secondary fonts
        to ender text in bold & italics.
        This function ensure that those fonts are available.
        It needs to perform Markdown parsing,
        so we return the resulting `styled_txt_frags` tuple
        to avoid repeating this processing later on.
        """
        if not txt:
            return tuple()
        if not markdown:
            return self._parse_chars(txt)
        prev_font_style = self.font_style
        styled_txt_frags = tuple(self._markdown_parse(txt))
        page = self.page
        # We set the current to page to zero so that
        # set_font() does not produce any text object on the stream buffer:
        self.page = 0
        if any("B" in frag.font_style for frag in styled_txt_frags):
            # Ensuring bold font is supported:
            self.set_font(style="B")
        if any("I" in frag.font_style for frag in styled_txt_frags):
            # Ensuring italics font is supported:
            self.set_font(style="I")
        for frag in styled_txt_frags:
            frag.font = self.fonts[frag.font_family + frag.font_style]
        # Restoring initial style:
        self.set_font(style=prev_font_style)
        self.page = page
        return styled_txt_frags

    def _parse_chars(self, txt):
        "Check if the font has all the necessary glyphs. If a glyph from a fallback font is used, break into fragments"
        fragments = []
        txt_frag = []
        if not self.is_ttf_font or not self._fallback_font_ids:
            return tuple([Fragment(txt, self._get_current_graphics_state(), self.k)])
        font_glyphs = self.current_font.cmap
        for char in txt:
            if char == "\n" or ord(char) in font_glyphs:
                txt_frag.append(char)
            else:
                if txt_frag:
                    fragments.append(
                        Fragment(txt_frag, self._get_current_graphics_state(), self.k)
                    )
                    txt_frag = []
                fallback_font = self.get_fallback_font(char, self.font_style)
                if fallback_font:
                    gstate = self._get_current_graphics_state()
                    gstate["font_family"] = fallback_font
                    frag = Fragment(char, gstate, self.k)
                    frag.font = self.fonts[fallback_font]
                    fragments.append(frag)
                else:
                    # no fallback font has this character.
                    # add it anyway with the current font
                    txt_frag.append(char)
        if txt_frag:
            fragments.append(
                Fragment(txt_frag, self._get_current_graphics_state(), self.k)
            )
        return tuple(fragments)

    def get_fallback_font(self, char, style=""):
        """
        Returns which fallback font has the requested glyph.
        This method can be overriden to provide more control than the `select_mode` parameter
        of `FPDF.set_fallback_fonts()` provides.
        """
        emphasis = TextEmphasis.coerce(style)
        fonts_with_char = [
            font_id
            for font_id in self._fallback_font_ids
            if ord(char) in self.fonts[font_id].cmap
        ]
        if not fonts_with_char:
            return None
        font_with_matching_emphasis = next(
            (font for font in fonts_with_char if self.fonts[font].emphasis == emphasis),
            None,
        )
        if font_with_matching_emphasis:
            return font_with_matching_emphasis
        if self._fallback_font_exact_match:
            return None
        return fonts_with_char[0]

    def _markdown_parse(self, txt):
        "Split some text into fragments based on styling: **bold**, __italics__, --underlined--"
        txt_frag, in_bold, in_italics, in_underline = (
            [],
            "B" in self.font_style,
            "I" in self.font_style,
            bool(self.underline),
        )

        def frag():
            gstate = self._get_current_graphics_state()
            gstate["font_style"] = ("B" if in_bold else "") + (
                "I" if in_italics else ""
            )
            gstate["underline"] = in_underline
            nonlocal txt_frag
            fragment = Fragment(txt_frag, gstate, self.k)
            txt_frag = []
            return fragment

        if self.is_ttf_font:
            font_glyphs = self.current_font.cmap
        else:
            font_glyphs = []

        while txt:
            is_marker = txt[:2] in (
                self.MARKDOWN_BOLD_MARKER,
                self.MARKDOWN_ITALICS_MARKER,
                self.MARKDOWN_UNDERLINE_MARKER,
            )
            half_marker = txt[0]
            # Check that previous & next characters are not identical to the marker:
            if (
                is_marker
                and (not txt_frag or txt_frag[0] != half_marker)
                and (len(txt) < 3 or txt[2] != half_marker)
            ):
                if txt_frag:
                    yield frag()
                if txt[:2] == self.MARKDOWN_BOLD_MARKER:
                    in_bold = not in_bold
                if txt[:2] == self.MARKDOWN_ITALICS_MARKER:
                    in_italics = not in_italics
                if txt[:2] == self.MARKDOWN_UNDERLINE_MARKER:
                    in_underline = not in_underline
                txt = txt[2:]
                continue
            is_link = self.MARKDOWN_LINK_REGEX.match(txt)
            if is_link:
                link_text, link_url, txt = is_link.groups()
                if txt_frag:
                    yield frag()
                gstate = self._get_current_graphics_state()
                gstate["underline"] = True
                if self.MARKDOWN_LINK_COLOR:
                    gstate["text_color"] = self.MARKDOWN_LINK_COLOR
                yield Fragment(list(link_text), gstate, self.k, url=link_url)
                continue
            if self.is_ttf_font and txt[0] != "\n" and not ord(txt[0]) in font_glyphs:
                style = ("B" if in_bold else "") + ("I" if in_italics else "")
                fallback_font = self.get_fallback_font(txt[0], style)
                if fallback_font:
                    if txt_frag:
                        yield frag()
                    gstate = self._get_current_graphics_state()
                    gstate["font_family"] = fallback_font
                    yield Fragment(txt[0], gstate, self.k)
                    txt = txt[1:]
                    continue
            txt_frag.append(txt[0])
            txt = txt[1:]
        if txt_frag:
            yield frag()

    def will_page_break(self, height):
        """
        Let you know if adding an element will trigger a page break,
        based on its height and the current ordinate (`y` position).

        Args:
            height (float): height of the section that would be added, e.g. a cell

        Returns: a boolean indicating if a page break would occur
        """
        return (
            # ensure that there is already some content on the page:
            self.y > self.t_margin
            and self.y + height > self.page_break_trigger
            and not self.in_footer
            and self.accept_page_break
        )

    def _perform_page_break_if_need_be(self, h):
        if self.will_page_break(h):
            LOGGER.debug(
                "Page break on page %d at y=%d for element of height %d > %d",
                self.page,
                self.y,
                h,
                self.page_break_trigger,
            )
            self._perform_page_break()
            return True
        return False

    def _perform_page_break(self):
        x = self.x
        self.add_page(same=True)
        self.x = x  # restore x but not y after drawing header

    def _has_next_page(self):
        return self.pages_count > self.page

    @contextmanager
    def _disable_writing(self):
        self._out = lambda *args, **kwargs: None
        prev_page, prev_x, prev_y = self.page, self.x, self.y
        self._push_local_stack()
        try:
            yield
        finally:
            self._pop_local_stack()
            # restore location:
            for p in range(prev_page + 1, self.page + 1):
                del self.pages[p]
            self.page = prev_page
            self.set_xy(prev_x, prev_y)
            # restore writing function:
            del self._out

    @check_page
    def multi_cell(
        self,
        w,
        h=None,
        txt="",
        border=0,
        align=Align.J,
        fill=False,
        split_only=False,  # DEPRECATED
        link="",
        ln="DEPRECATED",
        max_line_height=None,
        markdown=False,
        print_sh=False,
        new_x=XPos.RIGHT,
        new_y=YPos.NEXT,
        wrapmode: WrapMode = WrapMode.WORD,
        dry_run=False,
        output=MethodReturnValue.PAGE_BREAK,
    ):
        """
        This method allows printing text with line breaks. They can be automatic
        (breaking at the most recent space or soft-hyphen character) as soon as the text
        reaches the right border of the cell, or explicit (via the `\\n` character).
        As many cells as necessary are stacked, one below the other.
        Text can be aligned, centered or justified. The cell block can be framed and
        the background painted.

        Args:
            w (float): cell width. If 0, they extend up to the right margin of the page.
            h (float): cell height. Default value: None, meaning to use the current font size.
            txt (str): string to print.
            border: Indicates if borders must be drawn around the cell.
                The value can be either a number (`0`: no border ; `1`: frame)
                or a string containing some or all of the following characters
                (in any order):
                `L`: left ; `T`: top ; `R`: right ; `B`: bottom. Default value: 0.
            align (fpdf.enums.Align, str): Allows to center or align the text.
                Possible values are:
                `J`: justify (default value); `L` or empty string: left align;
                `C`: center; `X`: center around current x; `R`: right align
            fill (bool): Indicates if the cell background must be painted (`True`)
                or transparent (`False`). Default value: False.
            split_only (bool): **DEPRECATED since 2.7.4**:
                Use `dry_run=True` and `output=("LINES",)` instead.
            link (str): optional link to add on the cell, internal
                (identifier returned by `add_link`) or external URL.
            new_x (fpdf.enums.XPos, str): New current position in x after the call. Default: RIGHT
            new_y (fpdf.enums.YPos, str): New current position in y after the call. Default: NEXT
            ln (int): **DEPRECATED since 2.5.1**: Use `new_x` and `new_y` instead.
            max_line_height (float): optional maximum height of each sub-cell generated
            markdown (bool): enable minimal markdown-like markup to render part
                of text as bold / italics / underlined. Default to False.
            print_sh (bool): Treat a soft-hyphen (\\u00ad) as a normal printable
                character, instead of a line breaking opportunity. Default value: False
            wrapmode (fpdf.enums.WrapMode): "WORD" for word based line wrapping (default),
                "CHAR" for character based line wrapping.
            dry_run (bool): if `True`, does not output anything in the document.
                Can be useful when combined with `output`.
            output (fpdf.enums.MethodReturnValue): defines what this method returns.
                If several enum values are joined, the result will be a tuple.

        Using `new_x=XPos.RIGHT, new_y=XPos.TOP, maximum height=pdf.font_size` is
        useful to build tables with multiline text in cells.

        Returns: a single value or a tuple, depending on the `output` parameter value
        """
        if split_only:
            warnings.warn(
                # pylint: disable=implicit-str-concat
                'The parameter "split_only" is deprecated.'
                ' Use instead dry_run=True and output="LINES".',
                DeprecationWarning,
                stacklevel=3,
            )
        if dry_run or split_only:
            with self._disable_writing():
                return self.multi_cell(
                    w=w,
                    h=h,
                    txt=txt,
                    border=border,
                    align=align,
                    fill=fill,
                    link=link,
                    ln=ln,
                    max_line_height=max_line_height,
                    markdown=markdown,
                    print_sh=print_sh,
                    new_x=new_x,
                    new_y=new_y,
                    wrapmode=wrapmode,
                    dry_run=False,
                    split_only=False,
                    output=MethodReturnValue.LINES if split_only else output,
                )
        wrapmode = WrapMode.coerce(wrapmode)
        if isinstance(w, str) or isinstance(h, str):
            raise ValueError(
                # pylint: disable=implicit-str-concat
                "Parameter 'w' and 'h' must be numbers, not strings."
                " You can omit them by passing string content with txt="
            )
        new_x = XPos.coerce(new_x)
        new_y = YPos.coerce(new_y)
        if ln != "DEPRECATED":
            # For backwards compatibility, if "ln" is used we overwrite "new_[xy]".
            if ln == 0:
                new_x = XPos.RIGHT
                new_y = YPos.NEXT
            elif ln == 1:
                new_x = XPos.LMARGIN
                new_y = YPos.NEXT
            elif ln == 2:
                new_x = XPos.LEFT
                new_y = YPos.NEXT
            elif ln == 3:
                new_x = XPos.RIGHT
                new_y = YPos.TOP
            else:
                raise ValueError(
                    f'Invalid value for parameter "ln" ({ln}),'
                    " must be an int between 0 and 3."
                )
            warnings.warn(
                (
                    'The parameter "ln" is deprecated.'
                    f" Instead of ln={ln} use new_x=XPos.{new_x.name}, new_y=YPos.{new_y.name}."
                ),
                DeprecationWarning,
                stacklevel=3,
            )
        align = Align.coerce(align)

        page_break_triggered = False

        if h is None:
            h = self.font_size
        # If width is 0, set width to available width between margins
        if w == 0:
            w = self.w - self.r_margin - self.x
        maximum_allowed_width = w - 2 * self.c_margin

        # Calculate text length
        txt = self.normalize_text(txt)
        normalized_string = txt.replace("\r", "")
        styled_text_fragments = self._preload_font_styles(normalized_string, markdown)

        prev_font_style, prev_underline = self.font_style, self.underline
        prev_x, prev_y = self.x, self.y
        total_height = 0

        if not border:
            border = ""
        elif border == 1:
            border = "LTRB"

        text_lines = []
        multi_line_break = MultiLineBreak(
            styled_text_fragments,
            justify=(align == Align.J),
            print_sh=print_sh,
            wrapmode=wrapmode,
        )
        txt_line = multi_line_break.get_line_of_given_width(maximum_allowed_width)
        while (txt_line) is not None:
            text_lines.append(txt_line)
            txt_line = multi_line_break.get_line_of_given_width(maximum_allowed_width)

        if not text_lines:  # ensure we display at least one cell - cf. issue #349
            text_lines = [
                TextLine(
                    "",
                    text_width=0,
                    number_of_spaces=0,
                    justify=False,
                    trailing_nl=False,
                )
            ]
        should_render_bottom_blank_cell = False
        for text_line_index, text_line in enumerate(text_lines):
            is_last_line = text_line_index == len(text_lines) - 1
            should_render_bottom_blank_cell = False
            if max_line_height is not None and h > max_line_height:
                current_cell_height = max_line_height
                h -= current_cell_height
                if is_last_line:
                    if h > 0 and len(text_lines) > 1:
                        should_render_bottom_blank_cell = True
                    else:
                        h += current_cell_height
                        current_cell_height = h
            else:
                current_cell_height = h
            has_line_after = not is_last_line or should_render_bottom_blank_cell
            new_page = self._render_styled_text_line(
                text_line,
                w,
                h=current_cell_height,
                border="".join(
                    (
                        "T" if "T" in border and text_line_index == 0 else "",
                        "L" if "L" in border else "",
                        "R" if "R" in border else "",
                        "B" if "B" in border and not has_line_after else "",
                    )
                ),
                new_x=new_x if not has_line_after else XPos.LEFT,
                new_y=new_y if not has_line_after else YPos.NEXT,
                align=Align.L if (align == Align.J and is_last_line) else align,
                fill=fill,
                link=link,
            )
            page_break_triggered = page_break_triggered or new_page
            total_height += current_cell_height
            if not is_last_line and align == Align.X:
                # prevent cumulative shift to the left
                self.x = prev_x
        if should_render_bottom_blank_cell:
            new_page = self._render_styled_text_line(
                TextLine(
                    "",
                    text_width=0,
                    number_of_spaces=0,
                    justify=False,
                    trailing_nl=False,
                ),
                w,
                h=h,
                border="".join(
                    (
                        "L" if "L" in border else "",
                        "R" if "R" in border else "",
                        "B" if "B" in border else "",
                    )
                ),
                new_x=new_x,
                new_y=new_y,
                fill=fill,
                link=link,
            )
            page_break_triggered = page_break_triggered or new_page
        if new_page and new_y == YPos.TOP:
            # When a page jump is performed and the requested y is TOP,
            # pretend we started at the top of the text block on the new page.
            # cf. test_multi_cell_table_with_automatic_page_break
            prev_y = self.y
        # pylint: disable=undefined-loop-variable
        if text_line and text_line.trailing_nl and new_y in (YPos.LAST, YPos.NEXT):
            # The line renderer can't handle trailing newlines in the text.
            self.ln()

        if new_y == YPos.TOP:  # We may have jumped a few lines -> reset
            self.y = prev_y

        if markdown:
            if self.font_style != prev_font_style:
                self.font_style = prev_font_style
                self.current_font = self.fonts[self.font_family + self.font_style]
            self.underline = prev_underline

        output = MethodReturnValue.coerce(output)
        return_value = ()
        if output & MethodReturnValue.PAGE_BREAK:
            return_value += (page_break_triggered,)
        if output & MethodReturnValue.LINES:
            output_lines = []
            for text_line in text_lines:
                characters = []
                for frag in text_line.fragments:
                    characters.extend(frag.characters)
                output_lines.append("".join(characters))
            return_value += (output_lines,)
        if output & MethodReturnValue.HEIGHT:
            return_value += (total_height,)
        if len(return_value) == 1:
            return return_value[0]
        return return_value

    @check_page
    def write(
        self,
        h: float = None,
        txt: str = "",
        link: str = "",
        print_sh: bool = False,
        wrapmode: WrapMode = WrapMode.WORD,
    ):
        """
        Prints text from the current position.
        When the right margin is reached, a line break occurs at the most recent
        space or soft-hyphen character, and text continues from the left margin.
        A manual break happens any time the \\n character is met,
        Upon method exit, the current position is left just at the end of the text.

        Args:
            h (float): line height. Default value: None, meaning to use the current font size.
            txt (str): text content
            link (str): optional link to add on the text, internal
                (identifier returned by `FPDF.add_link`) or external URL.
            print_sh (bool): Treat a soft-hyphen (\\u00ad) as a normal printable
                character, instead of a line breaking opportunity. Default value: False
            wrapmode (fpdf.enums.WrapMode): "WORD" for word based line wrapping (default),
                "CHAR" for character based line wrapping.
        """
        wrapmode = WrapMode.coerce(wrapmode)
        if not self.font_family:
            raise FPDFException("No font set, you need to call set_font() beforehand")
        if isinstance(h, str):
            raise ValueError(
                # pylint: disable=implicit-str-concat
                "Parameter 'h' must be a number, not a string."
                " You can omit it by passing string content with txt="
            )
        if h is None:
            h = self.font_size

        page_break_triggered = False
        normalized_string = self.normalize_text(txt).replace("\r", "")
        styled_text_fragments = self._preload_font_styles(normalized_string, False)

        text_lines = []
        multi_line_break = MultiLineBreak(
            styled_text_fragments,
            print_sh=print_sh,
            wrapmode=wrapmode,
        )
        # first line from current x position to right margin
        first_width = self.w - self.x - self.r_margin
        txt_line = multi_line_break.get_line_of_given_width(
            first_width - 2 * self.c_margin, wordsplit=False
        )
        # remaining lines fill between margins
        full_width = self.w - self.l_margin - self.r_margin
        fit_width = full_width - 2 * self.c_margin
        while txt_line is not None:
            text_lines.append(txt_line)
            txt_line = multi_line_break.get_line_of_given_width(fit_width)
        if not text_lines:
            return False

        for text_line_index, text_line in enumerate(text_lines):
            if text_line_index == 0:
                line_width = first_width
            else:
                line_width = full_width
                self.ln()
            new_page = self._render_styled_text_line(
                text_line,
                line_width,
                h=h,
                border=0,
                new_x=XPos.WCONT,
                new_y=YPos.TOP,
                align=Align.L,
                fill=False,
                link=link,
            )
            page_break_triggered = page_break_triggered or new_page
        # pylint: disable=undefined-loop-variable
        if text_line.trailing_nl:
            # The line renderer can't handle trailing newlines in the text.
            self.ln()
        return page_break_triggered

    @check_page
    def image(
        self,
        name,
        x=None,
        y=None,
        w=0,
        h=0,
        type="",
        link="",
        title=None,
        alt_text=None,
        dims=None,
        keep_aspect_ratio=False,
    ):
        """
        Put an image on the page.

        The size of the image on the page can be specified in different ways:
        * explicit width and height (expressed in user units)
        * one explicit dimension, the other being calculated automatically
          in order to keep the original proportions
        * no explicit dimension, in which case the image is put at 72 dpi.
        * explicit width and height (expressed in user units) and `keep_aspect_ratio=True`

        **Remarks**:
        * if an image is used several times, only one copy is embedded in the file.
        * when using an animated GIF, only the first frame is used.

        Args:
            name: either a string representing a file path to an image, an URL to an image,
                bytes, an io.BytesIO, or a instance of `PIL.Image.Image`
            x (float, fpdf.enums.Align): optional horizontal position where to put the image on the page.
                If not specified or equal to None, the current abscissa is used.
                `Align.C` can also be passed to center the image horizontally;
                and `Align.R` to place it along the right page margin
            y (float): optional vertical position where to put the image on the page.
                If not specified or equal to None, the current ordinate is used.
                After the call, the current ordinate is moved to the bottom of the image
            w (float): optional width of the image. If not specified or equal to zero,
                it is automatically calculated from the image size.
                Pass `pdf.epw` to scale horizontally to the full page width.
            h (float): optional height of the image. If not specified or equal to zero,
                it is automatically calculated from the image size.
                Pass `pdf.eph` to scale horizontally to the full page height.
            type (str): [**DEPRECATED since 2.2.0**] unused, will be removed in a later version.
            link (str): optional link to add on the image, internal
                (identifier returned by `FPDF.add_link`) or external URL.
            title (str): optional. Currently, never seem rendered by PDF readers.
            alt_text (str): optional alternative text describing the image,
                for accessibility purposes. Displayed by some PDF readers on hover.
            dims (Tuple[float]): optional dimensions as a tuple (width, height) to resize the image
                before storing it in the PDF. Note that those are the **intrinsic** image dimensions,
                but the image will still be rendered on the page with the width (`w`) and height (`h`)
                provided as parameters. Note also that the `.oversized_images` attribute of FPDF
                provides an automated way to auto-adjust those intrinsic image dimensions.
            keep_aspect_ratio (bool): ensure the image fits in the rectangle defined by `x`, `y`, `w` & `h`
                while preserving its original aspect ratio. Defaults to False.
                Only meaningful if both `w` & `h` are provided.

        Returns: an instance of `ImageInfo`
        """
        if type:
            warnings.warn(
                '"type" parameter is deprecated, unused and will soon be removed',
                DeprecationWarning,
                stacklevel=3,
            )
        if str(name).endswith(".svg"):
            # Insert it as a PDF path:
            img = load_image(str(name))
            return self._vector_image(img, x, y, w, h, link, title, alt_text)
        if isinstance(name, bytes) and _is_svg(name.strip()):
            return self._vector_image(
                io.BytesIO(name), x, y, w, h, link, title, alt_text
            )
        if isinstance(name, io.BytesIO) and _is_svg(name.getvalue().strip()):
            return self._vector_image(name, x, y, w, h, link, title, alt_text)
        name, img, info = self.preload_image(name, dims)
        if "smask" in info:
            self._set_min_pdf_version("1.4")

        # Automatic width and height calculation if needed
        if w == 0 and h == 0:  # Put image at 72 dpi
            w = info["w"] / self.k
            h = info["h"] / self.k
        elif w == 0:
            w = h * info["w"] / info["h"]
        elif h == 0:
            h = w * info["h"] / info["w"]

        if self.oversized_images and info["usages"] == 1 and not dims:
            info = self._downscale_image(name, img, info, w, h)

        # Flowing mode
        if y is None:
            self._perform_page_break_if_need_be(h)
            y = self.y
            self.y += h
        if x is None:
            x = self.x

        if keep_aspect_ratio:
            ratio = info.width / info.height
            if h * ratio < w:
                x += (w - h * ratio) / 2
                w = h * ratio
            else:  # => too wide, limiting width:
                y += (h - w / ratio) / 2
                h = w / ratio

        if not isinstance(x, Number):
            if keep_aspect_ratio:
                raise ValueError(
                    "FPDF.image(): 'keep_aspect_ratio' cannot be used with an enum value provided to `x`"
                )
            x = Align.coerce(x)
            if x == Align.C:
                x = (self.w - w) / 2
            elif x == Align.R:
                x = self.w - w - self.r_margin
            elif x == Align.L:
                x = self.l_margin
            else:
                raise ValueError(f"Unsupported 'x' value passed to .image(): {x}")

        stream_content = (
            f"q {w * self.k:.2f} 0 0 {h * self.k:.2f} {x * self.k:.2f} "
            f"{(self.h - y - h) * self.k:.2f} cm /I{info['i']} Do Q"
        )
        if title or alt_text:
            with self._marked_sequence(title=title, alt_text=alt_text):
                self._out(stream_content)
        else:
            self._out(stream_content)
        if link:
            self.link(x, y, w, h, link)

        return ImageInfo(**info, rendered_width=w, rendered_height=h)

    def preload_image(self, name, dims=None):
        """
        Read a raster (= non-vector) image and loads it in memory in this FPDF instance.
        Following this call, the image is inserted in `.images`,
        and following calls to this method (or `FPDF.image`) will return (or re-use)
        the same cached values, without re-reading the image.

        Args:
            name: either a string representing a file path to an image, an URL to an image,
                an io.BytesIO, or a instance of `PIL.Image.Image`
            dims (Tuple[float]): optional dimensions as a tuple (width, height) to resize the image
                before storing it in the PDF.

        Returns: an instance of `ImageInfo`
        """
        if isinstance(name, str):
            img = None
        elif isinstance(name, Image):
            bytes_ = name.tobytes()
            img_hash = hashlib.new("md5", usedforsecurity=False)  # nosec B324
            img_hash.update(bytes_)
            name, img = img_hash.hexdigest(), name
        elif isinstance(name, (bytes, io.BytesIO)):
            bytes_ = name.getvalue() if isinstance(name, io.BytesIO) else name
            bytes_ = bytes_.strip()
            img_hash = hashlib.new("md5", usedforsecurity=False)  # nosec B324
            img_hash.update(bytes_)
            name, img = img_hash.hexdigest(), name
        else:
            name, img = str(name), name
        info = self.images.get(name)
        if info:
            info["usages"] += 1
        else:
            info = ImageInfo(get_img_info(name, img, self.image_filter, dims))
            info["i"] = len(self.images) + 1
            info["usages"] = 1
            info["iccp_i"] = None
            iccp = info.get("iccp")
            if iccp:
                LOGGER.debug(
                    "ICC profile found for image %s - It will be inserted in the PDF document",
                    name,
                )
                if iccp in self.icc_profiles:
                    info["iccp_i"] = self.icc_profiles[iccp]
                else:
                    iccp_i = len(self.icc_profiles)
                    self.icc_profiles[iccp] = iccp_i
                    info["iccp_i"] = iccp_i
                info["iccp"] = None
            self.images[name] = info
        return name, img, info

    def _vector_image(
        self,
        img: io.BytesIO,
        x=None,
        y=None,
        w=0,
        h=0,
        link="",
        title=None,
        alt_text=None,
    ):
        svg = SVGObject(img.getvalue())
        if not svg.viewbox and svg.width and svg.height:
            warnings.warn(
                '<svg> has no "viewBox", using its "width" & "height" as default "viewBox"'
            )
            svg.viewbox = 0, 0, svg.width, svg.height
        if w == 0 and h == 0:
            if svg.width and svg.height:
                w = (
                    svg.width * self.epw / 100
                    if isinstance(svg.width, Percent)
                    else svg.width
                )
                h = (
                    svg.height * self.eph / 100
                    if isinstance(svg.height, Percent)
                    else svg.height
                )
            elif svg.viewbox:
                _, _, w, h = svg.viewbox
            else:
                raise ValueError(
                    '<svg> has no "viewBox" nor "height" / "width": w= and h= must be provided to FPDF.image()'
                )
        elif w == 0 or h == 0:
            if svg.width and svg.height:
                svg_width, svg_height = svg.width, svg.height
            elif svg.viewbox:
                _, _, svg_width, svg_height = svg.viewbox
            else:
                raise ValueError(
                    '<svg> has no "viewBox" nor "height" / "width": w= and h= must be provided to FPDF.image()'
                )
            if w == 0:
                w = h * svg_width / svg_height
            else:  # h == 0
                h = w * svg_height / svg_width

        # Flowing mode
        if y is None:
            self._perform_page_break_if_need_be(h)
            y = self.y
            self.y += h
        if x is None:
            x = self.x

        _, _, path = svg.transform_to_rect_viewport(
            scale=1, width=w, height=h, ignore_svg_top_attrs=True
        )
        path.transform = path.transform @ drawing.Transform.translation(x, y)

        old_x, old_y = self.x, self.y
        try:
            self.set_xy(0, 0)
            if title or alt_text:
                with self._marked_sequence(title=title, alt_text=alt_text):
                    self.draw_path(path)
            else:
                self.draw_path(path)
        finally:
            self.set_xy(old_x, old_y)
        if link:
            self.link(x, y, w, h, link)

        return ImageInfo(rendered_width=w, rendered_height=h)

    def _downscale_image(self, name, img, info, w, h):
        width_in_pt, height_in_pt = w * self.k, h * self.k
        lowres_name = f"lowres-{name}"
        lowres_info = self.images.get(lowres_name)
        if (
            info["w"] > width_in_pt * self.oversized_images_ratio
            and info["h"] > height_in_pt * self.oversized_images_ratio
        ):
            factor = (
                min(info["w"] / width_in_pt, info["h"] / height_in_pt)
                / self.oversized_images_ratio
            )
            if self.oversized_images.lower().startswith("warn"):
                LOGGER.warning(
                    # pylint: disable=implicit-str-concat
                    "OVERSIZED: Image %s with size %.1fx%.1fpx is rendered at size %.1fx%.1fpt."
                    " Set pdf.oversized_images = 'DOWNSCALE' to reduce embedded image size by a factor %.1f",
                    name,
                    info["w"],
                    info["h"],
                    width_in_pt,
                    height_in_pt,
                    factor,
                )
            elif self.oversized_images.lower() == "downscale":
                dims = (
                    round(width_in_pt * self.oversized_images_ratio),
                    round(height_in_pt * self.oversized_images_ratio),
                )
                info["usages"] -= 1  # no need to embed the high-resolution image
                if lowres_info:  # Great, we've already done the job!
                    info = lowres_info
                    if info["w"] * info["h"] < dims[0] * dims[1]:
                        # The existing low-res image is too small, we need a bigger low-res image:
                        info.update(
                            get_img_info(
                                name, img or load_image(name), self.image_filter, dims
                            )
                        )
                        LOGGER.debug(
                            "OVERSIZED: Updated low-res image with name=%s id=%d to dims=%s",
                            lowres_name,
                            info["i"],
                            dims,
                        )
                    info["usages"] += 1
                else:
                    info = ImageInfo(
                        get_img_info(
                            name, img or load_image(name), self.image_filter, dims
                        )
                    )
                    info["i"] = len(self.images) + 1
                    info["usages"] = 1
                    self.images[lowres_name] = info
                    LOGGER.debug(
                        "OVERSIZED: Generated new low-res image with name=%s dims=%s id=%d",
                        lowres_name,
                        dims,
                        info["i"],
                    )
            else:
                raise ValueError(
                    f"Invalid value for attribute .oversized_images: {self.oversized_images}"
                )
        elif lowres_info:
            # Embedding the same image in high-res after inserting it in low-res:
            lowres_info.update(info)
            del self.images[name]
            info = lowres_info
        return info

    @contextmanager
    def _marked_sequence(self, **kwargs):
        """
        Can receive as named arguments any of the entries described in section 14.7.2 'Structure Hierarchy'
        of the PDF spec: iD, a, c, r, lang, e, actualText
        """
        mcid = self.struct_builder.next_mcid_for_page(self.page)
        struct_elem = self._add_marked_content(
            struct_type="/Figure", mcid=mcid, **kwargs
        )
        start_page = self.page
        self._out(f"/P <</MCID {mcid}>> BDC")
        yield struct_elem
        if self.page != start_page:
            raise FPDFException("A page jump occured inside a marked sequence")
        self._out("EMC")

    def _add_marked_content(self, **kwargs):
        """
        Can receive as named arguments any of the entries described in section 14.7.2 'Structure Hierarchy'
        of the PDF spec: iD, a, c, r, lang, e, actualText
        """
        struct_elem, spid = self.struct_builder.add_marked_content(
            page_number=self.page, **kwargs
        )
        self.pages[self.page].struct_parents = spid
        self._set_min_pdf_version("1.4")  # due to using /MarkInfo
        return struct_elem

    @check_page
    def ln(self, h=None):
        """
        Line Feed.
        The current abscissa goes back to the left margin and the ordinate increases by
        the amount passed as parameter.

        Args:
            h (float): The height of the break.
                By default, the value equals the height of the last printed cell.
        """
        self.x = self.l_margin
        self.y += self._lasth if h is None else h

    def get_x(self):
        """Returns the abscissa of the current position."""
        return self.x

    def set_x(self, x):
        """
        Defines the abscissa of the current position.
        If the value provided is negative, it is relative to the right of the page.

        Args:
            x (float): the new current abscissa
        """
        self.x = x if x >= 0 else self.w + x

    def get_y(self):
        """Returns the ordinate of the current position."""
        if self._in_unbreakable:
            raise FPDFException(
                "Using get_y() inside an unbreakable() code block is error-prone"
            )
        return self.y

    def set_y(self, y):
        """
        Moves the current abscissa back to the left margin and sets the ordinate.
        If the value provided is negative, it is relative to the bottom of the page.

        Args:
            y (float): the new current ordinate
        """
        self.x = self.l_margin
        self.y = y if y >= 0 else self.h + y

    def set_xy(self, x, y):
        """
        Defines the abscissa and ordinate of the current position.
        If the values provided are negative, they are relative respectively to the right and bottom of the page.

        Args:
            x (float): the new current abscissa
            y (float): the new current ordinate
        """
        self.set_y(y)
        self.set_x(x)

    def normalize_text(self, txt):
        """Check that text input is in the correct format/encoding"""
        # - for TTF unicode fonts: unicode object (utf8 encoding)
        # - for built-in fonts: string instances (encoding: latin-1, cp1252)
        if not self.is_ttf_font and self.core_fonts_encoding:
            try:
                return txt.encode(self.core_fonts_encoding).decode("latin-1")
            except UnicodeEncodeError as error:
                raise FPDFUnicodeEncodingException(
                    text_index=error.start,
                    character=txt[error.start],
                    font_name=self.font_family + self.font_style,
                ) from error
        return txt

    def sign_pkcs12(
        self,
        pkcs_filepath,
        password=None,
        hashalgo="sha256",
        contact_info=None,
        location=None,
        signing_time=None,
        reason=None,
        flags=(AnnotationFlag.PRINT, AnnotationFlag.LOCKED),
    ):
        """
        Args:
            pkcs_filepath (str): file path to a .pfx or .p12 PKCS12,
                in the binary format described by RFC 7292
            password (bytes-like): the password to use to decrypt the data.
                `None` if the PKCS12 is not encrypted.
            hashalgo (str): hashing algorithm used, passed to `hashlib.new`
            contact_info (str): optional information provided by the signer to enable
                a recipient to contact the signer to verify the signature
            location (str): optional CPU host name or physical location of the signing
            signing_time (datetime): optional time of signing
            reason (str): optional signing reason
            flags (Tuple[fpdf.enums.AnnotationFlag], Tuple[str]): optional list of flags defining annotation properties
        """
        if not signer:
            raise EnvironmentError(
                "endesive.signer not available - PDF cannot be signed - Try: pip install endesive"
            )
        with open(pkcs_filepath, "rb") as pkcs_file:
            key, cert, extra_certs = pkcs12.load_key_and_certificates(
                pkcs_file.read(), password
            )
        self.sign(
            key=key,
            cert=cert,
            extra_certs=extra_certs,
            hashalgo=hashalgo,
            contact_info=contact_info,
            location=location,
            signing_time=signing_time,
            reason=reason,
            flags=flags,
        )

    @check_page
    def sign(
        self,
        key,
        cert,
        extra_certs=(),
        hashalgo="sha256",
        contact_info=None,
        location=None,
        signing_time=None,
        reason=None,
        flags=(AnnotationFlag.PRINT, AnnotationFlag.LOCKED),
    ):
        """
        Args:
            key: certificate private key
            cert (cryptography.x509.Certificate): certificate
            extra_certs (list[cryptography.x509.Certificate]): list of additional PKCS12 certificates
            hashalgo (str): hashing algorithm used, passed to `hashlib.new`
            contact_info (str): optional information provided by the signer to enable
                a recipient to contact the signer to verify the signature
            location (str): optional CPU host name or physical location of the signing
            signing_time (datetime): optional time of signing
            reason (str): optional signing reason
            flags (Tuple[fpdf.enums.AnnotationFlag], Tuple[str]): optional list of flags defining annotation properties
        """
        if not signer:
            raise EnvironmentError(
                "endesive.signer not available - PDF cannot be signed - Try: pip install endesive"
            )
        if self._sign_key:
            raise FPDFException(".sign* methods should be called only once")

        self._sign_key = key
        self._sign_cert = cert
        self._sign_extra_certs = extra_certs
        self._sign_hashalgo = hashalgo
        self._sign_time = signing_time or self.creation_date

        annotation = PDFAnnotation(
            "Widget",
            field_type="Sig",
            x=0,
            y=0,
            width=0,
            height=0,
            flags=flags,
            title="signature",
            value=Signature(
                contact_info=contact_info,
                location=location,
                m=PDFDate(self._sign_time),
                reason=reason,
            ),
        )
        self.pages[self.page].annots.append(annotation)

    def _substitute_page_number(self):
        substituted = False
        # Replace number of pages in fonts using subsets (unicode)
        alias = self.str_alias_nb_pages.encode("utf-16-be")
        encoded_nb = str(self.pages_count).encode("utf-16-be")
        for page in self.pages.values():
            substituted |= alias in page.contents
            page.contents = page.contents.replace(alias, encoded_nb)
        # Now repeat for no pages in non-subset fonts
        alias = self.str_alias_nb_pages.encode("latin-1")
        encoded_nb = str(self.pages_count).encode("latin-1")
        for page in self.pages.values():
            substituted |= alias in page.contents
            page.contents = page.contents.replace(alias, encoded_nb)
        if substituted:
            LOGGER.debug(
                "Substitution of '%s' was performed in the document",
                self.str_alias_nb_pages,
            )

    def _insert_table_of_contents(self):
        # Doc has been closed but we want to write to self.pages[self.page] instead of self.buffer:
        tocp = self._toc_placeholder
        prev_page, prev_y = self.page, self.y
        self.page, self.y = tocp.start_page, tocp.y
        # Disabling footer & header, as they have already been called:
        self.footer = lambda *args, **kwargs: None
        self.header = lambda *args, **kwargs: None
        tocp.render_function(self, self._outline)
        expected_final_page = tocp.start_page + tocp.pages - 1
        if self.page != expected_final_page:
            too = "many" if self.page > expected_final_page else "few"
            error_msg = f"The rendering function passed to FPDF.insert_toc_placeholder triggered too {too} page breaks: "
            error_msg += f"ToC ended on page {self.page} while it was expected to span exactly {tocp.pages} pages"
            raise FPDFException(error_msg)
        self.page, self.y = prev_page, prev_y
        del self.footer
        del self.header

    def file_id(self):  # pylint: disable=no-self-use
        """
        This method can be overridden in inherited classes
        in order to define a custom file identifier.
        Its output must have the format "<hex_string1><hex_string2>".
        If this method returns a falsy value (None, empty string),
        no /ID will be inserted in the generated PDF document.
        """
        return -1

    def _default_file_id(self, buffer):
        # Quoting the PDF 1.7 spec, section 14.4 File Identifiers:
        # > The value of this entry shall be an array of two byte strings.
        # > The first byte string shall be a permanent identifier
        # > based on the contents of the file at the time it was originally created
        # > and shall not change when the file is incrementally updated.
        # > The second byte string shall be a changing identifier
        # > based on the file’s contents at the time it was last updated.
        # > When a file is first written, both identifiers shall be set to the same value.
        id_hash = hashlib.new("md5", usedforsecurity=False)  # nosec B324
        id_hash.update(buffer)
        if self.creation_date:
            id_hash.update(self.creation_date.strftime("%Y%m%d%H%M%S").encode("utf8"))
        hash_hex = id_hash.hexdigest().upper()
        return f"<{hash_hex}><{hash_hex}>"

    def _do_underline(self, x, y, w, current_font=None):
        "Draw an horizontal line starting from (x, y) with a length equal to 'w'"
        if current_font is None:
            current_font = self.current_font
        up = current_font.up
        ut = current_font.ut
        return (
            f"{x * self.k:.2f} "
            f"{(self.h - y + up / 1000 * self.font_size) * self.k:.2f} "
            f"{w * self.k:.2f} {-ut / 1000 * self.font_size_pt:.2f} re f"
        )

    def _out(self, s):
        if self.buffer:
            raise FPDFException(
                "Content cannot be added on a finalized document, after calling output()"
            )
        if not isinstance(s, bytes):
            if not isinstance(s, str):
                s = str(s)
            s = s.encode("latin1")
        if not self.page:
            raise FPDFException("No page open, you need to call add_page() first")
        self.pages[self.page].contents += s + b"\n"

    @check_page
    def interleaved2of5(self, txt, x, y, w=1, h=10):
        """Barcode I2of5 (numeric), adds a 0 if odd length"""
        narrow = w / 3
        wide = w

        # wide/narrow codes for the digits
        bar_char = {
            "0": "nnwwn",
            "1": "wnnnw",
            "2": "nwnnw",
            "3": "wwnnn",
            "4": "nnwnw",
            "5": "wnwnn",
            "6": "nwwnn",
            "7": "nnnww",
            "8": "wnnwn",
            "9": "nwnwn",
            "A": "nn",
            "Z": "wn",
        }
        # The caller should do this, or we can't rotate the thing.
        # self.set_fill_color(0)
        code = txt
        # add leading zero if code-length is odd
        if len(code) % 2 != 0:
            code = f"0{code}"

        # add start and stop codes
        code = f"AA{code.lower()}ZA"

        for i in range(0, len(code), 2):
            # choose next pair of digits
            char_bar = code[i]
            char_space = code[i + 1]
            # check whether it is a valid digit
            if char_bar not in bar_char:
                raise RuntimeError(f'Char "{char_bar}" invalid for I25:')
            if char_space not in bar_char:
                raise RuntimeError(f'Char "{char_space}" invalid for I25: ')

            # create a wide/narrow-seq (first digit=bars, second digit=spaces)
            seq = "".join(
                f"{cb}{cs}" for cb, cs in zip(bar_char[char_bar], bar_char[char_space])
            )

            for bar_index, char in enumerate(seq):
                # set line_width depending on value
                line_width = narrow if char == "n" else wide

                # draw every second value, the other is represented by space
                if bar_index % 2 == 0:
                    self.rect(x, y, line_width, h, "F")

                x += line_width

    @check_page
    def code39(self, txt, x, y, w=1.5, h=5):
        """Barcode 3of9"""
        dim = {"w": w, "n": w / 3}
        if not txt.startswith("*") or not txt.endswith("*"):
            warnings.warn(
                # pylint: disable=implicit-str-concat
                "Code 39 input must start and end with a '*' character to be valid."
                " This method does not insert it automatically."
            )
        chars = {
            "0": "nnnwwnwnn",
            "1": "wnnwnnnnw",
            "2": "nnwwnnnnw",
            "3": "wnwwnnnnn",
            "4": "nnnwwnnnw",
            "5": "wnnwwnnnn",
            "6": "nnwwwnnnn",
            "7": "nnnwnnwnw",
            "8": "wnnwnnwnn",
            "9": "nnwwnnwnn",
            "A": "wnnnnwnnw",
            "B": "nnwnnwnnw",
            "C": "wnwnnwnnn",
            "D": "nnnnwwnnw",
            "E": "wnnnwwnnn",
            "F": "nnwnwwnnn",
            "G": "nnnnnwwnw",
            "H": "wnnnnwwnn",
            "I": "nnwnnwwnn",
            "J": "nnnnwwwnn",
            "K": "wnnnnnnww",
            "L": "nnwnnnnww",
            "M": "wnwnnnnwn",
            "N": "nnnnwnnww",
            "O": "wnnnwnnwn",
            "P": "nnwnwnnwn",
            "Q": "nnnnnnwww",
            "R": "wnnnnnwwn",
            "S": "nnwnnnwwn",
            "T": "nnnnwnwwn",
            "U": "wwnnnnnnw",
            "V": "nwwnnnnnw",
            "W": "wwwnnnnnn",
            "X": "nwnnwnnnw",
            "Y": "wwnnwnnnn",
            "Z": "nwwnwnnnn",
            "-": "nwnnnnwnw",
            ".": "wwnnnnwnn",
            " ": "nwwnnnwnn",
            "*": "nwnnwnwnn",
            "$": "nwnwnwnnn",
            "/": "nwnwnnnwn",
            "+": "nwnnnwnwn",
            "%": "nnnwnwnwn",
        }
        # The caller should do this, or we can't rotate the thing.
        # self.set_fill_color(0)
        for c in txt.upper():
            if c not in chars:
                raise RuntimeError(f'Invalid char "{c}" for Code39')
            for i, d in enumerate(chars[c]):
                if i % 2 == 0:
                    self.rect(x, y, dim[d], h, "F")
                x += dim[d]
            x += dim["n"]

    @check_page
    @contextmanager
    def rect_clip(self, x, y, w, h):
        """
        Context manager that defines a rectangular crop zone,
        useful to render only part of an image.

        Args:
            x (float): abscissa of the clipping region top left corner
            y (float): ordinate of the clipping region top left corner
            w (float): width of the clipping region
            h (float): height of the clipping region
        """
        self._out(
            (
                f"q {x * self.k:.2f} {(self.h - y - h) * self.k:.2f} {w * self.k:.2f} "
                f"{h * self.k:.2f} re W n"
            )
        )
        yield
        self._out("Q")

    @check_page
    @contextmanager
    def elliptic_clip(self, x, y, w, h):
        """
        Context manager that defines an elliptic crop zone,
        useful to render only part of an image.

        Args:
            x (float): abscissa of the clipping region top left corner
            y (float): ordinate of the clipping region top left corner
            w (float): ellipse width
            h (float): ellipse height
        """
        self._out("q")
        self._draw_ellipse(x, y, w, h, "W n")
        yield
        self._out("Q")

    @check_page
    @contextmanager
    def round_clip(self, x, y, r):
        """
        Context manager that defines a circular crop zone,
        useful to render only part of an image.

        Args:
            x (float): abscissa of the clipping region top left corner
            y (float): ordinate of the clipping region top left corner
            r (float): radius of the clipping region
        """
        with self.elliptic_clip(x, y, r, r):
            yield

    @contextmanager
    def unbreakable(self):
        """
        Ensures that all rendering performed in this context appear on a single page
        by performing page break beforehand if need be.

        Notes
        -----

        Using this method means to duplicate the FPDF `bytearray` buffer:
        when generating large PDFs, doubling memory usage may be troublesome.
        """
        prev_page, prev_y = self.page, self.y
        recorder = FPDFRecorder(self, accept_page_break=False)
        recorder.page_break_triggered = False
        self._in_unbreakable = True
        LOGGER.debug("Starting unbreakable block")
        yield recorder
        y_scroll = recorder.y - prev_y + (recorder.page - prev_page) * self.eph
        if prev_y + y_scroll > self.page_break_trigger or recorder.page > prev_page:
            LOGGER.debug("Performing page jump due to unbreakable height")
            recorder.rewind()
            # pylint: disable=protected-access
            # Performing this call through .pdf so that it does not get recorded & replayed:
            recorder.pdf._perform_page_break()
            recorder.replay()
            recorder.page_break_triggered = True
        self._in_unbreakable = False
        LOGGER.debug("Ending unbreakable block")

    @contextmanager
    def offset_rendering(self):
        """
        All rendering performed in this context is made on a dummy FPDF object.
        This allows to test the results of some operations on the global layout
        before performing them "for real".
        """
        prev_page, prev_y = self.page, self.y
        recorder = FPDFRecorder(self, accept_page_break=False)
        recorder.page_break_triggered = False
        yield recorder
        y_scroll = recorder.y - prev_y + (recorder.page - prev_page) * self.eph
        if prev_y + y_scroll > self.page_break_trigger or recorder.page > prev_page:
            recorder.page_break_triggered = True
        recorder.rewind()

    @check_page
    def insert_toc_placeholder(self, render_toc_function, pages=1):
        """
        Configure Table Of Contents rendering at the end of the document generation,
        and reserve some vertical space right now in order to insert it.

        Args:
            render_toc_function (function): a function that will be invoked to render the ToC.
                This function will receive 2 parameters: `pdf`, an instance of FPDF, and `outline`,
                a list of `fpdf.outline.OutlineSection`.
            pages (int): the number of pages that the Table of Contents will span,
                including the current one that will. As many page breaks as the value of this argument
                will occur immediately after calling this method.
        """
        if not callable(render_toc_function):
            raise TypeError(
                f"The first argument must be a callable, got: {type(render_toc_function)}"
            )
        if self._toc_placeholder:
            raise FPDFException(
                "A placeholder for the table of contents has already been defined"
                f" on page {self._toc_placeholder.start_page}"
            )
        self._toc_placeholder = ToCPlaceholder(
            render_toc_function, self.page, self.y, pages
        )
        for _ in range(pages):
            self.add_page()

    def set_section_title_styles(
        self,
        level0,
        level1=None,
        level2=None,
        level3=None,
        level4=None,
        level5=None,
        level6=None,
    ):
        """
        Defines a style for section titles.
        After calling this method, calls to `FPDF.start_section` will render section names visually.

        Args:
            level0 (TitleStyle): style for the top level section titles
            level1 (TitleStyle): optional style for the level 1 section titles
            level2 (TitleStyle): optional style for the level 2 section titles
            level3 (TitleStyle): optional style for the level 3 section titles
            level4 (TitleStyle): optional style for the level 4 section titles
            level5 (TitleStyle): optional style for the level 5 section titles
            level6 (TitleStyle): optional style for the level 6 section titles
        """
        for level in (level0, level1, level2, level3, level4, level5, level6):
            if level and not isinstance(level, TitleStyle):
                raise TypeError(
                    f"Arguments must all be TitleStyle instances, got: {type(level)}"
                )
        self.section_title_styles = {
            0: level0,
            1: level1,
            2: level2,
            3: level3,
            4: level4,
            5: level5,
            6: level6,
        }

    @check_page
    def start_section(self, name, level=0, strict=True):
        """
        Start a section in the document outline.
        If section_title_styles have been configured,
        render the section name visually as a title.

        Args:
            name (str): section name
            level (int): section level in the document outline. 0 means top-level.
        """
        if level < 0:
            raise ValueError('"level" mut be equal or greater than zero')
        if strict and self._outline and level > self._outline[-1].level + 1:
            raise ValueError(
                f"Incoherent hierarchy: cannot start a level {level} section after a level {self._outline[-1].level} one"
            )
        dest = DestinationXYZ(self.page, top=self.h_pt - self.y * self.k)
        outline_struct_elem = None
        if self.section_title_styles:
            # We first check if adding this multi-cell will trigger a page break:
            with self.offset_rendering() as pdf:
                # pylint: disable=protected-access
                with pdf._use_title_style(pdf.section_title_styles[level]):
                    pdf.multi_cell(
                        w=pdf.epw,
                        h=pdf.font_size,
                        txt=name,
                        new_x=XPos.LMARGIN,
                        new_y=YPos.NEXT,
                    )
            if pdf.page_break_triggered:
                # If so, we trigger a page break manually beforehand:
                self.add_page()
            with self._marked_sequence(title=name) as struct_elem:
                outline_struct_elem = struct_elem
                with self._use_title_style(self.section_title_styles[level]):
                    self.multi_cell(
                        w=self.epw,
                        h=self.font_size,
                        txt=name,
                        new_x=XPos.LMARGIN,
                        new_y=YPos.NEXT,
                    )
        self._outline.append(
            OutlineSection(name, level, self.page, dest, outline_struct_elem)
        )

    @contextmanager
    def _use_title_style(self, title_style: TitleStyle):
        if title_style.t_margin:
            self.ln(title_style.t_margin)
        if title_style.l_margin:
            self.set_x(title_style.l_margin)
        with self.use_font_face(title_style):
            yield
        if title_style.b_margin:
            self.ln(title_style.b_margin)

    @contextmanager
    def use_font_face(self, font_face: FontFace):
        """
        Sets the provided `fpdf.fonts.FontFace` in a local context,
        then restore font settings back to they were initially.
        This method must be used as a context manager using `with`:

            with pdf.use_font_face(FontFace(emphasis="BOLD", color=255, size_pt=42)):
                put_some_text()
        """
        if not font_face:
            yield
            return
        prev_font = (self.font_family, self.font_style, self.font_size_pt)
        self.set_font(
            font_face.family or self.font_family,
            font_face.emphasis.style
            if font_face.emphasis is not None
            else self.font_style,
            font_face.size_pt or self.font_size_pt,
        )
        prev_text_color = self.text_color
        if font_face.color is not None and font_face.color != self.text_color:
            self.set_text_color(font_face.color)
        prev_fill_color = self.fill_color
        if font_face.fill_color is not None and font_face.fill_color != self.fill_color:
            self.set_fill_color(font_face.fill_color)
        yield
        if font_face.fill_color is not None and font_face.fill_color != prev_fill_color:
            self.set_fill_color(prev_fill_color)
        self.text_color = prev_text_color
        self.set_font(*prev_font)

    @check_page
    @contextmanager
    def table(self, *args, **kwargs):
        """
        Inserts a table, that can be built using the `fpdf.table.Table` object yield.
        Detailed usage documentation: https://pyfpdf.github.io/fpdf2/Tables.html

        Args:
            rows: optional. Sequence of rows (iterable) of str to initiate the table cells with text content
            align (str, fpdf.enums.Align): optional, default to CENTER. Sets the table horizontal position relative to the page,
                when it's not using the full page width
            borders_layout (str, fpdf.enums.TableBordersLayout): optional, default to ALL. Control what cell borders are drawn
            cell_fill_color (int, tuple, fpdf.drawing.DeviceGray, fpdf.drawing.DeviceRGB): optional.
                Defines the cells background color
            cell_fill_mode (str, fpdf.enums.TableCellFillMode): optional. Defines which cells are filled with color in the background
            col_widths (int, tuple): optional. Sets column width. Can be a single number or a sequence of numbers
            first_row_as_headings (bool): optional, default to True. If False, the first row of the table
                is not styled differently from the others
            gutter_height (float): optional vertical space between rows
            gutter_width (float): optional horizontal space between columns
            headings_style (fpdf.fonts.FontFace): optional, default to bold.
                Defines the visual style of the top headings row: size, color, emphasis...
            line_height (number): optional. Defines how much vertical space a line of text will occupy
            markdown (bool): optional, default to False. Enable markdown interpretation of cells textual content
            text_align (str, fpdf.enums.Align): optional, default to JUSTIFY. Control text alignment inside cells.
            width (number): optional. Sets the table width
            wrapmode (fpdf.enums.WrapMode): "WORD" for word based line wrapping (default),
                "CHAR" for character based line wrapping.
        """
        table = Table(self, *args, **kwargs)
        yield table
        table.render()

    def output(
        self, name="", dest="", linearize=False, output_producer_class=OutputProducer
    ):
        """
        Output PDF to some destination.
        The method first calls [close](close.md) if necessary to terminate the document.
        After calling this method, content cannot be added to the document anymore.

        By default the bytearray buffer is returned.
        If a `name` is given, the PDF is written to a new file.

        Args:
            name (str): optional File object or file path where to save the PDF under
            dest (str): [**DEPRECATED since 2.3.0**] unused, will be removed in a later version
            output_producer_class (class): use a custom class for PDF file generation
        """
        if dest:
            warnings.warn(
                '"dest" parameter is deprecated, unused and will soon be removed',
                DeprecationWarning,
                stacklevel=2,
            )
        # Finish document if necessary:
        if not self.buffer:
            if self.page == 0:
                self.add_page()
            # Generating final page footer:
            self.in_footer = True
            self.footer()
            self.in_footer = False
            # Generating .buffer based on .pages:
            if self._toc_placeholder:
                self._insert_table_of_contents()
            if self.str_alias_nb_pages:
                self._substitute_page_number()
            if linearize:
                output_producer_class = LinearizedOutputProducer
            output_producer = output_producer_class(self)
            self.buffer = output_producer.bufferize()
        if name:
            if isinstance(name, os.PathLike):
                name.write_bytes(self.buffer)
            elif isinstance(name, str):
                Path(name).write_bytes(self.buffer)
            else:
                name.write(self.buffer)
            return None
        return self.buffer


def _convert_to_drawing_color(r, g, b):
    if isinstance(r, (drawing.DeviceGray, drawing.DeviceRGB)):
        # Note: in this case, r is also a Sequence
        return r
    if isinstance(r, Sequence):
        r, g, b = r
    if (r, g, b) == (0, 0, 0) or g == -1:
        return drawing.DeviceGray(r / 255)
    return drawing.DeviceRGB(r / 255, g / 255, b / 255)


def _is_svg(bytes):
    return bytes.startswith(b"<?xml ") or bytes.startswith(b"<svg ")


# Pattern from sir Guido Von Rossum: https://stackoverflow.com/a/72911884/636849
# > a module can define a class with the desired functionality, and then at
# > the end, replace itself in sys.modules with an instance of that class
sys.modules[__name__].__class__ = WarnOnDeprecatedModuleAttributes


__pdoc__ = {"FPDF.add_highlight": False}  # Replaced by FPDF.highlight

__all__ = [
    "FPDF",
    "XPos",
    "YPos",
    "get_page_format",
    "ImageInfo",
    "TextMode",
    "TitleStyle",
    "PAGE_FORMATS",
]

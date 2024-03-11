from fpdf import FPDF, FPDFException, TextMode
from fpdf.line_break import Fragment, MultiLineBreak, CurrentLine, TextLine
from fpdf.enums import Align, CharVPos

import pytest


class FxFragment(Fragment):
    """Test fixture returning a predetermined width for each character.
    Argument "wdict" is a dict of "styles" of arbitrary names.
    The value of each style is a dict of characters and widths.
    """

    def __init__(self, wdict, *args, **kwargs):
        self.wdict = wdict
        super().__init__(*args, **kwargs)

    def get_character_width(self, character, print_sh=False, initial_cs=True):
        """Return the relevant width from "wdict"."""
        cw = self.wdict[self.font_style]
        return cw[character]


class FxFont:
    def __init__(self, cw):
        self.i = 1
        self.cw = cw

    def get_char_width(self, char):
        return self.cw[char] if char in self.cw else 2

    def get_text_width(self, text, *_):
        return (len(text), sum(self.get_char_width(c) for c in text))


def test_fragment_properties():
    """
    Make sure the accessor properties in Fragment() return the correct
    value as of the originating graphics state.
    """
    # pylint: disable=protected-access
    pdf = FPDF()
    font_family = "helvetica"
    font_style = "I"
    font_size = 22
    pdf.set_font(font_family, font_style, font_size)
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert frag.font == pdf.current_font, (
        f"frag.font ({frag.font['name']}/{frag.font['fontkey']})"
        f" != pdf.current_font ({pdf.current_font['name']}/{pdf.current_font['fontkey']})"
    )
    assert frag.is_ttf_font == pdf.is_ttf_font, (
        f"frag.is_ttf_font ({frag.is_ttf_font})"
        f" != pdf.unifontsubset ({pdf.is_ttf_font})"
    )
    assert frag.font_family == pdf.font_family, (
        f"frag.font_family ({frag.font_family})"
        f" != pdf.font_family ({pdf.font_family})"
    )
    assert (
        frag.font_style == pdf.font_style
    ), f"frag.font_style ({frag.font_style}) != pdf.font_style ({pdf.font_style})"
    assert (
        frag.font_size == pdf.font_size
    ), f"frag.font_size ({frag.font_size}) != pdf.font_size ({pdf.font_size})"
    assert (
        frag.underline == pdf.underline
    ), f"frag.underline ({frag.underline}) != pdf.underline ({pdf.underline})"
    pdf.set_font_size(44)
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert (
        frag.font_size == pdf.font_size
    ), f"frag.font_size ({frag.font_size}) != pdf.font_size ({pdf.font_size})"
    pdf.set_stretching(120)
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert frag.font_stretching == pdf.font_stretching, (
        f"frag.font_stretching ({frag.font_stretching})"
        f" != pdf.font_stretching ({pdf.font_stretching})"
    )
    pdf.set_char_spacing(4)
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert frag.char_spacing == pdf.char_spacing, (
        f"frag.char_spacing ({frag.char_spacing})"
        f" != pdf.char_spacing ({pdf.char_spacing})"
    )
    pdf.text_mode = TextMode.STROKE
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert (
        frag.text_mode == pdf.text_mode
    ), f"frag.text_mode ({frag.text_mode}) != pdf.text_mode ({pdf.text_mode})"
    pdf.underline = True
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert (
        frag.underline == pdf.underline
    ), f"frag.underline ({frag.underline}) != pdf.underline ({pdf.underline})"
    pdf.set_draw_color(0.1, 0.2, 0.3)
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert (
        frag.draw_color == pdf.draw_color
    ), f"frag.draw_color ({frag.draw_color}) != pdf.draw_color ({pdf.draw_color})"
    pdf.set_fill_color(0.3, 0.2, 0.1)
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert (
        frag.fill_color == pdf.fill_color
    ), f"frag.fill_color ({frag.fill_color}) != pdf.fill_color ({pdf.fill_color})"
    pdf.set_text_color(0.5)
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert (
        frag.text_color == pdf.text_color
    ), f"frag.text_color ({frag.text_color}) != pdf.text_color ({pdf.text_color})"
    pdf.set_line_width(0.5)
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert (
        frag.line_width == pdf.line_width
    ), f"frag.line_width ({frag.line_width}) != pdf.line_width ({pdf.line_width})"
    pdf.char_vpos = "SUP"
    frag = Fragment("example", pdf._get_current_graphics_state(), pdf.k)
    assert (
        frag.char_vpos == pdf.char_vpos
    ), f"frag.char_vpos ({frag.char_vpos}) != pdf.char_vpos ({pdf.char_vpos})"


def test_no_fragments():
    """
    There is no text provided to break into multiple lines
    expected behavior ->
        - call to `get_line_of_given_width` always returns None
    """
    char_width = 6
    test_width = char_width * 200
    multi_line_break = MultiLineBreak([], test_width, [0, 0])
    assert multi_line_break.get_line() is None
    multi_line_break = MultiLineBreak([], 100, [0, 0])
    assert multi_line_break.get_line() is None


_gs_normal = dict(
    font_style="normal",
    font_size_pt=12,
    font_family="helvetica",
    font_stretching=100,
    char_spacing=0,
    current_font={},
    char_vpos=CharVPos.LINE,
    text_shaping=None,
)
_gs_bold = dict(
    font_style="bold",
    font_size_pt=12,
    font_family="helvetica",
    font_stretching=100,
    char_spacing=0,
    current_font={},
    char_vpos=CharVPos.LINE,
    text_shaping=None,
)


def gs_with_font(graphics_state, cw):
    gs = graphics_state
    gs["current_font"] = FxFont(cw)
    return gs


def test_width_calculation():
    """
    Every character has different width
    """
    text = "abcd"
    char_width = 2
    alphabet = {
        "normal": {},
    }

    def _get_width(height):  # pylint: disable=unused-argument
        return max_width

    for i, char in enumerate(text):
        alphabet["normal"][char] = char_width + i
    alphabet["normal"][" "] = char_width
    gs = _gs_normal
    gs["current_font"] = FxFont(alphabet["normal"])
    fragments = [FxFragment(alphabet, text, gs, 1)]
    multi_line_break = MultiLineBreak(fragments, _get_width, [0, 0])

    # zero width returns empty line
    max_width = 0
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[],
        text_width=0,
        number_of_spaces=0,
        align=Align.L,
        height=0,
        max_width=max_width,
        trailing_nl=False,
    )
    assert res == exp

    # the first character has width of char_width.
    # request of 1 unit line raises an exception
    with pytest.raises(FPDFException):
        max_width = 1
        res = multi_line_break.get_line()

    # get other characters one by one
    for i, char in enumerate(text):
        max_width = char_width + i
        res = multi_line_break.get_line()
        exp = TextLine(
            fragments=[Fragment(char, _gs_normal, 1)],
            text_width=char_width + i,
            number_of_spaces=0,
            align=Align.L,
            height=12,
            max_width=max_width,
            trailing_nl=False,
        )
        assert res == exp

    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_single_space_in_fragment():
    """
    there is only one space character in the input text.
    expected behavior ->
        - first call to `get_line` contains space.
        - second call to `get_line` is None because there is no
            text left.
    """
    text = " "
    char_width = 6
    test_width = char_width * 10
    alphabet = {
        "normal": {},
    }
    gs = _gs_normal
    gs["current_font"] = FxFont(alphabet["normal"])
    fragments = [FxFragment(alphabet, text, gs, 1)]
    for char in text:
        alphabet["normal"][char] = char_width
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=fragments,
        text_width=char_width,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_single_soft_hyphen_in_fragment():
    """
    there is only one soft hyphen character in the input text.
    expected behavior ->
        - call to `get_line` always returns None, because soft
          hyphen doesn't break a word
    """
    alphabet = {
        "normal": {"\u002d": 500},
    }
    text = "\u00ad"
    char_width = 6
    test_width = char_width * 200
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(alphabet, text, gs_with_font(_gs_normal, alphabet["normal"]), 1)
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_single_hard_hyphen_in_fragment():
    """
    there is only one hard hyphen character in the input text.
    expected behavior ->
        - first call to `get_line` contains hard hyphen.
        - second call to `get_line` is None because there is no
    """
    alphabet = {
        "normal": {"\u002d": 500},
    }
    text = "\u002d"
    char_width = 6
    test_width = char_width * 4
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(alphabet, text, gs_with_font(_gs_normal, alphabet["normal"]), 1)
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=fragments,
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_real_hyphen_acts_differently_from_soft_hyphen():
    words = ["a", "b", "c", "d"]
    char_width = 6
    test_width = char_width * 4
    alphabet = {
        "normal": {"\u002d": char_width},
    }
    words_separated_by_soft_hyphen = "\u00ad".join(words)
    words_separated_by_hard_hyphen = "\u002d".join(words)
    for char in words_separated_by_soft_hyphen:
        alphabet["normal"][char] = char_width
    soft_hyphen_line_break = MultiLineBreak(
        [
            FxFragment(
                alphabet,
                words_separated_by_soft_hyphen,
                gs_with_font(_gs_normal, alphabet["normal"]),
                1,
            )
        ],
        test_width,
        [0, 0],
    )
    hard_hyphen_line_break = MultiLineBreak(
        [
            FxFragment(
                alphabet,
                words_separated_by_hard_hyphen,
                gs_with_font(_gs_normal, alphabet["normal"]),
                1,
            )
        ],
        test_width,
        [0, 0],
    )
    hh_res = soft_hyphen_line_break.get_line()
    sh_res = hard_hyphen_line_break.get_line()
    assert hh_res != sh_res
    hh_res = soft_hyphen_line_break.get_line()
    sh_res = hard_hyphen_line_break.get_line()
    assert hh_res != sh_res


def test_trailing_soft_hyphen():
    """
    fit one word and trailing soft-hyphen into the line with extremely large width.
    expected behavior ->
        - first call to `get_line` cointains the word.
          soft hyphen is not included in the line.
        - second call to `get_line` is None because there is no
            text left.
    """
    text = "hello\u00ad"
    char_width = 6
    test_width = char_width * 10
    test_width_B = char_width * 5
    alphabet = {
        "normal": {"\u002d": char_width},
    }
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(alphabet, text, gs_with_font(_gs_normal, alphabet["normal"]), 1)
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("hello", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=test_width_B,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_trailing_whitespace():
    """
    fit one word and trailing whitespace into the line with extremely large width.
    expected behavior ->
        - first call to `get_line` cointains the word and the space.
        - second call to `get_line` is None because there is no
            text left.
    """
    text = "hello "
    char_width = 6
    test_width = char_width * 10
    test_width_B = char_width * 6
    alphabet = {
        "normal": {},
    }
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(alphabet, text, gs_with_font(_gs_normal, alphabet["normal"]), 1)
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=fragments,
        text_width=test_width_B,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_two_words_one_line():
    """
    fit two words into the line with extremely large width.
    expected behavior ->
        - first call to `get_line` cointains all words.
        - second call to `get_line` is None because there is no
            text left.
    """
    text = "hello world"
    char_width = 6
    test_width = char_width * 200
    test_width_B = char_width * 11
    alphabet = {
        "normal": {},
    }
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(alphabet, text, gs_with_font(_gs_normal, alphabet["normal"]), 1)
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=fragments,
        text_width=test_width_B,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_two_words_one_line_justify():
    """
    fit two words into the line with extremely large width.
    expected behavior ->
        - first call to `get_line` cointains all words.
            this line is expected to be unjustified, because it is the last
            line.
        - second call to `get_line` is None because there is no
            text left.
    """
    text = "hello world"
    char_width = 6
    test_width = char_width * 200
    test_width_B = char_width * 11
    alphabet = {
        "normal": {},
    }
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(alphabet, text, gs_with_font(_gs_normal, alphabet["normal"]), 1)
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0], align=Align.J)
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=fragments,
        text_width=test_width_B,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_two_words_two_lines_break_by_space():
    """
    fit two words into the line that can fit only one word.
    expected behavior:
        - first call to `get_line` cointains the first word.
        - second call to `get_line` cointains the second word.
        - third call to `get_line` is None because there is no
            text left.
    """
    text = "hello world"
    char_width = 6
    test_width = char_width * 5
    alphabet = {
        "normal": {},
    }
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(alphabet, text, gs_with_font(_gs_normal, alphabet["normal"]), 1)
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("hello", _gs_normal, 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("world", _gs_normal, 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_two_words_two_lines_break_by_space_justify():
    """
    fit two words into the line that can fit only one word.
    expected behavior:
        - first call to `get_line` cointains the first word.
            Line is expected to be unjustified, because there are no spaces in
            the line.
        - second call to `get_line` cointains the second word.
            Line is expected to be unjustified, because it is the last line.
        - third call to `get_line` is None because there is no
            text left.
    """
    text = "hello world"
    char_width = 6
    test_width = char_width * 5
    alphabet = {
        "normal": {},
    }
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [FxFragment(alphabet, text, _gs_normal, 1)]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])

    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("hello", _gs_normal, 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("world", _gs_normal, 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_four_words_two_lines_break_by_space():
    """
    fit two words into the line that can fit only one word.
    expected behavior:
        - first call to `get_line` cointains the first two words.
        - second call to `get_line` cointains the second two words.
        - third call to `get_line` is None because there is no
            text left.
    """
    first_line_text = "hello world"
    second_line_text = "hello world"
    char_width = 6
    test_width_A = char_width * 12
    test_width_AA = char_width * 11
    text = " ".join([first_line_text, second_line_text])
    alphabet = {
        "normal": {},
    }
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [FxFragment(alphabet, text, _gs_normal, 1)]
    multi_line_break = MultiLineBreak(fragments, test_width_A, [0, 0])
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment(first_line_text, _gs_normal, 1)],
        text_width=test_width_AA,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width_A,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment(second_line_text, _gs_normal, 1)],
        text_width=test_width_AA,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width_A,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_four_words_two_lines_break_by_space_justify():
    """
    fit two words into the line that can fit only one word.
    expected behavior:
        - first call to `get_line` cointains the first two words.
            Line is expected to be justified.
        - second call to `get_line` cointains the second two words.
            Line is expected to be unjustified, because it is the last line.
        - third call to `get_line` is None because there is no
            text left.
    """
    first_line_text = "hello world"
    second_line_text = "hello world"
    char_width = 6
    test_width_A = char_width * 12
    test_width_AA = char_width * 11
    text = " ".join((first_line_text, second_line_text))
    alphabet = {
        "normal": {},
    }
    for char in text:
        alphabet["normal"][char] = char_width
    fragments = [FxFragment(alphabet, text, _gs_normal, 1)]
    multi_line_break = MultiLineBreak(fragments, test_width_A, [0, 0], align=Align.J)
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment(first_line_text, _gs_normal, 1)],
        text_width=test_width_AA,
        number_of_spaces=1,
        align=Align.J,
        height=12,
        max_width=test_width_A,
        trailing_nl=False,
    )
    print(res)
    print(exp)
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment(second_line_text, _gs_normal, 1)],
        text_width=test_width_AA,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width_A,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_break_fragment_into_two_lines():
    """
    There are multiple fragments with different styles.
    This test breaks one fragment between two lines.
    """
    char_width = 6
    charB_width = 12
    test_width_A = char_width * 10
    test_width_B = char_width * 16
    test_width_BB = char_width * 15
    alphabet = {
        "normal": {},
        "bold": {},
    }
    first_line_text = "one "
    second_line_text = "two three"
    third_line_text = " four"
    text = "".join((first_line_text, second_line_text, third_line_text))
    for char in text:
        alphabet["normal"][char] = char_width
        alphabet["bold"][char] = charB_width

    fragments = [
        FxFragment(
            alphabet, first_line_text, gs_with_font(_gs_normal, alphabet["normal"]), 1
        ),
        FxFragment(
            alphabet, second_line_text, gs_with_font(_gs_bold, alphabet["bold"]), 1
        ),
        FxFragment(
            alphabet, third_line_text, gs_with_font(_gs_normal, alphabet["normal"]), 1
        ),
    ]

    def _get_width(height):  # pylint: disable=unused-argument
        return max_width

    multi_line_break = MultiLineBreak(fragments, _get_width, [0, 0])
    max_width = test_width_A
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment(first_line_text, _gs_normal, 1),
            Fragment("two", _gs_bold, 1),
        ],
        text_width=test_width_A,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width_A,
        trailing_nl=False,
    )
    assert res == exp
    max_width = test_width_B
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("three", _gs_bold, 1),
            Fragment(third_line_text, _gs_normal, 1),
        ],
        text_width=test_width_BB,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width_B,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_break_fragment_into_two_lines_justify():
    """
    There are multiple fragments with different styles.
    This test breaks one fragment between two lines.
    """
    char_width = 6
    charB_width = 12
    test_width_A = char_width * 10
    test_width_B = char_width * 16
    test_width_BB = char_width * 15
    alphabet = {
        "normal": {},
        "bold": {},
    }
    first_line_text = "one "
    second_line_text = "two three"
    third_line_text = " four"
    text = "".join((first_line_text, second_line_text, third_line_text))
    for char in text:
        alphabet["normal"][char] = char_width
        alphabet["bold"][char] = charB_width

    fragments = [
        FxFragment(
            alphabet, first_line_text, gs_with_font(_gs_normal, alphabet["normal"]), 1
        ),
        FxFragment(
            alphabet, second_line_text, gs_with_font(_gs_bold, alphabet["bold"]), 1
        ),
        FxFragment(
            alphabet, third_line_text, gs_with_font(_gs_normal, alphabet["normal"]), 1
        ),
    ]

    def _get_width(height):  # pylint: disable=unused-argument
        return max_width

    multi_line_break = MultiLineBreak(fragments, _get_width, [0, 0], align=Align.J)
    max_width = test_width_A
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment(first_line_text, _gs_normal, 1),
            Fragment("two", _gs_bold, 1),
        ],
        text_width=test_width_A,
        number_of_spaces=1,
        align=Align.J,
        height=12,
        max_width=test_width_A,
        trailing_nl=False,
    )
    assert res == exp
    max_width = test_width_B
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("three", _gs_bold, 1),
            Fragment(third_line_text, _gs_normal, 1),
        ],
        text_width=test_width_BB,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width_B,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_soft_hyphen_break():
    """
    all characters are separated by soft-hyphen
    expected behavior - there is a hard hyphen at the end of every line,
    except of the last one
    """
    char_width = 6
    test_width = char_width * 5
    test_width_A = char_width * 4.4
    test_width_AA = char_width * 4
    test_width_B = char_width * 2
    alphabet = {"normal": {"\u002d": char_width}}
    long_string = "\u00ad".join("abcdefghijklmnop")
    for char in long_string:
        alphabet["normal"][char] = char_width

    fragments = [
        FxFragment(
            alphabet, long_string, gs_with_font(_gs_normal, alphabet["normal"]), 1
        )
    ]

    def _get_width(height):  # pylint: disable=unused-argument
        return max_width

    multi_line_break = MultiLineBreak(fragments, _get_width, [0, 0])
    max_width = test_width
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("abcd\u002d", gs_with_font(_gs_normal, alphabet["normal"]), 1)
        ],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    print(res)
    print(exp)
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("efgh\u002d", gs_with_font(_gs_normal, alphabet["normal"]), 1)
        ],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    max_width = test_width_A
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("ijk\u002d", gs_with_font(_gs_normal, alphabet["normal"]), 1)
        ],
        text_width=test_width_AA,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width_A,
        trailing_nl=False,
    )
    assert res == exp
    max_width = test_width_B
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("l\u002d", gs_with_font(_gs_normal, alphabet["normal"]), 1)
        ],
        text_width=test_width_B,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width_B,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("m\u002d", gs_with_font(_gs_normal, alphabet["normal"]), 1)
        ],
        text_width=test_width_B,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width_B,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("n\u002d", gs_with_font(_gs_normal, alphabet["normal"]), 1)
        ],
        text_width=test_width_B,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width_B,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("op", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=test_width_B,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width_B,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_soft_hyphen_break_justify():
    """
    all characters are separated by soft-hyphen
    expected behavior - there is a hard hyphen at the end of every line,
    except of the last one
    """
    char_width = 6
    test_width = char_width * 6
    last_width = char_width * 5
    alphabet = {"normal": {"\u002d": char_width}}
    words = ["ab cd", "ef gh", "kl mn"]
    long_string = "\u00ad".join(words)
    for char in long_string:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(
            alphabet, long_string, gs_with_font(_gs_normal, alphabet["normal"]), 1
        )
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0], align=Align.J)
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("ab cd\u002d", gs_with_font(_gs_normal, alphabet["normal"]), 1)
        ],
        text_width=test_width,
        number_of_spaces=1,
        align=Align.J,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[
            Fragment("ef gh\u002d", gs_with_font(_gs_normal, alphabet["normal"]), 1)
        ],
        text_width=test_width,
        number_of_spaces=1,
        align=Align.J,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("kl mn", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=last_width,
        number_of_spaces=1,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_explicit_break():
    """
    There is an explicit break character after every character
    Expected behavior:
        `get_line` returns single character on every call
    """
    char_width = 6
    test_width = char_width * 5
    alphabet = {
        "normal": {},
    }
    long_string = "\n".join("abcd")
    for char in long_string:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(
            alphabet, long_string, gs_with_font(_gs_normal, alphabet["normal"]), 1
        )
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("a", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=True,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("b", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=True,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("c", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=True,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("d", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_explicit_break_justify():
    """
    There is an explicit break character after every character
    Expected behavior:
        `get_line` returns single character on every call,
        returned lines are expected to be unjustified
    """
    char_width = 6
    test_width = char_width * 5
    alphabet = {
        "normal": {},
    }
    long_string = "\n".join("abcd")
    for char in long_string:
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(
            alphabet, long_string, gs_with_font(_gs_normal, alphabet["normal"]), 1
        )
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0], align=Align.J)
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("a", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=True,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("b", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=True,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("c", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=True,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("d", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_single_word_doesnt_fit_into_width():
    """
    There is a single word that doesn't fit into requested line
    Expected behavior:
        `get_line` as much characters as can fit into user
        provided width.
    """
    alphabet = {
        "normal": {},
    }
    long_string = "abcdefghijklmnop"
    char_width = 6
    test_width = char_width * 5
    for char in long_string:
        # glyph space units
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(
            alphabet, long_string, gs_with_font(_gs_normal, alphabet["normal"]), 1
        )
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0])
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("abcde", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    print(res)
    print(exp)
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("fghij", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("klmno", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("p", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    assert res == exp
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_single_word_doesnt_fit_into_width_justify():
    """
    There is a single word that doesn't fit into requested line
    Expected behavior:
        `get_line` as much characters as can fit into user
        provided width. returned lines are expected to be unjustified
    """
    char_width = 6
    test_width = char_width * 5
    alphabet = {
        "normal": {},
    }
    long_string = "abcdefghijklmnop"
    for char in long_string:
        # glyph space units
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(
            alphabet, long_string, gs_with_font(_gs_normal, alphabet["normal"]), 1
        )
    ]
    multi_line_break = MultiLineBreak(fragments, test_width, [0, 0], align=Align.J)
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("abcde", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("fghij", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("klmno", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=test_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=[Fragment("p", gs_with_font(_gs_normal, alphabet["normal"]), 1)],
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,
        height=12,
        max_width=test_width,
        trailing_nl=False,
    )
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_last_line_no_justify():
    """
    Make sure that the last line is not justified.
    """
    alphabet = {
        "normal": {},
    }
    long_string = "a"
    char_width = 6
    for char in long_string:
        # glyph space units
        alphabet["normal"][char] = char_width
    fragments = [
        FxFragment(
            alphabet, long_string, gs_with_font(_gs_normal, alphabet["normal"]), 1
        )
    ]

    def _get_width(height):  # pylint: disable=unused-argument
        return max_width

    multi_line_break = MultiLineBreak(fragments, _get_width, [0, 0], align=Align.J)
    max_width = char_width * 5
    res = multi_line_break.get_line()
    exp = TextLine(
        fragments=fragments,
        text_width=char_width,
        number_of_spaces=0,
        align=Align.L,  # !
        height=12,
        max_width=max_width,
        trailing_nl=False,
    )
    assert res == exp
    max_width = char_width
    res = multi_line_break.get_line()
    exp = None
    assert res == exp


def test_trim_trailing_spaces():
    "Check special cases in CurrentLine method."
    # pylint: disable=protected-access,assignment-from-none
    pdf = FPDF()
    pdf.set_font("helvetica")
    cl = CurrentLine(pdf.w)
    # Result: None - if cl.fragments is empty to begin with.
    res = cl.trim_trailing_spaces()
    assert res is None
    # Result: None - if cl.fragments is empty after trimming trailing spaces.
    frag = Fragment(" ", pdf._get_current_graphics_state(), pdf.k)
    cl.fragments = [frag]
    res = cl.trim_trailing_spaces()
    assert res is None


def test_line_break_no_initial_newline():  # issue-847
    text = "X" * 50
    alphabet = {"normal": {}}
    alphabet["normal"]["X"] = 4.7
    fragments = [FxFragment(alphabet, text, _gs_normal, 1)]
    multi_line_break = MultiLineBreak(fragments, 188, [0, 0])
    text_line = multi_line_break.get_line()
    assert text_line.fragments

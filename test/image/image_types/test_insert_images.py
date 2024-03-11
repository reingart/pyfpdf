import io
import logging
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import pytest

import fpdf
from fpdf.image_parsing import transcode_monochrome
from test.conftest import assert_pdf_equal

HERE = Path(__file__).resolve().parent


def test_insert_jpg(tmp_path):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    pdf.image(HERE / "insert_images_insert_jpg.jpg", x=15, y=15, h=140)
    assert_pdf_equal(pdf, HERE / "image_types_insert_jpg.pdf", tmp_path)


@pytest.mark.skipif(
    sys.platform in ("cygwin", "win32"),
    reason="Required system libraries to generate JPEG2000 images are a PITA to install under Windows",
)
def test_insert_jpg_jpxdecode(tmp_path):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.set_image_filter("JPXDecode")
    pdf.add_page()
    pdf.image(HERE / "insert_images_insert_jpg.jpg", x=15, y=15, h=140)
    assert_pdf_equal(pdf, HERE / "image_types_insert_jpg_jpxdecode.pdf", tmp_path)


def test_insert_jpg_flatedecode(tmp_path):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.set_image_filter("FlateDecode")
    pdf.add_page()
    pdf.image(HERE / "insert_images_insert_jpg.jpg", x=15, y=15, h=140)
    if sys.platform in ("cygwin", "win32"):
        # Pillow uses libjpeg-turbo on Windows and libjpeg elsewhere,
        # leading to a slightly different image being parsed and included in the PDF:
        assert_pdf_equal(
            pdf, HERE / "image_types_insert_jpg_flatedecode_windows.pdf", tmp_path
        )
    else:
        assert_pdf_equal(pdf, HERE / "image_types_insert_jpg_flatedecode.pdf", tmp_path)


def test_insert_jpg_cmyk(tmp_path):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    pdf.image(HERE / "insert_images_insert_jpg_cmyk.jpg", x=15, y=15)
    assert_pdf_equal(pdf, HERE / "images_types_insert_jpg_cmyk.pdf", tmp_path)


def test_insert_png(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.image(HERE / "insert_images_insert_png.png", x=15, y=15, h=140)
    assert_pdf_equal(pdf, HERE / "image_types_insert_png.pdf", tmp_path)


def test_insert_png_monochromatic(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.image(HERE / "../png_test_suite/basi0g01.png", x=15, y=15, h=140)
    assert_pdf_equal(pdf, HERE / "image_types_insert_png_monochromatic.pdf", tmp_path)


def test_transcode_monochrome_and_libtiff_support_custom_tags():
    # Fails under WSL on my computer (Lucas), with this error:
    #   AttributeError: module 'PIL._imaging' has no attribute 'libtiff_support_custom_tags'
    # (as a consequence, the test above & everal others also fail, because PDFs don't match)
    # cf. https://github.com/python-pillow/Pillow/issues/7019
    with Image.open("test/image/png_test_suite/basi0g01.png") as img:
        transcode_monochrome(img)


def test_insert_png_alpha(tmp_path):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    pdf.set_font("Helvetica", size=30)
    pdf.cell(w=pdf.epw, h=30, text="BEHIND")
    pdf.image(
        HERE / "../png_images/ba2b2b6e72ca0e4683bb640e2d5572f8.png", x=25, y=0, h=40
    )
    assert_pdf_equal(pdf, HERE / "image_types_insert_png_alpha.pdf", tmp_path)


def test_insert_png_disallow_transparency(tmp_path):
    pdf = fpdf.FPDF()
    pdf.allow_images_transparency = False
    pdf.add_page()
    pdf.set_font("Helvetica", size=30)
    pdf.cell(w=pdf.epw, h=30, text="BEHIND")
    pdf.image(
        HERE / "../png_images/ba2b2b6e72ca0e4683bb640e2d5572f8.png", x=25, y=0, h=40
    )
    assert_pdf_equal(
        pdf, HERE / "image_types_insert_png_disallow_transparency.pdf", tmp_path
    )


def test_insert_png_alpha_dctdecode(tmp_path):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.set_image_filter("DCTDecode")
    pdf.add_page()
    pdf.image(
        HERE / "../png_images/ba2b2b6e72ca0e4683bb640e2d5572f8.png", x=15, y=15, h=140
    )
    if sys.platform in ("cygwin", "win32"):
        # Pillow uses libjpeg-turbo on Windows and libjpeg elsewhere,
        # leading to a slightly different image being parsed and included in the PDF:
        assert_pdf_equal(
            pdf, HERE / "image_types_insert_png_alpha_dctdecode_windows.pdf", tmp_path
        )
    else:
        assert_pdf_equal(
            pdf, HERE / "image_types_insert_png_alpha_dctdecode.pdf", tmp_path
        )


def test_insert_bmp(tmp_path):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    pdf.image(HERE / "circle.bmp", x=15, y=15, h=140)
    assert_pdf_equal(pdf, HERE / "image_types_insert_bmp.pdf", tmp_path)


def test_insert_jpg_icc(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page(format=(448, 498))
    pdf.set_margin(0)
    pdf.image(HERE / "insert_images_insert_jpg_icc.jpg", x=0, y=0, h=498)
    # we add the same image a second time to make sure the ICC profile is only included
    # only once in that case
    pdf.add_page(format=(448, 498))
    pdf.image(HERE / "insert_images_insert_jpg_icc.jpg", x=0, y=0, h=498)
    # we add another image with the same ICC profile to make sure it's also included
    # only once in that case
    pdf.add_page(format=(314, 500))
    pdf.image(HERE / "insert_images_insert_jpg_icc_2.jpg", x=0, y=0, h=500)
    assert_pdf_equal(pdf, HERE / "image_types_insert_jpg_icc.pdf", tmp_path)


def test_insert_jpg_invalid_icc(caplog, tmp_path):
    with caplog.at_level(logging.INFO):
        pdf = fpdf.FPDF()
        pdf.add_page(format=(448, 498))
        pdf.set_margin(0)
        pdf.image(HERE / "insert_images_insert_jpg_icc_invalid.jpg", x=0, y=0, h=498)
    assert "Invalid ICC Profile in file" in caplog.text
    assert_pdf_equal(pdf, HERE / "image_types_insert_jpg_icc_invalid.pdf", tmp_path)


def test_insert_gif(tmp_path):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    pdf.image(HERE / "circle.gif", x=15, y=15)
    assert_pdf_equal(pdf, HERE / "image_types_insert_gif.pdf", tmp_path)


def test_insert_g4_tiff(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.image(HERE / "test.tiff", x=15, y=15)
    assert_pdf_equal(pdf, HERE / "image_types_insert_tiff.pdf", tmp_path)


def test_insert_tiff_cmyk(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.image(HERE / "insert_images_insert_tiff_cmyk.tiff", x=15, y=15)
    assert_pdf_equal(pdf, HERE / "image_types_insert_tiff_cmyk.pdf", tmp_path)


def test_insert_pillow(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page()
    img = Image.open(HERE / "insert_images_insert_png.png")
    pdf.image(img, x=15, y=15, h=140)
    assert_pdf_equal(pdf, HERE / "image_types_insert_png.pdf", tmp_path)


def test_insert_pillow_issue_139(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page()
    font = ImageFont.truetype(f"{HERE}/../../fonts/DejaVuSans.ttf", 40)
    for y in range(5):
        for x in range(4):
            img = Image.new(mode="RGB", size=(100, 100), color=(60, 255, 10))
            ImageDraw.Draw(img).text((20, 20), f"{y}{x}", fill="black", font=font)
            pdf.image(img, x=x * 50 + 5, y=y * 50 + 5, w=45)
    assert_pdf_equal(pdf, HERE / "insert_pillow_issue_139.pdf", tmp_path)


def test_insert_bytesio(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page()
    img = Image.open(HERE / "insert_images_insert_png.png")
    img_bytes = io.BytesIO()
    img.save(img_bytes, "PNG")
    pdf.image(img_bytes, x=15, y=15, h=140)
    assert_pdf_equal(pdf, HERE / "image_types_insert_png.pdf", tmp_path)
    assert not img_bytes.closed  # cf. issue #881


def test_insert_bytes(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page()
    img = Image.open(HERE / "insert_images_insert_png.png")
    img_bytes = io.BytesIO()
    img.save(img_bytes, "PNG")
    pdf.image(img_bytes.getvalue(), x=15, y=15, h=140)
    assert_pdf_equal(pdf, HERE / "image_types_insert_png.pdf", tmp_path)

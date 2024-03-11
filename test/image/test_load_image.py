import binascii
from glob import glob
from pathlib import Path

import pytest

import fpdf

from test.conftest import assert_pdf_equal, ensure_rss_memory_below, time_execution


HERE = Path(__file__).resolve().parent


def test_load_text_file():
    file = HERE / "__init__.py"
    contents = '"""This package contains image tests"""\n'
    bc = contents.encode()

    resource = fpdf.image_parsing.load_image(str(file)).getvalue()
    # loaded a text file in binary mode, may contain DOS style line endings.
    resource = resource.replace(b"\r\n", b"\n")
    assert bytes(resource) == bc


def test_load_base64_data(tmp_path):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.image(
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQBAMAAADt3eJSAAAAMFBMVEU0OkArMjhobHEoPUPFEBIuO0L+AAC2FBZ2JyuNICOfGx7xAwT"
        "jCAlCNTvVDA1aLzQ3COjMAAAAVUlEQVQI12NgwAaCDSA0888GCItjn0szWGBJTVoGSCjWs8TleQCQYV95evdxkFT8Kpe0PLDi5WfKd4LUsN5zS1sKFolt8bwAZrCa"
        "GqNYJAgFDEpQAAAzmxafI4vZWwAAAABJRU5ErkJggg=="
    )
    assert_pdf_equal(pdf, HERE / "load_base64_data.pdf", tmp_path)


def test_load_invalid_base64_data():
    pdf = fpdf.FPDF()
    pdf.add_page()
    with pytest.raises(binascii.Error):
        pdf.image("data:image/png;base64,GARBAGE")


# ensure memory usage does not get too high - this value depends on Python version:
@ensure_rss_memory_below(mib=6)
def test_share_images_cache(tmp_path):
    image_cache = None

    def build_pdf_with_big_images():
        nonlocal image_cache
        pdf = fpdf.FPDF()
        if image_cache is None:
            image_cache = pdf.image_cache
        else:
            pdf.image_cache = image_cache
        pdf.add_page()
        for img_path in glob(f"{HERE}/png_images/*.png"):
            pdf.image(img_path, h=pdf.eph)
        with (tmp_path / "out.pdf").open("wb") as pdf_file:
            pdf.output(pdf_file)
        # Reset the "usages" count:
        image_cache.reset_usages()

    with time_execution() as duration:
        build_pdf_with_big_images()
    first_time_duration = duration.seconds

    with time_execution() as duration:
        build_pdf_with_big_images()
    assert duration.seconds < first_time_duration / 2

import logging
from pathlib import Path

import fpdf
from test.conftest import assert_pdf_equal, ensure_rss_memory_below


HERE = Path(__file__).resolve().parent
IMAGE_PATH = HERE / "png_images/6c853ed9dacd5716bc54eb59cec30889.png"
MAX_MEMORY_MB = 12  # memory usage depends on Python version


@ensure_rss_memory_below(MAX_MEMORY_MB)
def test_oversized_images_warn(caplog):
    pdf = fpdf.FPDF()
    pdf.oversized_images = "WARN"
    pdf.add_page()
    pdf.image(IMAGE_PATH, w=50)
    assert "OVERSIZED" in caplog.text


@ensure_rss_memory_below(MAX_MEMORY_MB)
def test_oversized_images_downscale_simple(caplog, tmp_path):
    caplog.set_level(logging.DEBUG)
    pdf = fpdf.FPDF()
    pdf.oversized_images = "DOWNSCALE"
    pdf.add_page()
    pdf.image(IMAGE_PATH, w=50)
    assert "OVERSIZED: Generated new low-res image" in caplog.text
    assert len(pdf.image_cache.images) == 2, pdf.image_cache.images.keys()
    in_use_img_names = _in_use_img_names(pdf)
    assert len(in_use_img_names) == 1, pdf.image_cache.images.keys()
    assert_pdf_equal(pdf, HERE / "oversized_images_downscale_simple.pdf", tmp_path)


@ensure_rss_memory_below(MAX_MEMORY_MB)
def test_oversized_images_downscale_twice(tmp_path):
    pdf = fpdf.FPDF()
    pdf.oversized_images = "DOWNSCALE"
    pdf.add_page()
    pdf.image(IMAGE_PATH, w=50)
    pdf.image(IMAGE_PATH, w=50)
    assert len(pdf.image_cache.images) == 2, pdf.image_cache.images.keys()
    in_use_img_names = _in_use_img_names(pdf)
    assert len(in_use_img_names) == 1, pdf.image_cache.images.keys()
    assert_pdf_equal(pdf, HERE / "oversized_images_downscale_twice.pdf", tmp_path)


@ensure_rss_memory_below(MAX_MEMORY_MB)
def test_oversized_images_downscaled_and_highres():
    pdf = fpdf.FPDF()
    pdf.oversized_images = "DOWNSCALE"
    pdf.add_page()
    pdf.image(IMAGE_PATH, w=50)
    pdf.image(IMAGE_PATH, w=pdf.epw)
    assert len(pdf.image_cache.images) == 1, pdf.image_cache.images.keys()
    # Not calling assert_pdf_equal to avoid storing a large binary (1.4M) in this git repo


@ensure_rss_memory_below(MAX_MEMORY_MB)
def test_oversized_images_highres_and_downscaled():
    pdf = fpdf.FPDF()
    pdf.oversized_images = "DOWNSCALE"
    pdf.add_page()
    pdf.image(IMAGE_PATH, w=pdf.epw)
    pdf.image(IMAGE_PATH, w=50)
    assert len(pdf.image_cache.images) == 1, pdf.image_cache.images.keys()
    # Not calling assert_pdf_equal to avoid storing a large binary (1.4M) in this git repo


@ensure_rss_memory_below(MAX_MEMORY_MB)
def test_oversized_images_downscale_biggest_1st(tmp_path):
    pdf = fpdf.FPDF()
    pdf.oversized_images = "DOWNSCALE"
    pdf.add_page()
    pdf.image(IMAGE_PATH, w=50)
    pdf.image(IMAGE_PATH, w=30)
    assert len(pdf.image_cache.images) == 2, pdf.image_cache.images.keys()
    in_use_img_names = _in_use_img_names(pdf)
    assert len(in_use_img_names) == 1, pdf.image_cache.images.keys()
    assert_pdf_equal(pdf, HERE / "oversized_images_downscale_biggest_1st.pdf", tmp_path)


@ensure_rss_memory_below(MAX_MEMORY_MB)
def test_oversized_images_downscale_biggest_2nd(caplog, tmp_path):
    caplog.set_level(logging.DEBUG)
    pdf = fpdf.FPDF()
    pdf.oversized_images = "DOWNSCALE"
    pdf.add_page()
    pdf.image(IMAGE_PATH, w=30)
    pdf.image(IMAGE_PATH, w=50)
    assert "OVERSIZED: Updated low-res image" in caplog.text
    assert len(pdf.image_cache.images) == 2, pdf.image_cache.images.keys()
    in_use_img_names = _in_use_img_names(pdf)
    assert len(in_use_img_names) == 1, pdf.image_cache.images.keys()
    assert_pdf_equal(pdf, HERE / "oversized_images_downscale_biggest_2nd.pdf", tmp_path)


def _in_use_img_names(pdf):
    return [name for name, img in pdf.image_cache.images.items() if img["usages"]]

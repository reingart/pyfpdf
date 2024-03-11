from pathlib import Path

from fpdf import FPDF
from test.conftest import assert_pdf_equal

HERE = Path(__file__).resolve().parent


def test_set_no_margin(tmp_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margin(0)
    pdf.image(HERE / "../image/image_types/insert_images_insert_png.png", w=pdf.epw)
    assert_pdf_equal(pdf, HERE / "set_no_margin.pdf", tmp_path)

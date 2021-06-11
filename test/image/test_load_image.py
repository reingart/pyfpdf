from io import BytesIO
from pathlib import Path

import fpdf


HERE = Path(__file__).resolve().parent


def test_recognize_bytesIO():
    s = BytesIO()
    a = fpdf.image_parsing.load_image(s)
    assert a == s


def test_load_text_file():
    file = HERE / "__init__.py"
    contents = '"""This package contains image tests"""\n'
    bc = contents.encode()

    resource = fpdf.image_parsing.load_image(str(file)).getvalue()
    assert bytes(resource) == bc

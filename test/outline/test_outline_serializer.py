from fpdf.outline import OutlineSection, build_outline_objs
from fpdf.syntax import DestinationXYZ, PDFString


def _serialize_outline(sections, first_object_id=1):
    n = first_object_id
    outline_objs = list(build_outline_objs(sections))
    for obj in outline_objs:
        obj.id = n
        if n > first_object_id:
            obj.dest.page_ref = f"{2 * obj.dest.page_number + 1} 0 R"
        n += 1
    output = "\n".join(obj.serialize() for obj in outline_objs)
    return output


def test_serialize_outline():
    sections = (
        OutlineSection(
            "Title 1", level=0, page_number=1, dest=DestinationXYZ(page=1, top=0)
        ),
        OutlineSection(
            "Subtitle 1.1", level=1, page_number=1, dest=DestinationXYZ(page=2, top=0)
        ),
        OutlineSection(
            "Title 2", level=0, page_number=1, dest=DestinationXYZ(page=3, top=0)
        ),
        OutlineSection(
            "Subtitle 2.1", level=1, page_number=1, dest=DestinationXYZ(page=4, top=0)
        ),
        OutlineSection(
            "Subtitle 2.2", level=1, page_number=1, dest=DestinationXYZ(page=5, top=0)
        ),
    )
    assert (
        _serialize_outline(sections, first_object_id=6)
        == """\
6 0 obj
<<
/Count 2
/First 7 0 R
/Last 9 0 R
/Type /Outlines
>>
endobj
7 0 obj
<<
/Count 1
/Dest [3 0 R /XYZ 0 0 null]
/First 8 0 R
/Last 8 0 R
/Next 9 0 R
/Parent 6 0 R
/Title (Title 1)
>>
endobj
8 0 obj
<<
/Count 0
/Dest [5 0 R /XYZ 0 0 null]
/Parent 7 0 R
/Title (Subtitle 1.1)
>>
endobj
9 0 obj
<<
/Count 2
/Dest [7 0 R /XYZ 0 0 null]
/First 10 0 R
/Last 11 0 R
/Parent 6 0 R
/Prev 7 0 R
/Title (Title 2)
>>
endobj
10 0 obj
<<
/Count 0
/Dest [9 0 R /XYZ 0 0 null]
/Next 11 0 R
/Parent 9 0 R
/Title (Subtitle 2.1)
>>
endobj
11 0 obj
<<
/Count 0
/Dest [11 0 R /XYZ 0 0 null]
/Parent 9 0 R
/Prev 10 0 R
/Title (Subtitle 2.2)
>>
endobj"""
    )


def test__serialize_outline_with_headless_hierarchy():  # issues 239
    sections = (
        OutlineSection(
            "?-1", level=1, page_number=2, dest=DestinationXYZ(page=2, top=0)
        ),
        OutlineSection(
            "?-1-1", level=2, page_number=2, dest=DestinationXYZ(page=2, top=0)
        ),
        OutlineSection("1", level=0, page_number=2, dest=DestinationXYZ(page=2, top=0)),
        OutlineSection(
            "1-1", level=1, page_number=2, dest=DestinationXYZ(page=2, top=0)
        ),
        OutlineSection(
            "1-1-1", level=2, page_number=2, dest=DestinationXYZ(page=2, top=0)
        ),
    )
    assert (
        _serialize_outline(sections, first_object_id=6)
        == """\
6 0 obj
<<
/Count 2
/First 7 0 R
/Last 9 0 R
/Type /Outlines
>>
endobj
7 0 obj
<<
/Count 1
/Dest [5 0 R /XYZ 0 0 null]
/First 8 0 R
/Last 8 0 R
/Parent 6 0 R
/Title (?-1)
>>
endobj
8 0 obj
<<
/Count 0
/Dest [5 0 R /XYZ 0 0 null]
/Parent 7 0 R
/Title (?-1-1)
>>
endobj
9 0 obj
<<
/Count 1
/Dest [5 0 R /XYZ 0 0 null]
/First 10 0 R
/Last 10 0 R
/Parent 6 0 R
/Title (1)
>>
endobj
10 0 obj
<<
/Count 1
/Dest [5 0 R /XYZ 0 0 null]
/First 11 0 R
/Last 11 0 R
/Parent 9 0 R
/Title (1-1)
>>
endobj
11 0 obj
<<
/Count 0
/Dest [5 0 R /XYZ 0 0 null]
/Parent 10 0 R
/Title (1-1-1)
>>
endobj"""
    )


def test_serialize_outline_with_hex_encoding():  # issue-458
    sections = (
        OutlineSection(
            "Title with non-ASCCI letters: éêè",
            level=0,
            page_number=1,
            dest=DestinationXYZ(page=1, top=0),
        ),
    )
    assert (
        _serialize_outline(sections, first_object_id=1)
        == """\
1 0 obj
<<
/Count 1
/First 2 0 R
/Last 2 0 R
/Type /Outlines
>>
endobj
2 0 obj
<<
/Count 0
/Dest [3 0 R /XYZ 0 0 null]
/Parent 1 0 R
/Title <feff005400690074006c0065002000770069007400680020006e006f006e002d004100530043004300490020006c006500740074006500720073003a002000e900ea00e8>
>>
endobj"""
    )


def test_serialize_outline_without_hex_encoding():  # issue-458
    PDFString.USE_HEX_ENCODING = False
    try:
        sections = (
            OutlineSection(
                "Title with non-ASCCI letters: éêè",
                level=0,
                page_number=1,
                dest=DestinationXYZ(page=1, top=0),
            ),
        )
        assert (
            _serialize_outline(sections, first_object_id=1)
            == f"""\
1 0 obj
<<
/Count 1
/First 2 0 R
/Last 2 0 R
/Type /Outlines
>>
endobj
2 0 obj
<<
/Count 0
/Dest [3 0 R /XYZ 0 0 null]
/Parent 1 0 R
/Title ({'Title with non-ASCCI letters: éêè'.encode('UTF-16').decode('latin-1')})
>>
endobj"""
        )
    finally:
        PDFString.USE_HEX_ENCODING = True  # restore default value

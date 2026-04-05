from src.parser import parse_header

def test_parse_header_entry_id():
    text = """
    entry_id: 1ABC
    method: X-RAY DIFFRACTION
    """
    data = parse_header(text)
    assert data["entry_id"] == "1ABC"
    assert data["method"] == "X-RAY DIFFRACTION"

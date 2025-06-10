from pathlib import Path
from creative_autogen.src.lp_parser import parse_lp


def test_summary_not_empty():
    file_url = 'file://' + str(Path(__file__).parent / 'fixtures' / 'test_lp.html')
    summary = parse_lp(file_url)
    assert summary

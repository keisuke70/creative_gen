from creative_autogen.src.copy_generator import generate_copy


def test_generate_at_least_three_lines():
    copies = generate_copy("Amazing widget that does things", n=3)
    assert len(copies) >= 3

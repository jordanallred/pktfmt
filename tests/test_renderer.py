"""Tests for pktfmt.renderer."""

import pytest

from pktfmt.parser import parse_inline
from pktfmt.renderer import ASCII_CHARS, UNICODE_CHARS, get_box_chars, render_diagram


def test_get_box_chars_ascii():
    assert get_box_chars("ascii") == ASCII_CHARS


def test_get_box_chars_unicode():
    assert get_box_chars("unicode") == UNICODE_CHARS


def test_get_box_chars_bold_no_longer_supported():
    # "bold" was removed; unknown styles fall back to ascii.
    assert get_box_chars("bold") == ASCII_CHARS


def test_get_box_chars_unknown_falls_back_to_ascii():
    assert get_box_chars("nonsense") == ASCII_CHARS


def test_render_ascii_with_ruler():
    fields = parse_inline("Type:16,Length:16,Payload:*")
    diagram = render_diagram(fields, bits_per_row=32, show_ruler=True, style="ascii")

    expected = (
        " 0                  1                  2                  3\n"
        " 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1\n"
        "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
        "|              Type             |             Length            |\n"
        "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
        ":                            Payload                            :\n"
        "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
    )
    assert diagram == expected


def test_render_unicode_without_ruler():
    fields = parse_inline("Type:16,Length:16,Payload:*")
    diagram = render_diagram(fields, bits_per_row=32, show_ruler=False, style="unicode")

    expected = (
        "┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐\n"
        "│              Type             │             Length            │\n"
        "├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤\n"
        "┊                            Payload                            ┊\n"
        "└─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘"
    )
    assert diagram == expected


def test_render_field_spanning_multiple_rows():
    # 24-bit field with only 16 bits per row must wrap across two rows,
    # leaving the continuation row's field cell blank and the name in
    # the row where the field actually ends.
    fields = parse_inline("Flags:24")
    diagram = render_diagram(fields, bits_per_row=16, show_ruler=False, style="ascii")

    expected = (
        "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
        "|                               |\n"
        "+                -+-+-+-+-+-+-+-+\n"
        "|     Flags     |\n"
        "+-+-+-+-+-+-+-+-+"
    )
    assert diagram == expected


def test_render_empty_fields_produces_no_diagram():
    assert render_diagram([], show_ruler=False) == ""


def test_bold_style_choice_rejected_by_cli_parser():
    from pktfmt.cli import create_parser

    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["tcp", "--style", "bold"])

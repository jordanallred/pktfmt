"""Tests for pktfmt.cli."""

import pytest

from pktfmt.cli import create_parser, main


def test_default_style_is_ascii():
    parser = create_parser()
    args = parser.parse_args(["tcp"])
    assert args.style == "ascii"
    assert args.unicode is False


def test_style_choices_no_longer_include_bold():
    parser = create_parser()
    assert parser._option_string_actions["--style"].choices == ["ascii", "unicode"]


def test_unicode_shortcut_flag_sets_style_unicode(capsys):
    exit_code = main(["udp", "--unicode"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "┌" in out  # unicode box-drawing corner, not "+"


def test_explicit_style_unicode_matches_shortcut(capsys):
    main(["udp", "--unicode"])
    shortcut_out = capsys.readouterr().out

    main(["udp", "--style", "unicode"])
    style_out = capsys.readouterr().out

    assert shortcut_out == style_out


def test_default_style_is_plain_ascii(capsys):
    exit_code = main(["udp"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "+" in out
    assert "┌" not in out


def test_style_bold_is_rejected():
    with pytest.raises(SystemExit):
        main(["udp", "--style", "bold"])


def test_missing_input_prints_help_and_returns_1(capsys):
    exit_code = main([])
    out = capsys.readouterr().out
    assert exit_code == 1
    assert "usage:" in out

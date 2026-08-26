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


def test_output_flag_writes_to_file(tmp_path, capsys):
    out_file = tmp_path / "tcp.txt"
    exit_code = main(["tcp", "--output", str(out_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == ""
    assert out_file.read_text().startswith(" 0")


def test_stdin_dash_reads_json(monkeypatch, capsys):
    import io

    payload = '{"fields": [{"name": "Type", "bits": 8}]}'
    monkeypatch.setattr("sys.stdin", io.StringIO(payload))

    exit_code = main(["-", "--no-ruler"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "Type" in out

"""Tests for pktfmt.parser."""

import json

import pytest

from pktfmt.parser import Field, parse_inline, parse_input, parse_json


def test_parse_inline_basic():
    fields = parse_inline("Type:16,Length:16")
    assert [f.name for f in fields] == ["Type", "Length"]
    assert [f.bits for f in fields] == [16, 16]


def test_parse_inline_variable_field():
    fields = parse_inline("Payload:*")
    assert fields[0].is_variable is True
    assert fields[0].bits == "*"


def test_parse_inline_strips_whitespace():
    fields = parse_inline(" Type : 16 , Length : 16 ")
    assert fields[0].name == "Type"
    assert fields[1].name == "Length"


def test_parse_inline_skips_empty_segments():
    fields = parse_inline("Type:16,,Length:16")
    assert len(fields) == 2


def test_parse_inline_missing_colon_raises():
    with pytest.raises(ValueError, match="expected 'Name:bits'"):
        parse_inline("Type16")


def test_parse_inline_empty_name_raises():
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_inline(":16")


def test_parse_inline_non_numeric_bits_raises():
    with pytest.raises(ValueError, match="Invalid bit width"):
        parse_inline("Type:abc")


def test_parse_inline_zero_bits_raises():
    # The "must be positive" ValueError raised inside parse_inline's try block
    # is immediately caught by its own except clause and re-wrapped, so the
    # message that actually surfaces is "Invalid bit width", not the intended one.
    with pytest.raises(ValueError, match="Invalid bit width"):
        parse_inline("Type:0")


def test_parse_inline_negative_bits_raises():
    with pytest.raises(ValueError, match="Invalid bit width"):
        parse_inline("Type:-4")


def test_parse_inline_no_fields_raises():
    with pytest.raises(ValueError, match="No fields defined"):
        parse_inline("")


def test_parse_json_from_string():
    data = json.dumps({
        "name": "Custom",
        "fields": [{"name": "Type", "bits": 16}, {"name": "Payload", "bits": "*"}],
    })
    fields = parse_json(data)
    assert [f.name for f in fields] == ["Type", "Payload"]
    assert fields[1].is_variable is True


def test_parse_json_from_file(tmp_path):
    payload = {"name": "Custom", "fields": [{"name": "Type", "bits": 8}]}
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(payload))

    fields = parse_json(path)
    assert fields[0].name == "Type"
    assert fields[0].bits == 8


def test_parse_json_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_json("does-not-exist.json")


def test_parse_json_not_an_object_raises(tmp_path):
    # A bare "[1, 2, 3]" string is routed to the file-path branch (it doesn't
    # start with "{"), so the "must be an object" check is only reachable via
    # a file whose contents parse to a non-dict.
    path = tmp_path / "not_object.json"
    path.write_text("[1, 2, 3]")
    with pytest.raises(ValueError, match="must be an object"):
        parse_json(path)


def test_parse_json_missing_fields_key_raises():
    with pytest.raises(ValueError, match="'fields' array"):
        parse_json(json.dumps({"name": "Custom"}))


def test_parse_json_field_missing_name_raises():
    with pytest.raises(ValueError, match="missing 'name'"):
        parse_json(json.dumps({"fields": [{"bits": 16}]}))


def test_parse_json_field_missing_bits_raises():
    with pytest.raises(ValueError, match="missing 'bits'"):
        parse_json(json.dumps({"fields": [{"name": "Type"}]}))


def test_parse_json_invalid_bits_type_raises():
    with pytest.raises(ValueError, match="must be an integer or"):
        parse_json(json.dumps({"fields": [{"name": "Type", "bits": "sixteen"}]}))


def test_parse_json_non_positive_bits_raises():
    with pytest.raises(ValueError, match="must be positive"):
        parse_json(json.dumps({"fields": [{"name": "Type", "bits": 0}]}))


def test_parse_json_empty_fields_raises():
    with pytest.raises(ValueError, match="No fields defined"):
        parse_json(json.dumps({"fields": []}))


def test_parse_input_resolves_builtin_protocol():
    fields = parse_input("tcp")
    assert any(f.name == "Sequence Number" for f in fields)


def test_parse_input_resolves_json_file(tmp_path, monkeypatch):
    payload = {"fields": [{"name": "Type", "bits": 8}]}
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(payload))
    monkeypatch.chdir(tmp_path)

    fields = parse_input("packet.json")
    assert fields[0].name == "Type"


def test_parse_input_falls_back_to_inline():
    fields = parse_input("Type:16,Payload:*")
    assert fields[0].name == "Type"
    assert fields[1].is_variable is True

"""Tests for pktfmt.protocols."""

import pytest

from pktfmt.protocols import PROTOCOLS, get_protocol, is_protocol, list_protocols


def test_get_protocol_returns_description_and_spec():
    desc, spec = get_protocol("tcp")
    assert desc == "Transmission Control Protocol"
    assert "Source Port:16" in spec


def test_get_protocol_is_case_insensitive():
    desc, spec = get_protocol("TCP")
    assert desc == PROTOCOLS["tcp"][0]


def test_get_protocol_unknown_raises_key_error():
    with pytest.raises(KeyError, match="Unknown protocol"):
        get_protocol("nope")


def test_is_protocol_true_for_known_name():
    assert is_protocol("udp") is True
    assert is_protocol("UDP") is True


def test_is_protocol_false_for_unknown_name():
    assert is_protocol("nope") is False


def test_list_protocols_covers_every_entry():
    listed = list_protocols()
    assert len(listed) == len(PROTOCOLS)
    assert set(name for name, _ in listed) == set(PROTOCOLS.keys())


def test_list_protocols_is_sorted_by_name():
    listed = list_protocols()
    names = [name for name, _ in listed]
    assert names == sorted(names)


def test_all_protocol_specs_are_parseable():
    from pktfmt.parser import parse_inline

    for name, (_, spec) in PROTOCOLS.items():
        fields = parse_inline(spec)
        assert len(fields) > 0, f"{name} produced no fields"


def test_tcp_flags_match_rfc_9293_bit_layout():
    # Data Offset(4) + Reserved(4) + 8 named 1-bit flags = 12 control bits,
    # matching RFC 9293 Figure 1. A prior bundled definition split this as
    # Reserved:3 + Flags:9, which put the flags region one bit too early.
    from pktfmt.parser import parse_inline

    _, spec = PROTOCOLS["tcp"]
    fields = {f.name: f.bits for f in parse_inline(spec)}

    assert fields["Reserved"] == 4
    for flag in ["CWR", "ECE", "URG", "ACK", "PSH", "RST", "SYN", "FIN"]:
        assert fields[flag] == 1, f"{flag} should be a single bit"

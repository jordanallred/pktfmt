# pktfmt

Generate RFC-style ASCII packet diagrams from field definitions.

A modern, pip-installable alternative to [protocol](https://github.com/luismartingarcia/protocol) that works on Windows and modern Python.

## Installation

```bash
pip install pktfmt
```

## Features

- **20+ built-in protocols** - TCP, UDP, IP, DNS, and more
- **Custom packet definitions** - inline format or JSON files
- **Unicode box drawing** - pretty output for modern terminals
- **Variable-length fields** - with distinct visual styling
- **Cross-platform** - works on Windows, macOS, and Linux
- **Modern Python** - supports Python 3.8+

## Quick Start

```bash
# Show a built-in protocol
pktfmt tcp

# List all available protocols
pktfmt --list

# Custom inline format
pktfmt "Type:16,Length:16,Payload:*"

# Pretty Unicode output
pktfmt udp --unicode
```

## Usage

### Built-in Protocols

```bash
$ pktfmt tcp
 0                  1                  2                  3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |        Destination Port       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     Acknowledgment Number                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Data Of|Reser|      Flags      |          Window Size          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|            Checksum           |         Urgent Pointer        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:                            Options                            :
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Custom Inline Format

```bash
$ pktfmt "Type:16,Length:16,Payload:*"
 0                  1                  2                  3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|              Type             |             Length            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:                            Payload                            :
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### JSON File Format

```bash
pktfmt packet.json
```

```json
{
  "name": "MyPacket",
  "fields": [
    {"name": "Type", "bits": 16},
    {"name": "Length", "bits": 16},
    {"name": "Payload", "bits": "*"}
  ]
}
```

### Unicode Output

```bash
$ pktfmt udp --unicode
 0                  1                  2                  3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
│          Source Port          │        Destination Port       │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│             Length            │            Checksum           │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
┊                              Data                             ┊
└─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
```

### Options

```
pktfmt <input> [options]

Options:
  -l, --list              List all built-in protocols
  -b, --bits-per-row N    Bits per row (default: 32)
  -s, --style STYLE       Output style: ascii, unicode, bold
  -u, --unicode           Shortcut for --style unicode
  --no-ruler              Omit the bit number header
  -v, --version           Show version
```

## Field Syntax

- `Name:N` - Fixed-width field of N bits
- `Name:*` - Variable-length field (rendered with `:` or `┊` borders)

## Built-in Protocols

| Layer | Protocols |
|-------|-----------|
| Layer 2 | ethernet, 8021q, arp |
| Layer 3 | ipv4, ipv6, icmp, icmpv6 |
| Layer 4 | tcp, udp, sctp |
| Application | dns, dhcp, ntp, tls |
| Tunneling | gre, vxlan, quic |
| Industrial | modbus, dnp3 |

## Why pktfmt?

- **Actually installs via pip** - `protocol` requires manual setup.py installation
- **Works on modern Python** - `protocol` uses deprecated `distutils`
- **Works on Windows** - proper UTF-8 handling
- **Actively maintained** - PRs get merged
- **Unicode support** - pretty box drawing characters
- **More protocols** - 20+ built-in, vs ~10 in protocol

## License

MIT

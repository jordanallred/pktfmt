# pktfmt

Generate RFC-style ASCII packet diagrams from field definitions.

## Installation

```bash
pip install pktfmt
```

## Usage

### Inline format

```bash
pktfmt "Type:16,Length:16,Payload:*"
```

Output:
```
 0                  1                  2                  3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|              Type             |             Length            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:                            Payload                            :
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### JSON file

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

### Options

```bash
pktfmt "Type:16,Data:32" --bits-per-row 16   # Custom row width
pktfmt "Type:32" --no-ruler                   # Omit bit number header
```

## Field syntax

- `Name:N` - Fixed-width field of N bits
- `Name:*` - Variable-length field (rendered with `:` borders)

## License

MIT

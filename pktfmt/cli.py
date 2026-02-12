"""Command-line interface for pktfmt."""

import argparse
import sys
from typing import List, Optional

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from . import __version__
from .parser import parse_input
from .protocols import list_protocols, get_protocol
from .renderer import render_diagram


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pktfmt",
        description="Generate RFC-style ASCII packet diagrams from field definitions.",
        epilog="""
Examples:
  pktfmt tcp                              # Built-in TCP header
  pktfmt --list                           # Show all built-in protocols
  pktfmt "Type:16,Length:16,Payload:*"    # Custom inline format
  pktfmt packet.json                      # Load from JSON file
  pktfmt udp --unicode                    # Pretty Unicode output
  pktfmt ip -b 16                         # 16 bits per row
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Protocol name, inline 'Name:bits,...' format, or JSON file path",
    )

    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all built-in protocols",
    )

    parser.add_argument(
        "-b", "--bits-per-row",
        type=int,
        default=32,
        metavar="N",
        help="Number of bits per row (default: 32)",
    )

    parser.add_argument(
        "--no-ruler",
        action="store_true",
        help="Omit the bit number header",
    )

    parser.add_argument(
        "-s", "--style",
        choices=["ascii", "unicode", "bold"],
        default="ascii",
        help="Output style (default: ascii)",
    )

    parser.add_argument(
        "-u", "--unicode",
        action="store_true",
        help="Use Unicode box drawing characters (shortcut for --style unicode)",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def print_protocol_list() -> None:
    """Print list of available protocols."""
    protocols = list_protocols()

    print("Available protocols:\n")

    # Group by layer for nicer output
    layers = {
        "Layer 2 (Data Link)": ["ethernet", "8021q", "arp"],
        "Layer 3 (Network)": ["ipv4", "ip", "ipv6", "icmp", "icmpv6"],
        "Layer 4 (Transport)": ["tcp", "udp", "sctp"],
        "Application": ["dns", "dhcp", "ntp", "tls"],
        "Tunneling": ["gre", "vxlan", "quic"],
        "Industrial/ICS": ["modbus", "dnp3"],
    }

    printed = set()
    for layer, proto_names in layers.items():
        layer_protos = [(n, d) for n, d in protocols if n in proto_names]
        if layer_protos:
            print(f"  {layer}:")
            for name, desc in layer_protos:
                print(f"    {name:<12} {desc}")
                printed.add(name)
            print()

    # Print any remaining protocols not in our categories
    remaining = [(n, d) for n, d in protocols if n not in printed]
    if remaining:
        print("  Other:")
        for name, desc in remaining:
            print(f"    {name:<12} {desc}")
        print()

    print("Usage: pktfmt <protocol_name>")
    print("Example: pktfmt tcp")


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Handle --list
    if args.list:
        print_protocol_list()
        return 0

    # Require input if not --list
    if not args.input:
        parser.print_help()
        return 1

    # Determine style
    style = args.style
    if args.unicode:
        style = "unicode"

    try:
        fields = parse_input(args.input)
        diagram = render_diagram(
            fields,
            bits_per_row=args.bits_per_row,
            show_ruler=not args.no_ruler,
            style=style,
        )
        print(diagram)
        return 0
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

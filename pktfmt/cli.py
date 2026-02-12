"""Command-line interface for pktfmt."""

import argparse
import sys
from typing import List, Optional

from . import __version__
from .parser import parse_input
from .renderer import render_diagram


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pktfmt",
        description="Generate RFC-style ASCII packet diagrams from field definitions.",
        epilog="""
Examples:
  pktfmt "Type:16,Length:16,Payload:*"
  pktfmt packet.json
  pktfmt "Type:16,Data:32" --bits-per-row 16
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input",
        help="Field definition (inline 'Name:bits,...' format) or path to JSON file",
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
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        fields = parse_input(args.input)
        diagram = render_diagram(
            fields,
            bits_per_row=args.bits_per_row,
            show_ruler=not args.no_ruler,
        )
        print(diagram)
        return 0
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

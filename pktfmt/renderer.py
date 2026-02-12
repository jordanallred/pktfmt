"""Render ASCII packet diagrams in RFC style."""

from typing import List, Optional
from .parser import Field


def render_diagram(fields: List[Field], bits_per_row: int = 32, show_ruler: bool = True) -> str:
    """Render fields as an RFC-style ASCII packet diagram.

    Args:
        fields: List of Field objects to render
        bits_per_row: Number of bits per row (default 32)
        show_ruler: Whether to show the bit number header

    Returns:
        ASCII diagram string
    """
    lines = []

    # Generate ruler
    if show_ruler:
        lines.extend(_generate_ruler(bits_per_row))

    # Build list of rows, each row is list of (name, width, is_variable, is_continuation)
    rows = []
    current_row = []
    current_bit = 0

    for field in fields:
        if field.is_variable:
            # Flush current row if any
            if current_row:
                rows.append(current_row)
                current_row = []
                current_bit = 0

            # Variable field gets its own full-width row
            rows.append([(field.name, bits_per_row, True, False)])
        else:
            bits_remaining = field.bits
            is_first_part = True

            while bits_remaining > 0:
                space_in_row = bits_per_row - current_bit

                if bits_remaining <= space_in_row:
                    # Field fits in current row
                    current_row.append((field.name, bits_remaining, False, not is_first_part))
                    current_bit += bits_remaining
                    bits_remaining = 0

                    # If row is complete, flush it
                    if current_bit == bits_per_row:
                        rows.append(current_row)
                        current_row = []
                        current_bit = 0
                else:
                    # Field spans to next row
                    current_row.append((field.name, space_in_row, False, not is_first_part))
                    rows.append(current_row)
                    current_row = []
                    current_bit = 0
                    bits_remaining -= space_in_row
                    is_first_part = False

    # Flush any remaining partial row
    if current_row:
        rows.append(current_row)

    # Render rows
    separator = "+" + "-+" * bits_per_row
    prev_continues_to_next = False

    for i, row in enumerate(rows):
        row_width = sum(f[1] for f in row)
        is_full_row = row_width == bits_per_row
        has_variable = any(f[2] for f in row)

        # Check if first field in this row is a continuation
        first_is_continuation = row[0][3] if row else False

        # Check if last field continues to next row
        continues_to_next = False
        if i + 1 < len(rows) and row:
            next_row = rows[i + 1]
            if next_row and next_row[0][3]:  # Next row's first field is continuation
                continues_to_next = True

        # Add separator (skip if this row continues from previous)
        if not first_is_continuation:
            if is_full_row:
                lines.append(separator)
            else:
                lines.append("+" + "-+" * row_width)
            # Render the row content
            lines.append(_render_field_row(row, bits_per_row, has_variable))
        else:
            # Continuation row - just side borders, blank inside (no separator, no content row)
            lines.append("|" + " " * (bits_per_row * 2 - 1) + "|")

        prev_continues_to_next = continues_to_next

    # Final separator
    if rows:
        last_row = rows[-1]
        last_width = sum(f[1] for f in last_row)
        lines.append("+" + "-+" * last_width)

    return "\n".join(lines)


def _generate_ruler(bits_per_row: int) -> List[str]:
    """Generate the bit number ruler header."""
    # First line: byte markers (0, 1, 2, 3 for 32-bit)
    byte_line = " "
    for byte_num in range(bits_per_row // 8):
        byte_line += f"{byte_num:<19}"
    byte_line = byte_line[:bits_per_row * 2]

    # Second line: bit numbers within each byte (0-9, repeating)
    bit_line = " "
    for i in range(bits_per_row):
        bit_line += f"{i % 10} "
    bit_line = bit_line.rstrip()

    return [byte_line.rstrip(), bit_line]


def _render_field_row(row_fields: List[tuple], bits_per_row: int, has_variable: bool) -> str:
    """Render a single row of fields.

    Args:
        row_fields: List of (name, width, is_variable, is_continuation) tuples
        bits_per_row: Number of bits per row
        has_variable: Whether this row contains a variable-length field

    Returns:
        Rendered row string
    """
    border = ":" if has_variable else "|"
    result = border

    for name, width, is_var, is_continuation in row_fields:
        cell_width = width * 2 - 1

        if is_continuation:
            # Show blank or continuation indicator for multi-row fields
            display_name = " " * cell_width
        else:
            # Center the name
            if len(name) > cell_width:
                display_name = name[:cell_width]
            else:
                display_name = name.center(cell_width)

        result += display_name + border

    return result

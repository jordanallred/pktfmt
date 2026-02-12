"""Render ASCII packet diagrams in RFC style."""

from typing import List, NamedTuple


class BoxChars(NamedTuple):
    """Box drawing character set."""
    h: str      # horizontal
    v: str      # vertical
    tl: str     # top-left corner
    tr: str     # top-right corner
    bl: str     # bottom-left corner
    br: str     # bottom-right corner
    tj: str     # top junction (T pointing down)
    bj: str     # bottom junction (T pointing up)
    lj: str     # left junction (T pointing right)
    rj: str     # right junction (T pointing left)
    x: str      # cross/plus
    v_var: str  # vertical for variable fields


# ASCII style (RFC-compatible)
ASCII_CHARS = BoxChars(
    h="-", v="|", tl="+", tr="+", bl="+", br="+",
    tj="+", bj="+", lj="+", rj="+", x="+", v_var=":"
)

# Unicode box drawing
UNICODE_CHARS = BoxChars(
    h="─", v="│", tl="┌", tr="┐", bl="└", br="┘",
    tj="┬", bj="┴", lj="├", rj="┤", x="┼", v_var="┊"
)

# Unicode bold/heavy
UNICODE_BOLD_CHARS = BoxChars(
    h="━", v="┃", tl="┏", tr="┓", bl="┗", br="┛",
    tj="┳", bj="┻", lj="┣", rj="┫", x="╋", v_var="┇"
)


class FieldSegment(NamedTuple):
    """A segment of a field within a single row."""
    name: str
    width: int              # bits in this row
    is_variable: bool
    is_continuation: bool   # field started in a previous row
    continues_next: bool    # field continues to next row


def get_box_chars(style: str) -> BoxChars:
    """Get box drawing characters for a style."""
    styles = {
        "ascii": ASCII_CHARS,
        "unicode": UNICODE_CHARS,
        "bold": UNICODE_BOLD_CHARS,
    }
    return styles.get(style, ASCII_CHARS)


def render_diagram(
    fields: List,
    bits_per_row: int = 32,
    show_ruler: bool = True,
    style: str = "ascii"
) -> str:
    """Render fields as an RFC-style packet diagram."""
    chars = get_box_chars(style)
    lines = []

    if show_ruler:
        lines.extend(_generate_ruler(bits_per_row))

    # Build rows with field segments
    rows: List[List[FieldSegment]] = []
    current_row: List[FieldSegment] = []
    current_bit = 0

    for field in fields:
        if field.is_variable:
            if current_row:
                rows.append(current_row)
                current_row = []
                current_bit = 0
            rows.append([FieldSegment(field.name, bits_per_row, True, False, False)])
        else:
            bits_remaining = field.bits
            is_first_part = True

            while bits_remaining > 0:
                space_in_row = bits_per_row - current_bit

                if bits_remaining <= space_in_row:
                    seg = FieldSegment(
                        field.name, bits_remaining, False,
                        not is_first_part,
                        False
                    )
                    current_row.append(seg)
                    current_bit += bits_remaining
                    bits_remaining = 0

                    if current_bit == bits_per_row:
                        rows.append(current_row)
                        current_row = []
                        current_bit = 0
                else:
                    seg = FieldSegment(
                        field.name, space_in_row, False,
                        not is_first_part,
                        True
                    )
                    current_row.append(seg)
                    rows.append(current_row)
                    current_row = []
                    current_bit = 0
                    bits_remaining -= space_in_row
                    is_first_part = False

    if current_row:
        rows.append(current_row)

    # Render rows
    for i, row in enumerate(rows):
        is_first_row = i == 0
        prev_row = rows[i - 1] if i > 0 else None
        has_variable = any(seg.is_variable for seg in row)

        lines.append(_make_separator(row, prev_row, chars, is_first_row, bits_per_row))
        lines.append(_render_field_row(row, chars, has_variable))

    if rows:
        lines.append(_make_bottom_separator(rows[-1], chars, bits_per_row))

    return "\n".join(lines)


def _generate_ruler(bits_per_row: int) -> List[str]:
    """Generate the bit number ruler header."""
    byte_line = " "
    for byte_num in range(bits_per_row // 8):
        byte_line += f"{byte_num:<19}"
    byte_line = byte_line[:bits_per_row * 2]

    bit_line = " "
    for i in range(bits_per_row):
        bit_line += f"{i % 10} "
    bit_line = bit_line.rstrip()

    return [byte_line.rstrip(), bit_line]


def _make_separator(
    row: List[FieldSegment],
    prev_row: List[FieldSegment],
    chars: BoxChars,
    is_first_row: bool,
    bits_per_row: int
) -> str:
    """Generate separator line above a row."""

    if is_first_row:
        # Simple top border
        result = "+"
        for seg in row:
            result += "-+" * seg.width
        return result

    # For each bit position, determine if we need a line or space
    # Line is drawn if: field ends above OR field starts below
    # Space is drawn if: same field continues through this boundary

    # Build arrays for: does field end at this bit (from prev_row)?
    #                   does field start at this bit (from row)?
    prev_ends = []      # True if the field in prev_row ends here (not continues_next)
    curr_starts = []    # True if the field in row starts here (not is_continuation)

    for seg in prev_row:
        prev_ends.extend([False] * (seg.width - 1) + [not seg.continues_next])

    for seg in row:
        curr_starts.extend([not seg.is_continuation] + [False] * (seg.width - 1))

    # Pad arrays
    while len(prev_ends) < bits_per_row:
        prev_ends.append(True)
    while len(curr_starts) < bits_per_row:
        curr_starts.append(True)

    # Build the separator
    result = "+"

    pos = 0
    for seg in row:
        for bit_offset in range(seg.width):
            bit_pos = pos + bit_offset

            # Does this bit need a line above it?
            # Yes if: field ended in prev row at or before this position
            #     OR: field starts in current row at or after this position
            # Actually simpler: draw line if field_above ended OR field_below starts
            # Draw space if same field continues through

            # Check if this bit is a continuation from above
            needs_line = not seg.is_continuation

            if needs_line:
                result += "-+"
            else:
                result += " +"

        pos += seg.width

    # Fix: we need to handle boundaries correctly
    # Let me rewrite this more carefully

    return _make_separator_v2(row, prev_row, chars, bits_per_row)


def _make_separator_v2(
    row: List[FieldSegment],
    prev_row: List[FieldSegment],
    chars: BoxChars,
    bits_per_row: int
) -> str:
    """Generate separator between two rows.

    Draw `-+-+-+` pattern where fields END above (continues_next=False).
    Draw spaces where fields CONTINUE (continues_next=True).
    """
    # Build info about prev_row fields: for each bit, does field continue?
    prev_continues_map = []  # For each bit: True if field continues to next row
    for seg in prev_row:
        prev_continues_map.extend([seg.continues_next] * seg.width)
    while len(prev_continues_map) < bits_per_row:
        prev_continues_map.append(False)

    # Build info about current row: for each bit, is it a continuation?
    curr_continuation_map = []
    for seg in row:
        curr_continuation_map.extend([seg.is_continuation] * seg.width)
    while len(curr_continuation_map) < bits_per_row:
        curr_continuation_map.append(False)

    # Get field boundaries in both rows
    prev_boundaries = set([0])
    pos = 0
    for seg in prev_row:
        pos += seg.width
        prev_boundaries.add(pos)

    curr_boundaries = set([0])
    pos = 0
    for seg in row:
        pos += seg.width
        curr_boundaries.add(pos)

    all_boundaries = prev_boundaries | curr_boundaries

    # Build separator
    result = ""
    for bit in range(bits_per_row):
        # Junction at start of this bit
        if bit == 0:
            result += "+"
        else:
            # Check if we need a junction here
            if bit in all_boundaries:
                result += "+"
            elif prev_continues_map[bit - 1] and curr_continuation_map[bit]:
                # Field continues through - no junction
                result += " "
            else:
                result += "+"

        # Line or space for this bit
        # Draw line if: field ends above OR field starts below
        # Draw space only if: field continues AND no new field starts
        if prev_continues_map[bit] and curr_continuation_map[bit]:
            result += " "
        else:
            result += "-"

    # Final junction
    result += "+"

    return result


def _make_bottom_separator(row: List[FieldSegment], chars: BoxChars, bits_per_row: int) -> str:
    """Generate the final separator line at the bottom."""
    result = "+"
    for seg in row:
        result += "-+" * seg.width
    return result


def _render_field_row(row: List[FieldSegment], chars: BoxChars, has_variable: bool) -> str:
    """Render a single row of fields.

    Field names are shown in the LAST segment (where continues_next is False).
    This puts the name in the segment with the most space.
    """
    border = chars.v_var if has_variable else chars.v
    result = border

    for seg in row:
        cell_width = seg.width * 2 - 1

        # Show name only in last segment of multi-row field (continues_next=False)
        # For single-row fields, both is_continuation=False and continues_next=False
        if seg.continues_next:
            # This segment continues to next row - leave blank
            display_name = " " * cell_width
        else:
            # This is the last (or only) segment - show name
            if len(seg.name) > cell_width:
                display_name = seg.name[:cell_width]
            else:
                display_name = seg.name.center(cell_width)

        result += display_name + border

    return result

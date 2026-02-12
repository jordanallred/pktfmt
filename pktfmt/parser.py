"""Parse packet field definitions from inline strings and JSON files."""

import json
from pathlib import Path
from typing import List, Union


class Field:
    """Represents a packet field with a name and bit width."""

    def __init__(self, name: str, bits: Union[int, str]):
        self.name = name
        self.bits = bits  # int for fixed width, "*" for variable

    @property
    def is_variable(self) -> bool:
        return self.bits == "*"

    def __repr__(self) -> str:
        return f"Field({self.name!r}, {self.bits!r})"


def parse_inline(definition: str) -> List[Field]:
    """Parse inline format: 'Name:bits,Name:bits,Name:*'

    Args:
        definition: Comma-separated field definitions

    Returns:
        List of Field objects

    Raises:
        ValueError: If the format is invalid
    """
    fields = []

    for part in definition.split(","):
        part = part.strip()
        if not part:
            continue

        if ":" not in part:
            raise ValueError(f"Invalid field format: '{part}' (expected 'Name:bits')")

        name, bits_str = part.rsplit(":", 1)
        name = name.strip()
        bits_str = bits_str.strip()

        if not name:
            raise ValueError(f"Field name cannot be empty: '{part}'")

        if bits_str == "*":
            bits = "*"
        else:
            try:
                bits = int(bits_str)
                if bits <= 0:
                    raise ValueError(f"Bit width must be positive: '{part}'")
            except ValueError:
                raise ValueError(f"Invalid bit width: '{bits_str}' in '{part}'")

        fields.append(Field(name, bits))

    if not fields:
        raise ValueError("No fields defined")

    return fields


def parse_json(json_input: Union[str, Path]) -> List[Field]:
    """Parse JSON format for packet definition.

    Args:
        json_input: JSON string or path to JSON file

    Returns:
        List of Field objects

    Raises:
        ValueError: If the JSON format is invalid
    """
    # Try to load as file first
    if isinstance(json_input, Path) or (isinstance(json_input, str) and not json_input.strip().startswith("{")):
        path = Path(json_input)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            raise FileNotFoundError(f"File not found: {json_input}")
    else:
        data = json.loads(json_input)

    if not isinstance(data, dict):
        raise ValueError("JSON must be an object with a 'fields' array")

    if "fields" not in data:
        raise ValueError("JSON must contain a 'fields' array")

    fields = []
    for i, field_data in enumerate(data["fields"]):
        if not isinstance(field_data, dict):
            raise ValueError(f"Field {i} must be an object")

        if "name" not in field_data:
            raise ValueError(f"Field {i} missing 'name'")

        if "bits" not in field_data:
            raise ValueError(f"Field {i} missing 'bits'")

        name = field_data["name"]
        bits = field_data["bits"]

        if bits != "*" and not isinstance(bits, int):
            raise ValueError(f"Field '{name}': bits must be an integer or '*'")

        if isinstance(bits, int) and bits <= 0:
            raise ValueError(f"Field '{name}': bit width must be positive")

        fields.append(Field(name, bits))

    if not fields:
        raise ValueError("No fields defined")

    return fields


def parse_input(input_str: str) -> List[Field]:
    """Auto-detect and parse input format (inline or JSON file).

    Args:
        input_str: Either an inline definition or a path to a JSON file

    Returns:
        List of Field objects
    """
    # Check if it's a file path
    path = Path(input_str)
    if path.exists() and path.suffix.lower() == ".json":
        return parse_json(path)

    # Otherwise treat as inline format
    return parse_inline(input_str)

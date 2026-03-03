import argparse
import re


def parse_size(value: str) -> int:
    """Parse string representing a size into integer.

    Parse a human-readable size string (e.g. "100MB", "10KB", "102400") into an integer number of bytes.

    Parameters
    ----------
    value : str
        The size string to parse.

    Returns
    -------
    number : int
        The size in bytes.

    Raises
    ------
    argparse.ArgumentTypeError
        If the input string is not a valid size format.
    """

    value = value.strip()

    # Pure integer (bytes)
    if value.isdigit():
        return int(value)

    pattern = r"^(\d+(?:\.\d+)?)\s*([kKmMgG][bB]?)$"
    match = re.match(pattern, value)

    if not match:
        raise argparse.ArgumentTypeError(
            f"Invalid size format: {value}. Use e.g. 100MB, 10KB, 102400"
        )

    number, unit = match.groups()
    number = float(number)
    unit = unit.lower()

    multipliers = {
        "k": 1024,
        "kb": 1024,
        "m": 1024**2,
        "mb": 1024**2,
        "g": 1024**3,
        "gb": 1024**3,
    }

    return int(number * multipliers[unit])

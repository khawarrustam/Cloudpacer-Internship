"""Simple console messages for learning and debugging."""


def print_step(area: str, english: str, roman_urdu: str) -> None:
    """Print one action in easy English and Roman Urdu."""
    print(f"[{area}] {english}")
    print(f"  Roman Urdu: {roman_urdu}")


def print_error(area: str, english: str, roman_urdu: str) -> None:
    """Print one error in easy English and Roman Urdu."""
    print(f"[{area} ERROR] {english}")
    print(f"  Roman Urdu: {roman_urdu}")

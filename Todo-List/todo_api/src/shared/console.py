"""Simple backend console messages for learning and debugging.

English: Keep every print format in one file.
Roman Urdu: Har print ka format aik hi file mein rakha gaya hai.
"""


def module_file(instance: object) -> str:
    """Return the Python file path for an injected repository object."""
    module_path = instance.__class__.__module__.replace(".", "/")
    return f"{module_path}.py"


def find_layer(location: str) -> str:
    """Return the architecture layer for a file, client, or external service."""
    clean_location = location.lower()

    # English: Check project layers before general service words.
    # Roman Urdu: General service words se pehle project layers check karo.
    if "src/presentation/" in clean_location or "fastapi" in clean_location:
        return "PRESENTATION LAYER"
    if "src/application/" in clean_location:
        return "APPLICATION LAYER"
    if "src/domain/" in clean_location:
        return "DOMAIN LAYER"
    if "src/infrastructure/" in clean_location:
        return "INFRASTRUCTURE LAYER"
    if "frontend" in clean_location or "http authorization" in clean_location:
        return "CLIENT / HTTP"
    if "firebase" in clean_location or "firestore" in clean_location:
        return "EXTERNAL SERVICE"
    if "ram" in clean_location or "temporary memory" in clean_location:
        return "INFRASTRUCTURE STORAGE"

    return "BACKEND FLOW"


def print_flow(
    source: str,
    destination: str,
    data: str,
    english: str,
    roman_urdu: str,
) -> None:
    """Show where safe data came from and where it is going."""
    print("\n[DATA FLOW]")
    print(f"  FROM LAYER : {find_layer(source)}")
    print(f"  FROM       : {source}")
    print(f"  TO LAYER   : {find_layer(destination)}")
    print(f"  TO         : {destination}")
    print(f"  DATA       : {data}")
    print(f"  English: {english}")
    print(f"  Roman Urdu: {roman_urdu}")


def print_step(area: str, english: str, roman_urdu: str) -> None:
    """Print one action in easy English and Roman Urdu."""
    print(f"[{area}] {english}")
    print(f"  Roman Urdu: {roman_urdu}")


def print_error(area: str, english: str, roman_urdu: str) -> None:
    """Print one error in easy English and Roman Urdu."""
    print(f"[{area} ERROR] {english}")
    print(f"  Roman Urdu: {roman_urdu}")

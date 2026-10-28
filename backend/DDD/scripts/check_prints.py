"""Check that Python print statements do not contain emoji characters."""

from pathlib import Path
import re

EMOJI_PATTERN = re.compile("[\U0001F300-\U0001FAFF]")


def find_emoji_prints(project_directory: Path) -> list[str]:
    """Return print lines that still contain emojis."""
    matches = []
    project_files = [
        project_directory / "main.py",
        project_directory / "scripts" / "clear_firebase.py",
        *list((project_directory / "src").rglob("*.py")),
    ]

    # English: Check project code only, not installed venv packages.
    # Roman Urdu: Sirf project code check karo, venv packages nahi.
    for path in project_files:
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if "print(" in line and EMOJI_PATTERN.search(line):
                matches.append(f"{path}:{line_number}: {line.strip()}")

    return matches


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[1]
    problems = find_emoji_prints(project)

    if problems:
        print(
            "Emoji print statements found. "
            "Roman Urdu: Emoji walay print statements milay."
        )
        for problem in problems:
            print(problem)
        raise SystemExit(1)

    print(
        "Print check passed. "
        "Roman Urdu: Print statements ka check pass ho gaya."
    )

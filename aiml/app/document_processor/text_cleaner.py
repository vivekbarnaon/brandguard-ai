"""Conservative text cleanup for extracted brand guideline content."""

import re


def clean_text(text: str) -> str:
    """Normalize whitespace without removing meaningful paragraph boundaries."""
    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in normalized.split("\n")]

    cleaned_lines = []
    previous_blank = False
    for line in lines:
        if line:
            cleaned_lines.append(line)
            previous_blank = False
        elif not previous_blank and cleaned_lines:
            cleaned_lines.append("")
            previous_blank = True

    return "\n".join(cleaned_lines).strip()

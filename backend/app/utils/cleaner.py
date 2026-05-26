import re

FILLERS = {
    "um",
    "uh",
    "erm",
    "ah",
    "like",
    "you know",
}


def clean_transcript(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    normalized = re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", normalized, flags=re.I)
    for filler in FILLERS:
        normalized = re.sub(rf"\b{re.escape(filler)}\b[, ]*", "", normalized, flags=re.I)
    return re.sub(r"\s+", " ", normalized).strip()
